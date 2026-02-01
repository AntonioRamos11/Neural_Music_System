"""
Tests para playlist_generator.py

Tests específicos para:
- Enum WorkoutPhase
- Clase CyclingPlaylistGenerator
- Generación de playlists por tipo
- Cálculo de scores
- Ordenamiento por cadencia
"""

import unittest
import sys
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from test.helpers import (
    create_test_song_dataframe,
    assert_valid_phase,
    assert_playlist_structure,
    assert_time_progression
)


class TestWorkoutPhase(unittest.TestCase):
    """Tests para el enum WorkoutPhase"""
    
    def test_all_phases_exist(self):
        """Test: Todas las fases definidas existen"""
        from playlist_generator import WorkoutPhase
        
        expected_phases = ['warmup', 'build', 'peak', 'sustain', 'cooldown']
        actual_phases = [p.value for p in WorkoutPhase]
        
        for phase in expected_phases:
            self.assertIn(phase, actual_phases)
    
    def test_phase_count(self):
        """Test: Número correcto de fases"""
        from playlist_generator import WorkoutPhase
        
        self.assertEqual(len(WorkoutPhase), 5)


class TestCyclingPlaylistGenerator(unittest.TestCase):
    """Tests para CyclingPlaylistGenerator"""
    
    def setUp(self):
        """Setup: Crear DataFrame de prueba"""
        self.test_df = create_test_song_dataframe(n_songs=20)
    
    def test_creation(self):
        """Test: Crear instancia de generador"""
        from playlist_generator import CyclingPlaylistGenerator
        
        generator = CyclingPlaylistGenerator(self.test_df)
        
        self.assertIsNotNone(generator)
        self.assertEqual(len(generator.df), 20)
    
    def test_df_is_copy(self):
        """Test: El DataFrame interno es una copia"""
        from playlist_generator import CyclingPlaylistGenerator
        
        original_df = self.test_df.copy()
        generator = CyclingPlaylistGenerator(self.test_df)
        
        # Modificar el original no debe afectar al generador
        self.test_df['bpm'] = 999
        self.assertNotEqual(generator.df['bpm'].iloc[0], 999)
    
    def test_calculate_scores(self):
        """Test: Se calculan todos los scores"""
        from playlist_generator import CyclingPlaylistGenerator
        
        generator = CyclingPlaylistGenerator(self.test_df)
        
        required_scores = [
            'intensity_score',
            'warmup_score',
            'cooldown_score',
            'motivation_score'
        ]
        
        for score in required_scores:
            self.assertIn(score, generator.df.columns)
    
    def test_scores_in_range(self):
        """Test: Scores están en rango válido"""
        from playlist_generator import CyclingPlaylistGenerator
        
        generator = CyclingPlaylistGenerator(self.test_df)
        
        self.assertTrue((generator.df['intensity_score'] >= 0).all())
        self.assertTrue((generator.df['intensity_score'] <= 1.1).all())
    
    def test_normalize_features(self):
        """Test: Features se normalizan correctamente"""
        from playlist_generator import CyclingPlaylistGenerator
        
        generator = CyclingPlaylistGenerator(self.test_df)
        
        normalized_cols = ['bpm_norm', 'energy_norm', 'brightness_norm']
        
        for col in normalized_cols:
            self.assertIn(col, generator.df.columns)
            self.assertTrue((generator.df[col] >= 0).all())
            self.assertTrue((generator.df[col] <= 1).all())


class TestEndurancePlaylist(unittest.TestCase):
    """Tests para playlists tipo endurance"""
    
    def setUp(self):
        """Setup"""
        from playlist_generator import CyclingPlaylistGenerator
        self.test_df = create_test_song_dataframe(n_songs=20)
        self.generator = CyclingPlaylistGenerator(self.test_df)
    
    def test_generate_endurance_30min(self):
        """Test: Generar playlist endurance de 30 minutos"""
        playlist = self.generator.generate_workout_playlist(
            duration_minutes=30,
            workout_type="endurance"
        )
        
        self.assertGreater(len(playlist), 0)
        assert_playlist_structure(playlist)
    
    def test_endurance_has_correct_phases(self):
        """Test: Playlist endurance tiene fases correctas"""
        playlist = self.generator.generate_workout_playlist(
            duration_minutes=30,
            workout_type="endurance"
        )
        
        phases = set(playlist['phase'].unique())
        expected = {'warmup', 'build', 'sustain', 'cooldown'}
        
        self.assertTrue(phases.issubset(expected))
    
    def test_endurance_starts_with_warmup(self):
        """Test: Playlist endurance empieza con warmup"""
        playlist = self.generator.generate_workout_playlist(
            duration_minutes=30,
            workout_type="endurance"
        )
        
        self.assertEqual(playlist.iloc[0]['phase'], 'warmup')
    
    def test_endurance_ends_with_cooldown(self):
        """Test: Playlist endurance termina con cooldown"""
        playlist = self.generator.generate_workout_playlist(
            duration_minutes=30,
            workout_type="endurance"
        )
        
        self.assertEqual(playlist.iloc[-1]['phase'], 'cooldown')
    
    def test_cumulative_time_exists(self):
        """Test: Se calcula tiempo acumulado"""
        playlist = self.generator.generate_workout_playlist(
            duration_minutes=30,
            workout_type="endurance"
        )
        
        self.assertIn('cumulative_time', playlist.columns)
        self.assertIn('start_time', playlist.columns)
        assert_time_progression(playlist)


