"""
Audio Analyzer - Sistema de análisis de características musicales

Arquitectura:
- SongFeatures: Modelo de datos inmutable con características extraídas
- CacheManager: Responsable de persistencia de caché (SRP)
- AudioFeatureExtractor: Extracción de características de audio (SRP)
- AudioAnalyzer: Orquestador principal con procesamiento paralelo

Principios:
- Separación de responsabilidades
- Código modular y testeable
- Manejo explícito de errores
- Caché transparente para rendimiento
"""

import librosa
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
import warnings
import json
import hashlib
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import sys
import os
from contextlib import contextmanager

warnings.filterwarnings('ignore')


@contextmanager
def suppress_stderr():
    """Context manager para suprimir mensajes de error de stderr (libmpg123, etc.)"""
    stderr_fd = sys.stderr.fileno()
    with open(os.devnull, 'w') as devnull:
        old_stderr = os.dup(stderr_fd)
        os.dup2(devnull.fileno(), stderr_fd)
        try:
            yield
        finally:
            os.dup2(old_stderr, stderr_fd)
            os.close(old_stderr)

# ============================================================================
# MODELOS DE DATOS
# ============================================================================

@dataclass
class SongFeatures:
    """
    Modelo inmutable de características extraídas de una canción.
    
    Attributes:
        filename: Nombre del archivo de audio
        filepath: Ruta completa al archivo (para M3U)
        title: Título limpio extraído del nombre
        duration: Duración en segundos
        bpm: Beats por minuto
        beat_strength: Claridad del ritmo (0-1)
        energy: Energía promedio RMS normalizada (0-1)
        energy_variance: Variación en la energía
        brightness: Centroid espectral (frecuencias altas = brillante)
        contrast: Contraste espectral
        dynamic_range: Diferencia entre partes fuertes y suaves
        onset_rate: Golpes/ataques por segundo
        workout_score: Puntuación para ejercicio (calculada después)
    """
    filename: str
    filepath: str
    title: str
    duration: float
    
    # Características de ritmo
    bpm: float
    beat_strength: float
    
    # Características de energía
    energy: float
    energy_variance: float
    
    # Características espectrales
    brightness: float
    contrast: float
    
    # Características dinámicas
    dynamic_range: float
    onset_rate: float
    
    # Métricas derivadas
    workout_score: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario para serialización"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SongFeatures':
        """Crea instancia desde diccionario"""
        return cls(**data)


# ============================================================================
# GESTOR DE CACHÉ
# ============================================================================

