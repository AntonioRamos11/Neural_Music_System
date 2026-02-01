"""
Tests de integración - Pipeline completo

Tests que verifican el flujo completo del sistema:
- Análisis → Generación → Export
"""

import unittest
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from test.helpers import (
    TemporaryMusicFolder,
    assert_playlist_structure,
    skip_if_no_librosa,
    SuppressOutput
)


class TestFullPipeline(unittest.TestCase):
    """Tests del pipeline completo del sistema"""
    
    @skip_if_no_librosa()
    def test_analyze_to_playlist_pipeline(self):
        """Test: Pipeline completo de análisis a playlist"""
        from audio_analyzer import AudioAnalyzer
        from playlist_generator import CyclingPlaylistGenerator
        
        with TemporaryMusicFolder(n_songs=5) as folder:
            # Paso 1: Análisis
            analyzer = AudioAnalyzer(str(folder))
            
            with SuppressOutput():
                songs_df = analyzer.analyze_folder()
            
            self.assertGreater(len(songs_df), 0, "No se analizaron canciones")
            
            # Paso 2: Generación
            generator = CyclingPlaylistGenerator(songs_df)
            playlist = generator.generate_workout_playlist(
                duration_minutes=10,
                workout_type="endurance"
            )
            
            self.assertGreater(len(playlist), 0, "No se generó playlist")
            assert_playlist_structure(playlist)
            
            # Verificar que las canciones en la playlist existen en el análisis
            for filename in playlist['filename']:
                self.assertIn(filename, songs_df['filename'].values)
    
    def test_dataframe_to_csv_roundtrip(self):
        """Test: Guardar y cargar CSV"""
        from audio_analyzer import AudioAnalyzer, SongFeatures
        import tempfile
        
        # Crear datos de prueba
        analyzer = AudioAnalyzer("/tmp/music")
        analyzer.songs = [
            SongFeatures(
                filename="test.mp3", title="Test", duration=180.0,
                bpm=120.0, beat_strength=0.8, energy=0.7,
                energy_variance=0.1, brightness=0.5, contrast=15.0,
                dynamic_range=0.3, onset_rate=2.5
            )
        ]
        
        df1 = analyzer.to_dataframe()
        
        # Guardar y cargar
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_path = f.name
        
        df1.to_csv(csv_path, index=False)
        df2 = pd.read_csv(csv_path)
        
        # Verificar
        pd.testing.assert_frame_equal(df1, df2)
        
        # Cleanup
        Path(csv_path).unlink()
    
    def test_multiple_workout_types(self):
        """Test: Generar múltiples tipos de workout"""
        from playlist_generator import CyclingPlaylistGenerator
        from test.helpers import create_test_song_dataframe
        
        songs_df = create_test_song_dataframe(n_songs=20)
        generator = CyclingPlaylistGenerator(songs_df)
        
        workout_types = ["endurance", "intervals", "recovery"]
        
        for workout_type in workout_types:
            with self.subTest(workout_type=workout_type):
                playlist = generator.generate_workout_playlist(
                    duration_minutes=20,
                    workout_type=workout_type
                )
                
                self.assertGreater(len(playlist), 0)
                assert_playlist_structure(playlist)


if __name__ == '__main__':
    unittest.main()