class TestIntervalsPlaylist(unittest.TestCase):
    """Tests para playlists tipo intervals"""
    
    def setUp(self):
        """Setup"""
        from playlist_generator import CyclingPlaylistGenerator
        self.test_df = create_test_song_dataframe(n_songs=20)
        self.generator = CyclingPlaylistGenerator(self.test_df)
    
    def test_generate_intervals(self):
        """Test: Generar playlist intervals"""
        playlist = self.generator.generate_workout_playlist(
            duration_minutes=30,
            workout_type="intervals"
        )
        
        self.assertGreater(len(playlist), 0)
        assert_playlist_structure(playlist)
    
    def test_intervals_has_peak_phases(self):
        """Test: Playlist intervals tiene fases peak"""
        playlist = self.generator.generate_workout_playlist(
            duration_minutes=30,
            workout_type="intervals"
        )
        
        self.assertIn('peak', playlist['phase'].values)


class TestRecoveryPlaylist(unittest.TestCase):
    """Tests para playlists tipo recovery"""
    
    def setUp(self):
        """Setup"""
        from playlist_generator import CyclingPlaylistGenerator
        self.test_df = create_test_song_dataframe(n_songs=20)
        self.generator = CyclingPlaylistGenerator(self.test_df)
    
    def test_generate_recovery(self):
        """Test: Generar playlist recovery"""
        playlist = self.generator.generate_workout_playlist(
            duration_minutes=30,
            workout_type="recovery"
        )
        
        self.assertGreater(len(playlist), 0)
    
    def test_recovery_low_intensity(self):
        """Test: Recovery tiene baja intensidad promedio"""
        playlist = self.generator.generate_workout_playlist(
            duration_minutes=30,
            workout_type="recovery"
        )
        
        avg_intensity = playlist['intensity_score'].mean()
        self.assertLess(avg_intensity, 0.7)


class TestCadenceOrdering(unittest.TestCase):
    """Tests para ordenamiento por cadencia"""
    
    def setUp(self):
        """Setup"""
        from playlist_generator import CyclingPlaylistGenerator
        self.test_df = create_test_song_dataframe(n_songs=20)
        self.generator = CyclingPlaylistGenerator(self.test_df)
    
    def test_order_by_cadence_90rpm(self):
        """Test: Ordenar por cadencia 90 RPM"""
        playlist = self.generator.order_by_bpm_for_cadence(
            target_cadence=90,
            tolerance=10
        )
        
        self.assertGreater(len(playlist), 0)
        self.assertIn('best_cadence_match', playlist.columns)
    
    def test_cadence_match_calculation(self):
        """Test: Se calcula match de cadencia"""
        playlist = self.generator.order_by_bpm_for_cadence(
            target_cadence=90,
            tolerance=10
        )
        
        # Debe tener columnas de match
        required_cols = ['cadence_match_1x', 'cadence_match_2x', 'best_cadence_match']
        for col in required_cols:
            self.assertIn(col, playlist.columns)


class TestEnergyCurve(unittest.TestCase):
    """Tests para playlist con curva de energía personalizada"""
    
    def setUp(self):
        """Setup"""
        from playlist_generator import CyclingPlaylistGenerator
        self.test_df = create_test_song_dataframe(n_songs=20)
        self.generator = CyclingPlaylistGenerator(self.test_df)
    
    def test_generate_with_custom_curve(self):
        """Test: Generar playlist con curva personalizada"""
        energy_curve = [0.3, 0.5, 0.7, 0.9, 0.7, 0.5, 0.3]
        
        playlist = self.generator.generate_energy_curve_playlist(
            energy_curve=energy_curve,
            duration_minutes=30
        )
        
        self.assertGreater(len(playlist), 0)
        self.assertIn('target_energy', playlist.columns)
        self.assertIn('segment', playlist.columns)
    
    def test_curve_length_matches(self):
        """Test: Número de segmentos coincide con curva"""
        energy_curve = [0.3, 0.5, 0.7, 0.9, 0.7]
        
        playlist = self.generator.generate_energy_curve_playlist(
            energy_curve=energy_curve,
            duration_minutes=20
        )
        
        # Puede ser <= porque se puede quedar sin canciones
        self.assertLessEqual(len(playlist), len(energy_curve))


class TestNoduplicates(unittest.TestCase):
    """Tests para verificar que no hay duplicados"""
    
    def setUp(self):
        """Setup"""
        from playlist_generator import CyclingPlaylistGenerator
        self.test_df = create_test_song_dataframe(n_songs=20)
        self.generator = CyclingPlaylistGenerator(self.test_df)
    
    def test_no_duplicate_songs_endurance(self):
        """Test: No hay canciones duplicadas en endurance"""
        playlist = self.generator.generate_workout_playlist(
            duration_minutes=30,
            workout_type="endurance"
        )
        
        unique_count = playlist['filename'].nunique()
        total_count = len(playlist)
        
        self.assertEqual(unique_count, total_count)
    
    def test_no_duplicate_songs_intervals(self):
        """Test: No hay canciones duplicadas en intervals"""
        playlist = self.generator.generate_workout_playlist(
            duration_minutes=30,
            workout_type="intervals"
        )
        
        unique_count = playlist['filename'].nunique()
        total_count = len(playlist)
        
        self.assertEqual(unique_count, total_count)


if __name__ == '__main__':
    unittest.main()
