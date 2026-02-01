# audio_analyzer.py
import librosa
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import warnings
warnings.filterwarnings('ignore')

@dataclass
class SongFeatures:
    """Features extraídas de cada canción"""
    filename: str
    title: str
    duration: float          # segundos
    
    # Ritmo
    bpm: float               # Beats por minuto
    beat_strength: float     # Qué tan marcado es el beat (0-1)
    
    # Energía
    energy: float            # RMS energy promedio (0-1)
    energy_variance: float   # Variación de energía
    
    # Espectro
    brightness: float        # Spectral centroid (frecuencias altas = más brillante)
    contrast: float          # Spectral contrast
    
    # Dinámica
    dynamic_range: float     # Diferencia entre partes fuertes y suaves
    onset_rate: float        # Cantidad de "golpes" por segundo
    
    # Para ciclismo
    workout_score: float = 0.0  # Calculado después

class AudioAnalyzer:
    def __init__(self, music_folder: str):
        self.music_folder = Path(music_folder)
        self.songs: List[SongFeatures] = []
        
    def analyze_song(self, filepath: Path) -> Optional[SongFeatures]:
        """Analiza un archivo MP3 y extrae features"""
        try:
            print(f"  Analizando: {filepath.name}...")
            
            # Carga audio (sr=None mantiene sample rate original)
            y, sr = librosa.load(filepath, sr=22050, mono=True)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # === RITMO ===
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            tempo = float(tempo) if not hasattr(tempo, '__len__') else float(tempo[0])
            
            # Beat strength (qué tan claros son los beats)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            beat_strength = float(np.mean(onset_env[beats]) / (np.max(onset_env) + 1e-6))
            
            # === ENERGÍA ===
            rms = librosa.feature.rms(y=y)[0]
            energy = float(np.mean(rms))
            energy_variance = float(np.std(rms))
            
            # Normaliza energía a 0-1
            energy = min(1.0, energy * 5)
            
            # === ESPECTRO ===
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            brightness = float(np.mean(spectral_centroid) / (sr/2))  # Normalizado
            
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            contrast = float(np.mean(spectral_contrast))
            
            # === DINÁMICA ===
            dynamic_range = float(np.max(rms) - np.min(rms))
            
            # Onset rate (golpes por segundo)
            onsets = librosa.onset.onset_detect(y=y, sr=sr)
            onset_rate = len(onsets) / duration
            
            # Nombre limpio
            title = filepath.stem.replace('_', ' ').replace('-', ' ')
            
            return SongFeatures(
                filename=filepath.name,
                title=title,
                duration=duration,
                bpm=tempo,
                beat_strength=beat_strength,
                energy=energy,
                energy_variance=energy_variance,
                brightness=brightness,
                contrast=contrast,
                dynamic_range=dynamic_range,
                onset_rate=onset_rate
            )
            
        except Exception as e:
            print(f"  ❌ Error en {filepath.name}: {e}")
            return None
    
    def analyze_folder(self) -> pd.DataFrame:
        """Analiza todos los archivos de audio en la carpeta"""
        print(f"🔍 Buscando archivos de audio en: {self.music_folder}")
        
        # Buscar múltiples formatos de audio
        audio_files = []
        audio_files += list(self.music_folder.glob("*.mp3"))
        audio_files += list(self.music_folder.glob("*.MP3"))
        audio_files += list(self.music_folder.glob("*.wav"))
        audio_files += list(self.music_folder.glob("*.WAV"))
        audio_files += list(self.music_folder.glob("*.flac"))
        audio_files += list(self.music_folder.glob("*.FLAC"))
        audio_files += list(self.music_folder.glob("*.m4a"))
        audio_files += list(self.music_folder.glob("*.M4A"))
        audio_files += list(self.music_folder.glob("*.aac"))
        audio_files += list(self.music_folder.glob("*.AAC"))
        audio_files += list(self.music_folder.glob("*.ogg"))
        audio_files += list(self.music_folder.glob("*.OGG"))
        
        mp3_files = audio_files
        
        print(f"📁 Encontrados: {len(mp3_files)} archivos\n")
        
        for filepath in mp3_files:
            features = self.analyze_song(filepath)
            if features:
                self.songs.append(features)
        
        print(f"\n✅ Analizadas: {len(self.songs)} canciones")
        
        return self.to_dataframe()
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convierte a DataFrame para análisis"""
        data = []
        for song in self.songs:
            data.append({
                'filename': song.filename,
                'title': song.title,
                'duration': song.duration,
                'bpm': song.bpm,
                'beat_strength': song.beat_strength,
                'energy': song.energy,
                'energy_variance': song.energy_variance,
                'brightness': song.brightness,
                'contrast': song.contrast,
                'dynamic_range': song.dynamic_range,
                'onset_rate': song.onset_rate
            })
        return pd.DataFrame(data)
