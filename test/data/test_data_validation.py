"""
Tests de validación de datos

Tests para verificar:
- Rangos válidos de features
- Tipos de datos correctos
- No hay valores NaN
- Consistencia de datos
"""

import unittest
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from test.helpers import create_test_song_dataframe, create_test_playlist


class TestDataRanges(unittest.TestCase):
    """Tests para validar rangos de datos"""
    
    def test_bpm_range(self):
        """Test: BPM está en rango razonable (40-200)"""
        df = create_test_song_dataframe(n_songs=50)
        
        self.assertTrue((df['bpm'] >= 40).all())
        self.assertTrue((df['bpm'] <= 200).all())
    
    def test_energy_normalized(self):
        """Test: Energía está normalizada (0-1)"""
        df = create_test_song_dataframe(n_songs=50)
        
        self.assertTrue((df['energy'] >= 0).all())
        self.assertTrue((df['energy'] <= 1.0).all())
    
    def test_duration_positive(self):
        """Test: Duración es positiva"""
        df = create_test_song_dataframe(n_songs=50)
        
        self.assertTrue((df['duration'] > 0).all())
    
    def test_beat_strength_range(self):
        """Test: Beat strength entre 0 y 1"""
        df = create_test_song_dataframe(n_songs=50)
        
        self.assertTrue((df['beat_strength'] >= 0).all())
        self.assertTrue((df['beat_strength'] <= 1.0).all())
    
    def test_brightness_range(self):
        """Test: Brightness entre 0 y 1"""
        df = create_test_song_dataframe(n_songs=50)
        
        self.assertTrue((df['brightness'] >= 0).all())
        self.assertTrue((df['brightness'] <= 1.0).all())



class TestDataTypes(unittest.TestCase):
    """Tests para validar tipos de datos"""
    
    def test_numeric_columns(self):
        """Test: Columnas numéricas tienen tipo correcto"""
        df = create_test_song_dataframe(n_songs=10)
        
        numeric_cols = ['duration', 'bpm', 'energy', 'beat_strength']
        
        for col in numeric_cols:
            self.assertTrue(
                pd.api.types.is_numeric_dtype(df[col]),
                f"{col} no es numérico"
            )
    
    def test_string_columns(self):
        """Test: Columnas de texto tienen tipo correcto"""
        df = create_test_song_dataframe(n_songs=10)
        
        string_cols = ['filename', 'title']
        
        for col in string_cols:
            # pandas 2.0+ puede usar 'string' dtype o 'object'
            is_string_type = (
                df[col].dtype == object or 
                df[col].dtype.name == 'string' or
                pd.api.types.is_string_dtype(df[col])
            )
            self.assertTrue(
                is_string_type,
                f"{col} no es string/object, es {df[col].dtype}"
            )


class TestNoNaN(unittest.TestCase):
    """Tests para verificar ausencia de NaN"""
    
    def test_no_nan_in_songs(self):
        """Test: No hay NaN en DataFrame de canciones"""
        df = create_test_song_dataframe(n_songs=20)
        
        nan_count = df.isna().sum().sum()
        self.assertEqual(nan_count, 0, f"Hay {nan_count} valores NaN")
    
    def test_no_nan_in_playlist(self):
        """Test: No hay NaN en playlist"""
        df = create_test_playlist(n_songs=10)
        
        nan_count = df.isna().sum().sum()
        self.assertEqual(nan_count, 0, f"Hay {nan_count} valores NaN")


class TestDataConsistency(unittest.TestCase):
    """Tests para verificar consistencia de datos"""
    
    def test_unique_filenames(self):
        """Test: Nombres de archivo son únicos en canciones"""
        df = create_test_song_dataframe(n_songs=20)
        
        unique_count = df['filename'].nunique()
        total_count = len(df)
        
        self.assertEqual(unique_count, total_count)
    
    def test_cumulative_time_increasing(self):
        """Test: Tiempo acumulado es siempre creciente"""
        df = create_test_playlist(n_songs=10)
        
        if 'cumulative_time' in df.columns:
            diffs = df['cumulative_time'].diff()[1:]
            self.assertTrue((diffs > 0).all())
    
    def test_time_calculation_consistency(self):
        """Test: start_time + duration = cumulative_time"""
        df = create_test_playlist(n_songs=10)
        
        if all(col in df.columns for col in ['start_time', 'duration', 'cumulative_time']):
            calculated = df['start_time'] + df['duration']
            
            np.testing.assert_array_almost_equal(
                calculated.values,
                df['cumulative_time'].values,
                decimal=1
            )
    
    def test_valid_phases(self):
        """Test: Todas las fases son válidas"""
        df = create_test_playlist(n_songs=10)
        
        if 'phase' in df.columns:
            valid_phases = {'warmup', 'build', 'peak', 'sustain', 'cooldown'}
            actual_phases = set(df['phase'].unique())
            
            invalid = actual_phases - valid_phases
            self.assertEqual(len(invalid), 0, f"Fases inválidas: {invalid}")


class TestPlaylistStructure(unittest.TestCase):
    """Tests para verificar estructura de playlist"""
    
    def test_required_columns(self):
        """Test: Playlist tiene columnas requeridas"""
        df = create_test_playlist(n_songs=10)
        
        required = ['filename', 'title', 'duration', 'bpm', 'phase']
        missing = set(required) - set(df.columns)
        
        self.assertEqual(len(missing), 0, f"Faltan columnas: {missing}")
    
    def test_playlist_not_empty(self):
        """Test: Playlist no está vacía"""
        df = create_test_playlist(n_songs=10)
        
        self.assertGreater(len(df), 0)
    
    def test_first_phase_warmup(self):
        """Test: Primera fase es warmup"""
        df = create_test_playlist(n_songs=10)
        
        if 'phase' in df.columns and len(df) > 0:
            self.assertEqual(df.iloc[0]['phase'], 'warmup')
    
    def test_last_phase_cooldown(self):
        """Test: Última fase es cooldown"""
        df = create_test_playlist(n_songs=10)
        
        if 'phase' in df.columns and len(df) > 0:
            self.assertEqual(df.iloc[-1]['phase'], 'cooldown')


if __name__ == '__main__':
    unittest.main()
