"""
Tests para audio_analyzer.py

Tests específicos para:
- Clase SongFeatures
- Clase AudioAnalyzer
- Extracción de features de audio
- Conversión a DataFrame
"""

import unittest
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Añadir directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from test.helpers import (
    create_test_song_dataframe,
    TemporaryMusicFolder,
    assert_valid_bpm,
    assert_valid_energy,
    assert_valid_duration,
    skip_if_no_librosa,
    SuppressOutput
)


class TestSongFeatures(unittest.TestCase):
    """Tests para la dataclass SongFeatures"""
    
    def test_creation(self):
        """Test: Crear SongFeatures con todos los parámetros"""
        from audio_analyzer import SongFeatures
        
        song = SongFeatures(
            filename="test.mp3",
            title="Test Song",
            duration=180.0,
            bpm=120.0,
            beat_strength=0.8,
            energy=0.7,
            energy_variance=0.1,
            brightness=0.5,
            contrast=15.0,
            dynamic_range=0.3,
            onset_rate=2.5
        )
        
        self.assertEqual(song.filename, "test.mp3")
        self.assertEqual(song.title, "Test Song")
        self.assertEqual(song.bpm, 120.0)
        self.assertEqual(song.workout_score, 0.0)  # Default
    
    def test_default_workout_score(self):
        """Test: workout_score tiene valor por defecto"""
        from audio_analyzer import SongFeatures
        
        song = SongFeatures(
            filename="test.mp3", title="Test", duration=180.0,
            bpm=120.0, beat_strength=0.8, energy=0.7,
            energy_variance=0.1, brightness=0.5, contrast=15.0,
            dynamic_range=0.3, onset_rate=2.5
        )
        
        self.assertEqual(song.workout_score, 0.0)
    
    def test_valid_ranges(self):
        """Test: Features están en rangos válidos"""
        from audio_analyzer import SongFeatures
        
        song = SongFeatures(
            filename="test.mp3", title="Test", duration=180.0,
            bpm=120.0, beat_strength=0.8, energy=0.7,
            energy_variance=0.1, brightness=0.5, contrast=15.0,
            dynamic_range=0.3, onset_rate=2.5
        )
        
        assert_valid_bpm(song.bpm)
        assert_valid_energy(song.energy)
        assert_valid_duration(song.duration)


class TestAudioAnalyzer(unittest.TestCase):
    """Tests para la clase AudioAnalyzer"""
    
    def test_creation(self):
        """Test: Crear instancia de AudioAnalyzer"""
        from audio_analyzer import AudioAnalyzer
        
        with TemporaryMusicFolder() as folder:
            analyzer = AudioAnalyzer(str(folder))
            
            self.assertIsNotNone(analyzer)
            self.assertEqual(analyzer.music_folder, folder)
            self.assertEqual(len(analyzer.songs), 0)
    
    def test_music_folder_as_path(self):
        """Test: music_folder se convierte a Path"""
        from audio_analyzer import AudioAnalyzer
        
        analyzer = AudioAnalyzer("/tmp/music")
        self.assertIsInstance(analyzer.music_folder, Path)
    
    @skip_if_no_librosa()
    def test_analyze_song_with_synthetic_audio(self):
        """Test: Analizar archivo de audio sintético"""
        from audio_analyzer import AudioAnalyzer
        
        with TemporaryMusicFolder(n_songs=1) as folder:
            analyzer = AudioAnalyzer(str(folder))
            audio_files = list(folder.glob("*.wav"))
            
            if len(audio_files) > 0:
                with SuppressOutput():
                    features = analyzer.analyze_song(audio_files[0])
                
                self.assertIsNotNone(features)
                # BPM puede ser 0 con audio sintético simple, pero debe existir
                self.assertGreaterEqual(features.bpm, 0)
                self.assertGreater(features.duration, 0)
                self.assertGreaterEqual(features.energy, 0)
    
    def test_to_dataframe_empty(self):
        """Test: to_dataframe con lista vacía"""
        from audio_analyzer import AudioAnalyzer
        
        analyzer = AudioAnalyzer("/tmp/music")
        df = analyzer.to_dataframe()
        
        self.assertEqual(len(df), 0)
    
    def test_to_dataframe_with_songs(self):
        """Test: to_dataframe con canciones"""
        from audio_analyzer import AudioAnalyzer, SongFeatures
        
        analyzer = AudioAnalyzer("/tmp/music")
        analyzer.songs = [
            SongFeatures(
                filename="song1.mp3", title="Song 1", duration=180.0,
                bpm=120.0, beat_strength=0.8, energy=0.7,
                energy_variance=0.1, brightness=0.5, contrast=15.0,
                dynamic_range=0.3, onset_rate=2.5
            ),
            SongFeatures(
                filename="song2.mp3", title="Song 2", duration=200.0,
                bpm=140.0, beat_strength=0.9, energy=0.8,
                energy_variance=0.15, brightness=0.6, contrast=18.0,
                dynamic_range=0.4, onset_rate=3.0
            )
        ]
        
        df = analyzer.to_dataframe()
        
        self.assertEqual(len(df), 2)
        self.assertIn('filename', df.columns)
        self.assertIn('bpm', df.columns)
        self.assertEqual(df.iloc[0]['bpm'], 120.0)
        self.assertEqual(df.iloc[1]['bpm'], 140.0)
    
    def test_dataframe_columns(self):
        """Test: DataFrame tiene todas las columnas necesarias"""
        from audio_analyzer import AudioAnalyzer, SongFeatures
        
        analyzer = AudioAnalyzer("/tmp/music")
        analyzer.songs = [
            SongFeatures(
                filename="test.mp3", title="Test", duration=180.0,
                bpm=120.0, beat_strength=0.8, energy=0.7,
                energy_variance=0.1, brightness=0.5, contrast=15.0,
                dynamic_range=0.3, onset_rate=2.5
            )
        ]
        
        df = analyzer.to_dataframe()
        
        expected_columns = [
            'filename', 'title', 'duration', 'bpm', 'beat_strength',
            'energy', 'energy_variance', 'brightness', 'contrast',
            'dynamic_range', 'onset_rate'
        ]
        
        for col in expected_columns:
            self.assertIn(col, df.columns)


if __name__ == '__main__':
    unittest.main()