class CacheManager:
    """
    Gestiona la persistencia de análisis previos.
    
    Responsabilidades:
    - Cargar/guardar caché en formato JSON
    - Generar hashes únicos por archivo
    - Validar integridad de caché
    """
    
    def __init__(self, cache_file: Path):
        """
        Args:
            cache_file: Ruta al archivo de caché JSON
        """
        self.cache_file = cache_file
        self._cache: Dict[str, Dict] = {}
    
    def load(self) -> None:
        """Carga el caché desde disco"""
        if not self.cache_file.exists():
            self._cache = {}
            return
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self._cache = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Error al cargar caché: {e}")
            self._cache = {}
    
    def save(self) -> None:
        """Guarda el caché a disco"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"⚠️  Error al guardar caché: {e}")
    
    def get_file_hash(self, filepath: Path) -> str:
        """
        Genera hash único basado en archivo.
        
        Usa nombre + tamaño + timestamp de modificación para detectar cambios.
        
        Args:
            filepath: Ruta al archivo
            
        Returns:
            Hash MD5 del archivo
        """
        try:
            stat = filepath.stat()
            content = f"{filepath.name}_{stat.st_size}_{stat.st_mtime}"
            return hashlib.md5(content.encode()).hexdigest()
        except OSError:
            # Si falla, usar solo el nombre
            return hashlib.md5(filepath.name.encode()).hexdigest()
    
    def get(self, filepath: Path) -> Optional[SongFeatures]:
        """
        Obtiene análisis desde caché si existe.
        
        Args:
            filepath: Ruta al archivo de audio
            
        Returns:
            SongFeatures si está en caché, None si no
        """
        file_hash = self.get_file_hash(filepath)
        if file_hash in self._cache:
            return SongFeatures.from_dict(self._cache[file_hash])
        return None
    
    def put(self, filepath: Path, features: SongFeatures) -> None:
        """
        Agrega análisis al caché.
        
        Args:
            filepath: Ruta al archivo de audio
            features: Características extraídas
        """
        file_hash = self.get_file_hash(filepath)
        self._cache[file_hash] = features.to_dict()
    
    def size(self) -> int:
        """Retorna cantidad de entradas en caché"""
        return len(self._cache)


# ============================================================================
# EXTRACTOR DE CARACTERÍSTICAS
# ============================================================================

class AudioFeatureExtractor:
    """
    Extrae características de audio usando librosa.
    
    Responsabilidades:
    - Cargar archivo de audio
    - Extraer características de ritmo, energía, espectro y dinámica
    - Normalizar valores a rangos estándar
    - Manejo robusto de errores
    """
    
    SAMPLE_RATE = 22050  # Hz - balance entre calidad y velocidad
    
    @classmethod
    def extract(cls, filepath: Path) -> Optional[SongFeatures]:
        """
        Extrae todas las características de un archivo de audio.
        
        Args:
            filepath: Ruta al archivo de audio
            
        Returns:
            SongFeatures si exitoso, None si falla
        """
        try:
            # Cargar audio (stderr ya suprimido en worker)
            y, sr = librosa.load(filepath, sr=cls.SAMPLE_RATE, mono=True)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Extraer características por categoría
            rhythm_features = cls._extract_rhythm_features(y, sr)
            energy_features = cls._extract_energy_features(y)
            spectral_features = cls._extract_spectral_features(y, sr)
            dynamic_features = cls._extract_dynamic_features(y, duration)
            
            # Generar título limpio
            title = cls._clean_title(filepath.stem)
            
            return SongFeatures(
                filename=filepath.name,
                filepath=str(filepath.resolve()),  # Ruta completa absoluta
                title=title,
                duration=duration,
                **rhythm_features,
                **energy_features,
                **spectral_features,
                **dynamic_features
            )
            
        except Exception as e:
            print(f"  ❌ Error en {filepath.name}: {e}")
            return None
    
    @staticmethod
    def _extract_rhythm_features(y: np.ndarray, sr: int) -> Dict:
        """Extrae características de ritmo (BPM, beat strength)"""
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        tempo = float(tempo) if not hasattr(tempo, '__len__') else float(tempo[0])
        
        # Fuerza del beat (qué tan marcado es el ritmo)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        beat_strength = float(np.mean(onset_env[beats]) / (np.max(onset_env) + 1e-6))
        
        return {
            'bpm': tempo,
            'beat_strength': beat_strength
        }
    
    @staticmethod
    def _extract_energy_features(y: np.ndarray) -> Dict:
        """Extrae características de energía (RMS, varianza)"""
        rms = librosa.feature.rms(y=y)[0]
        energy = float(np.mean(rms))
        energy_variance = float(np.std(rms))
        
        # Normalizar energía a rango 0-1
        energy = min(1.0, energy * 5)
        
        return {
            'energy': energy,
            'energy_variance': energy_variance
        }
    
    @staticmethod
    def _extract_spectral_features(y: np.ndarray, sr: int) -> Dict:
        """Extrae características espectrales (brightness, contrast)"""
        # Centroid espectral (frecuencias dominantes)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        brightness = float(np.mean(spectral_centroid) / (sr / 2))
        
        # Contraste espectral
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        contrast = float(np.mean(spectral_contrast))
        
        return {
            'brightness': brightness,
            'contrast': contrast
        }
    
    @staticmethod
    def _extract_dynamic_features(y: np.ndarray, duration: float) -> Dict:
        """Extrae características dinámicas (rango, onset rate)"""
        rms = librosa.feature.rms(y=y)[0]
        dynamic_range = float(np.max(rms) - np.min(rms))
        
        # Tasa de onsets (golpes/ataques por segundo)
        onsets = librosa.onset.onset_detect(y=y, sr=AudioFeatureExtractor.SAMPLE_RATE)
        onset_rate = len(onsets) / duration if duration > 0 else 0.0
        
        return {
            'dynamic_range': dynamic_range,
            'onset_rate': onset_rate
        }
    
    @staticmethod
    def _clean_title(filename_stem: str) -> str:
        """Limpia el nombre del archivo para título legible"""
        return filename_stem.replace('_', ' ').replace('-', ' ').strip()


# ============================================================================
# WORKER PARA PROCESAMIENTO PARALELO
# ============================================================================

def _analyze_song_worker(filepath: Path) -> Optional[SongFeatures]:
    """
    Worker function para procesamiento paralelo.
    
    Debe estar a nivel de módulo para ser pickle-able por multiprocessing.
    
    Args:
        filepath: Ruta al archivo de audio
        
    Returns:
        SongFeatures si exitoso, None si falla
    """
    try:
        # Timeout de 30 segundos por canción
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Timeout analizando {filepath.name}")
        
        # Solo en sistemas Unix
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
        
        try:
            # Suprimir stderr en cada proceso hijo (libmpg123 warnings)
            with suppress_stderr():
                result = AudioFeatureExtractor.extract(filepath)
            
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)  # Cancelar alarma
            
            return result
            
        except TimeoutError:
            print(f"\n  ⏱️  Timeout: {filepath.name} (>30s)")
            return None
            
    except Exception as e:
        # Capturar cualquier error para que no trabe el pool
        print(f"\n  ⚠️  Error procesando {filepath.name}: {str(e)[:50]}")
        return None


# ============================================================================
# ANALIZADOR PRINCIPAL
# ============================================================================

class AudioAnalyzer:
    """
    Orquestador principal del análisis de audio.
    
    Responsabilidades:
    - Buscar archivos de audio en carpeta
    - Coordinar caché y extracción de características
    - Procesamiento paralelo con barra de progreso
    - Conversión a DataFrame para análisis
    
    Uso:
        analyzer = AudioAnalyzer("mis_canciones")
        df = analyzer.analyze_folder()  # Con caché y paralelo
    """
    
    AUDIO_EXTENSIONS = [
        "mp3", "MP3", "wav", "WAV", "flac", "FLAC",
        "m4a", "M4A", "aac", "AAC", "ogg", "OGG"
    ]
    
    def __init__(
        self,
        music_folder: str,
        cache_file: str = "csv/audio_cache.json",
        use_cache: bool = True
    ):
        """
        Args:
            music_folder: Ruta a carpeta con archivos de audio
            cache_file: Ruta al archivo de caché JSON
            use_cache: Si True, usa caché para evitar re-análisis
        """
        self.music_folder = Path(music_folder)
        self.cache_manager = CacheManager(Path(cache_file)) if use_cache else None
        self.songs: List[SongFeatures] = []
        
        if self.cache_manager:
            self.cache_manager.load()
    
    def analyze_folder(
        self,
        n_jobs: Optional[int] = None,
        use_parallel: bool = True
    ) -> pd.DataFrame:
        """
        Analiza todos los archivos de audio en la carpeta.
        
        Args:
            n_jobs: Número de procesos paralelos (None = usa todos los cores - 1)
            use_parallel: Si False, procesa secuencialmente (útil para debugging)
            
        Returns:
            DataFrame con características de todas las canciones
        """
        print(f"🔍 Buscando archivos de audio en: {self.music_folder}")
        print("   (búsqueda recursiva en todas las subcarpetas)")
        
        # Buscar archivos de audio
        audio_files = self._find_audio_files()
        
        if not audio_files:
            print("⚠️  No se encontraron archivos de audio")
            return pd.DataFrame()
        
        print(f"📁 Encontrados: {len(audio_files)} archivos")
        
        # Mostrar distribución por subcarpetas (si hay)
        folders = {}
        for file in audio_files:
            folder = file.parent.relative_to(self.music_folder) if file.parent != self.music_folder else Path(".")
            folders[str(folder)] = folders.get(str(folder), 0) + 1
        
        if len(folders) > 1:
            print(f"   Distribuidos en {len(folders)} carpetas:")
            for folder, count in sorted(folders.items())[:5]:  # Mostrar primeras 5
                folder_display = "raíz" if folder == "." else folder
                print(f"   - {folder_display}: {count} archivos")
            if len(folders) > 5:
                print(f"   - ... y {len(folders) - 5} carpetas más")
        
        # Separar archivos en caché vs nuevos
        files_to_analyze, cached_count = self._load_from_cache(audio_files)
        
        if cached_count > 0:
            print(f"💾 Cargadas desde caché: {cached_count} canciones")
        
        if not files_to_analyze:
            print("✅ Todas las canciones ya estaban en caché")
            return self.to_dataframe()
        
        print(f"🎵 Analizando: {len(files_to_analyze)} canciones nuevas")
        
        # Analizar archivos nuevos
        if use_parallel and len(files_to_analyze) > 1:
            self._analyze_parallel(files_to_analyze, n_jobs)
        else:
            self._analyze_sequential(files_to_analyze)
        
        # Contar cuántas se analizaron exitosamente
        new_songs = len(self.songs) - cached_count
        
        # Contar cuántas se analizaron exitosamente
        new_songs = len(self.songs) - cached_count
        failed_songs = len(files_to_analyze) - new_songs
        
        # Guardar caché actualizado
        if self.cache_manager and files_to_analyze:
            self.cache_manager.save()
            print(f"💾 Caché actualizado: {self.cache_manager.cache_file}")
        
        print(f"\n✅ Total analizadas: {len(self.songs)} canciones")
        if failed_songs > 0:
            print(f"⚠️  {failed_songs} archivos no se pudieron analizar (corruptos o formato no soportado)")
        
        return self.to_dataframe()
    
    def analyze_song(self, filepath: Path) -> Optional[SongFeatures]:
        """
        Analiza un solo archivo de audio.
        
        Args:
            filepath: Ruta al archivo de audio
            
        Returns:
            SongFeatures si exitoso, None si falla
        """
        # Intentar obtener desde caché
        if self.cache_manager:
            cached = self.cache_manager.get(filepath)
            if cached:
                return cached
        
        # Analizar archivo
        features = AudioFeatureExtractor.extract(filepath)
        
        # Guardar en caché
        if features and self.cache_manager:
            self.cache_manager.put(filepath, features)
        
        return features
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convierte las canciones analizadas a DataFrame.
        
        Returns:
            DataFrame con una fila por canción
        """
        if not self.songs:
            return pd.DataFrame()
        
        data = [song.to_dict() for song in self.songs]
        return pd.DataFrame(data)
    
    # ========================================================================
    # MÉTODOS PRIVADOS
    # ========================================================================
    
    def _find_audio_files(self) -> List[Path]:
        """Busca todos los archivos de audio soportados (recursivamente en subcarpetas)"""
        audio_files = []
        for ext in self.AUDIO_EXTENSIONS:
            # Usar rglob para búsqueda recursiva en todas las subcarpetas
            audio_files.extend(self.music_folder.rglob(f"*.{ext}"))
        return sorted(audio_files)
    
    def _load_from_cache(self, audio_files: List[Path]) -> tuple[List[Path], int]:
        """
        Carga canciones desde caché y retorna archivos pendientes.
        
        Returns:
            Tupla (archivos_pendientes, cantidad_desde_cache)
        """
        if not self.cache_manager:
            return audio_files, 0
        
        files_to_analyze = []
        cached_count = 0
        
        for filepath in audio_files:
            cached = self.cache_manager.get(filepath)
            if cached:
                self.songs.append(cached)
                cached_count += 1
            else:
                files_to_analyze.append(filepath)
        
        return files_to_analyze, cached_count
    
    def _analyze_parallel(self, files: List[Path], n_jobs: Optional[int]) -> None:
        """Analiza archivos en paralelo con barra de progreso"""
        if n_jobs is None:
            # Limitar a 8 procesos máximo para evitar problemas de memoria
            n_jobs = min(8, max(1, cpu_count() - 1))
        
        print(f"⚡ Usando {n_jobs} procesos paralelos\n")
        
        try:
            with Pool(processes=n_jobs) as pool:
                # imap_unordered es más rápido y menos propenso a bloqueos
                results = []
                for result in tqdm(
                    pool.imap_unordered(_analyze_song_worker, files, chunksize=1),
                    total=len(files),
                    desc="Analizando",
                    unit="canción"
                ):
                    results.append(result)
                
                # Forzar cierre del pool
                pool.close()
                pool.join()
        except KeyboardInterrupt:
            print("\n⚠️  Análisis interrumpido por el usuario")
            pool.terminate()
            pool.join()
            raise
        except Exception as e:
            print(f"\n⚠️  Error en procesamiento paralelo: {e}")
            pool.terminate()
            pool.join()
            results = []
        
        # Agregar resultados exitosos (mantener orden con zip original)
        for features in results:
            if features:
                self.songs.append(features)
                # Buscar filepath correspondiente para caché
                for filepath in files:
                    if features.filename == filepath.name:
                        if self.cache_manager:
                            self.cache_manager.put(filepath, features)
                        break
    
    def _analyze_sequential(self, files: List[Path]) -> None:
        """Analiza archivos secuencialmente (para debugging)"""
        print("📝 Modo secuencial\n")
        
        for filepath in tqdm(files, desc="Analizando", unit="canción"):
            # Suprimir stderr también en modo secuencial
            with suppress_stderr():
                features = AudioFeatureExtractor.extract(filepath)
            if features:
                self.songs.append(features)
                if self.cache_manager:
                    self.cache_manager.put(filepath, features)
