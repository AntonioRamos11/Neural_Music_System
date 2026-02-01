"""
Helpers y utilidades compartidas para tests
"""

import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import shutil
from typing import Optional, List
import warnings
warnings.filterwarnings('ignore')


class TestColors:
    """Colores ANSI para output de tests"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def create_test_song_dataframe(n_songs: int = 20, seed: int = 42) -> pd.DataFrame:
    """
    Crea un DataFrame de prueba con canciones sintéticas
    
    Args:
        n_songs: Número de canciones a generar
        seed: Seed para reproducibilidad
    
    Returns:
        DataFrame con features de canciones
    """
    np.random.seed(seed)
    
    return pd.DataFrame({
        'filename': [f'song_{i:03d}.mp3' for i in range(n_songs)],
        'title': [f'Test Song {i}' for i in range(n_songs)],
        'duration': np.random.uniform(150, 250, n_songs),
        'bpm': np.random.uniform(80, 160, n_songs),
        'beat_strength': np.random.uniform(0.5, 1.0, n_songs),
        'energy': np.random.uniform(0.2, 0.9, n_songs),
        'energy_variance': np.random.uniform(0.05, 0.2, n_songs),
        'brightness': np.random.uniform(0.3, 0.8, n_songs),
        'contrast': np.random.uniform(10, 25, n_songs),
        'dynamic_range': np.random.uniform(0.1, 0.5, n_songs),
        'onset_rate': np.random.uniform(1.5, 4.0, n_songs)
    })


def create_test_playlist(n_songs: int = 10) -> pd.DataFrame:
    """
    Crea una playlist de prueba con estructura completa
    
    Args:
        n_songs: Número de canciones en la playlist
    
    Returns:
        DataFrame con playlist completa
    """
    phases = ['warmup', 'build', 'sustain', 'peak', 'cooldown']
    phase_distribution = [0, 1, 2, 2, 3, 3, 3, 2, 4, 4][:n_songs]
    
    durations = [180] * n_songs
    start_times = [sum(durations[:i]) for i in range(n_songs)]
    cumulative_times = [sum(durations[:i+1]) for i in range(n_songs)]
    
    return pd.DataFrame({
        'filename': [f'song_{i}.mp3' for i in range(n_songs)],
        'title': [f'Test Song {i}' for i in range(n_songs)],
        'duration': durations,
        'bpm': [90 + i*5 for i in range(n_songs)],
        'energy': [0.2 + i*0.08 for i in range(n_songs)],
        'intensity_score': [0.2 + i*0.08 for i in range(n_songs)],
        'phase': [phases[p] for p in phase_distribution],
        'start_time': start_times,
        'cumulative_time': cumulative_times
    })


def generate_synthetic_audio(
    filepath: Path,
    duration: float = 3.0,
    bpm: float = 120.0,
    energy: float = 0.7,
    sample_rate: int = 22050
) -> bool:
    """
    Genera un archivo de audio sintético para testing
    
    Args:
        filepath: Ruta donde guardar el archivo
        duration: Duración en segundos
        bpm: Tempo deseado
        energy: Nivel de energía (0-1)
        sample_rate: Sample rate del audio
    
    Returns:
        True si se generó correctamente, False si falta scipy
    """
    try:
        import scipy.io.wavfile as wav
    except ImportError:
        return False
    
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples)
    
    # Frecuencia base proporcional al BPM
    freq_base = bpm / 60 * 2  # Hz
    
    # Señal con múltiples armónicos
    signal = np.zeros(n_samples)
    for harmonic in [1, 2, 3, 4]:
        amplitude = energy / harmonic
        signal += amplitude * np.sin(2 * np.pi * freq_base * harmonic * t)
    
    # Añadir variación temporal
    envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 0.1 * t)
    signal *= envelope
    
    # Normalizar y convertir a int16
    signal = signal / np.max(np.abs(signal)) * energy
    signal = (signal * 32767 * 0.8).astype(np.int16)
    
    # Guardar
    wav.write(str(filepath), sample_rate, signal)
    return True


class TemporaryMusicFolder:
    """Context manager para crear carpeta temporal con archivos de audio"""
    
    def __init__(self, n_songs: int = 5):
        self.n_songs = n_songs
        self.temp_dir = None
        self.music_folder = None
    
    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.music_folder = Path(self.temp_dir) / "music"
        self.music_folder.mkdir()
        
        # Generar archivos
        configs = [
            (85, 0.3),   # Baja energía, bajo BPM
            (100, 0.5),  # Media energía, medio BPM
            (120, 0.7),  # Alta energía, alto BPM
            (140, 0.8),  # Muy alta energía
            (160, 0.9),  # Máxima energía
        ]
        
        for i in range(min(self.n_songs, len(configs))):
            bpm, energy = configs[i]
            filepath = self.music_folder / f"test_{i:02d}_{bpm}bpm.wav"
            generate_synthetic_audio(filepath, bpm=bpm, energy=energy)
        
        return self.music_folder
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir:
            shutil.rmtree(self.temp_dir)


def assert_valid_bpm(bpm: float, min_bpm: float = 40, max_bpm: float = 200):
    """Valida que el BPM esté en un rango razonable"""
    assert min_bpm <= bpm <= max_bpm, f"BPM {bpm} fuera de rango [{min_bpm}, {max_bpm}]"


def assert_valid_energy(energy: float):
    """Valida que la energía esté normalizada"""
    assert 0 <= energy <= 1.1, f"Energía {energy} fuera de rango [0, 1]"


def assert_valid_duration(duration: float):
    """Valida que la duración sea positiva"""
    assert duration > 0, f"Duración {duration} debe ser positiva"


def assert_valid_phase(phase: str):
    """Valida que la fase sea válida"""
    valid_phases = {'warmup', 'build', 'peak', 'sustain', 'cooldown'}
    assert phase in valid_phases, f"Fase '{phase}' no válida. Debe ser una de {valid_phases}"


def assert_playlist_structure(playlist: pd.DataFrame):
    """Valida la estructura básica de una playlist"""
    required_columns = ['filename', 'title', 'duration', 'bpm', 'phase']
    missing = set(required_columns) - set(playlist.columns)
    assert len(missing) == 0, f"Faltan columnas requeridas: {missing}"
    
    assert len(playlist) > 0, "Playlist vacía"
    assert playlist['filename'].nunique() == len(playlist), "Archivos duplicados en playlist"


def assert_time_progression(playlist: pd.DataFrame):
    """Valida que el tiempo progrese correctamente"""
    if 'cumulative_time' in playlist.columns:
        diffs = playlist['cumulative_time'].diff()[1:]
        assert (diffs > 0).all(), "El tiempo acumulado debe ser siempre creciente"
    
    if 'start_time' in playlist.columns and 'duration' in playlist.columns:
        calculated = playlist['start_time'] + playlist['duration']
        if 'cumulative_time' in playlist.columns:
            np.testing.assert_array_almost_equal(
                calculated.values,
                playlist['cumulative_time'].values,
                decimal=1,
                err_msg="start_time + duration != cumulative_time"
            )


def skip_if_no_librosa():
    """Decorator para saltear tests que requieren librosa"""
    import unittest
    try:
        import librosa
        return lambda func: func
    except ImportError:
        return unittest.skip("librosa no instalado")


def skip_if_no_scipy():
    """Decorator para saltear tests que requieren scipy"""
    import unittest
    try:
        import scipy
        return lambda func: func
    except ImportError:
        return unittest.skip("scipy no instalado")


def skip_if_no_matplotlib():
    """Decorator para saltear tests que requieren matplotlib"""
    import unittest
    try:
        import matplotlib
        return lambda func: func
    except ImportError:
        return unittest.skip("matplotlib no instalado")


class SuppressOutput:
    """Context manager para suprimir output durante tests"""
    
    def __enter__(self):
        import sys
        import os
        self.devnull = open(os.devnull, 'w')
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        sys.stdout = self.devnull
        sys.stderr = self.devnull
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import sys
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        self.devnull.close()
