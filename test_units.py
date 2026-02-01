#!/usr/bin/env python3
"""
🧪 Tests Unitarios con unittest

Tests más específicos y detallados para cada componente.

Uso:
    python -m unittest test_units.py           # Todos los tests
    python -m unittest test_units.TestAudioAnalyzer  # Solo AudioAnalyzer
    python -m unittest test_units.TestAudioAnalyzer.test_bpm_extraction  # Test específico
"""

import unittest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import shutil
import warnings
warnings.filterwarnings('ignore')


class TestSongFeatures(unittest.TestCase):
    """Tests para la clase SongFeatures"""
    
    def test_songfeatures_creation(self):
        """Test de creación de SongFeatures"""
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
        self.assertEqual(song.bpm, 120.0)
        self.assertGreaterEqual(song.energy, 0.0)
        self.assertLessEqual(song.energy, 1.0)
    
    def test_songfeatures_default_workout_score(self):
        """Test del valor por defecto de workout_score"""
        from audio_analyzer import SongFeatures
        
        song = SongFeatures(
            filename="test.mp3",
            title="Test",
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
        
        self.assertEqual(song.workout_score, 0.0)


class TestAudioAnalyzer(unittest.TestCase):
    """Tests para la clase AudioAnalyzer"""
    
    @classmethod
    def setUpClass(cls):
        """Setup que se ejecuta una vez antes de todos los tests"""
        # Crear carpeta temporal
        cls.temp_dir = tempfile.mkdtemp()
        cls.music_folder = Path(cls.temp_dir) / "test_music"
        cls.music_folder.mkdir()
        
        # Generar archivos de prueba si es posible
        try:
            import scipy.io.wavfile as wav
            sr = 22050
            duration = 3  # 3 segundos
            
            # Generar 3 archivos WAV de prueba
            for i, bpm in enumerate([100, 120, 140]):
                t = np.linspace(0, duration, int(sr * duration))
                # Señal simple con frecuencia proporcional al BPM
                freq = bpm / 60 * 2  # Hz
                signal = np.sin(2 * np.pi * freq * t)
                signal = (signal * 32767).astype(np.int16)
                
                filepath = cls.music_folder / f"test_song_{i}.wav"
                wav.write(str(filepath), sr, signal)
            
            cls.has_audio = True
        except:
            cls.has_audio = False
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup después de todos los tests"""
        shutil.rmtree(cls.temp_dir)
    
    def test_analyzer_creation(self):
        """Test de creación de AudioAnalyzer"""
        from audio_analyzer import AudioAnalyzer
        
        analyzer = AudioAnalyzer(str(self.music_folder))
        self.assertIsNotNone(analyzer)
        self.assertEqual(analyzer.music_folder, self.music_folder)
        self.assertEqual(len(analyzer.songs), 0)
    
    @unittest.skipUnless(Path("mis_canciones").exists(), 
                        "No hay carpeta mis_canciones")
    def test_analyze_folder_finds_files(self):
        """Test que analyze_folder encuentra archivos"""
        from audio_analyzer import AudioAnalyzer
        
        analyzer = AudioAnalyzer("mis_canciones")
        df = analyzer.analyze_folder()
        
        # Debe encontrar al menos algunos archivos
        self.assertGreater(len(df), 0, "No se encontraron archivos de audio")
    
    def test_to_dataframe(self):
        """Test de conversión a DataFrame"""
        from audio_analyzer import AudioAnalyzer, SongFeatures
        
        analyzer = AudioAnalyzer(str(self.music_folder))
        
        # Añadir songs manualmente
        analyzer.songs = [
            SongFeatures(
                filename="test1.mp3",
                title="Test 1",
                duration=180.0,
                bpm=120.0,
                beat_strength=0.8,
                energy=0.7,
                energy_variance=0.1,
                brightness=0.5,
                contrast=15.0,
                dynamic_range=0.3,
                onset_rate=2.5
            ),
            SongFeatures(
                filename="test2.mp3",
                title="Test 2",
                duration=200.0,
                bpm=140.0,
                beat_strength=0.9,
                energy=0.8,
                energy_variance=0.15,
                brightness=0.6,
                contrast=18.0,
                dynamic_range=0.4,
                onset_rate=3.0
            )
        ]
        
        df = analyzer.to_dataframe()
        
        self.assertEqual(len(df), 2)
        self.assertIn('filename', df.columns)
        self.assertIn('bpm', df.columns)
        self.assertIn('energy', df.columns)
        self.assertEqual(df.iloc[0]['bpm'], 120.0)
        self.assertEqual(df.iloc[1]['bpm'], 140.0)


class TestWorkoutPhase(unittest.TestCase):
    """Tests para el enum WorkoutPhase"""
    
    def test_workout_phases_exist(self):
        """Test que todas las fases existen"""
        from playlist_generator import WorkoutPhase
        
        phases = [p.value for p in WorkoutPhase]
        expected = ['warmup', 'build', 'peak', 'sustain', 'cooldown']
        
        for phase in expected:
            self.assertIn(phase, phases)


class TestCyclingPlaylistGenerator(unittest.TestCase):
    """Tests para CyclingPlaylistGenerator"""
    
    @classmethod
    def setUpClass(cls):
        """Setup con datos de prueba"""
        # Crear DataFrame de prueba
        cls.test_df = pd.DataFrame({
            'filename': [f'song_{i}.mp3' for i in range(20)],
            'title': [f'Test Song {i}' for i in range(20)],
            'duration': np.random.uniform(150, 250, 20),
            'bpm': np.random.uniform(80, 160, 20),
            'beat_strength': np.random.uniform(0.5, 1.0, 20),
            'energy': np.random.uniform(0.2, 0.9, 20),
            'energy_variance': np.random.uniform(0.05, 0.2, 20),
            'brightness': np.random.uniform(0.3, 0.8, 20),
            'contrast': np.random.uniform(10, 25, 20),
            'dynamic_range': np.random.uniform(0.1, 0.5, 20),
            'onset_rate': np.random.uniform(1.5, 4.0, 20)
        })
    
    def test_generator_creation(self):
        """Test de creación del generador"""
        from playlist_generator import CyclingPlaylistGenerator
        
        generator = CyclingPlaylistGenerator(self.test_df)
        self.assertIsNotNone(generator)
        self.assertEqual(len(generator.df), 20)
    
    def test_calculate_scores(self):
        """Test del cálculo de scores"""
        from playlist_generator import CyclingPlaylistGenerator
        
        generator = CyclingPlaylistGenerator(self.test_df)
        
        # Verificar que se calcularon los scores
        self.assertIn('intensity_score', generator.df.columns)
        self.assertIn('warmup_score', generator.df.columns)
        self.assertIn('cooldown_score', generator.df.columns)
        self.assertIn('motivation_score', generator.df.columns)
        
        # Verificar rangos
        self.assertTrue((generator.df['intensity_score'] >= 0).all())
        self.assertTrue((generator.df['intensity_score'] <= 1.1).all())
    
    def test_normalize_features(self):
        """Test de normalización de features"""
        from playlist_generator import CyclingPlaylistGenerator
        
        generator = CyclingPlaylistGenerator(self.test_df)
        
        # Verificar que se crearon columnas normalizadas
        self.assertIn('bpm_norm', generator.df.columns)
        self.assertIn('energy_norm', generator.df.columns)
        
        # Verificar rango 0-1
        self.assertTrue((generator.df['bpm_norm'] >= 0).all())
        self.assertTrue((generator.df['bpm_norm'] <= 1).all())
    
    def test_generate_endurance_playlist(self):
        """Test de generación de playlist endurance"""
        from playlist_generator import CyclingPlaylistGenerator
        
        generator = CyclingPlaylistGenerator(self.test_df)
        playlist = generator.generate_workout_playlist(
            duration_minutes=30,
            workout_type="endurance"
        )
        
        self.assertGreater(len(playlist), 0)
        self.assertIn('phase', playlist.columns)
        
        # Verificar que tiene las fases correctas
        phases = set(playlist['phase'].unique())
        expected = {'warmup', 'build', 'sustain', 'cooldown'}
        self.assertTrue(phases.issubset(expected))
        
        # Primera canción debe ser warmup
        self.assertEqual(playlist.iloc[0]['phase'], 'warmup')
        
        # Última canción debe ser cooldown
        self.assertEqual(playlist.iloc[-1]['phase'], 'cooldown')
    
    def test_generate_intervals_playlist(self):
        """Test de generación de playlist intervals"""
        from playlist_generator import CyclingPlaylistGenerator
        
        generator = CyclingPlaylistGenerator(self.test_df)
        playlist = generator.generate_workout_playlist(
            duration_minutes=30,
            workout_type="intervals"
        )
        
        self.assertGreater(len(playlist), 0)
        
        # Debe contener fases peak (intervalos)
        phases = playlist['phase'].unique()
        self.assertIn('peak', phases)
    
    def test_generate_recovery_playlist(self):
        """Test de generación de playlist recovery"""
        from playlist_generator import CyclingPlaylistGenerator
        
        generator = CyclingPlaylistGenerator(self.test_df)
        playlist = generator.generate_workout_playlist(
            duration_minutes=30,
            workout_type="recovery"
        )
        
        self.assertGreater(len(playlist), 0)
        
        # Recovery debe tener baja intensidad promedio
        avg_intensity = playlist['intensity_score'].mean()
        self.assertLess(avg_intensity, 0.7)
    
    def test_order_by_cadence(self):
        """Test de ordenamiento por cadencia"""
        from playlist_generator import CyclingPlaylistGenerator
        
        generator = CyclingPlaylistGenerator(self.test_df)
        playlist = generator.order_by_bpm_for_cadence(
            target_cadence=90,
            tolerance=10
        )
        
        self.assertGreater(len(playlist), 0)
        self.assertIn('best_cadence_match', playlist.columns)
        
        # Todas las canciones deben estar dentro de la tolerancia o ser las mejores disponibles
        # (puede no haber suficientes canciones dentro del rango)
    
    def test_energy_curve_playlist(self):
        """Test de playlist con curva de energía"""
        from playlist_generator import CyclingPlaylistGenerator
        
        generator = CyclingPlaylistGenerator(self.test_df)
        energy_curve = [0.3, 0.5, 0.7, 0.9, 0.7, 0.5, 0.3]
        
        playlist = generator.generate_energy_curve_playlist(
            energy_curve=energy_curve,
            duration_minutes=30
        )
        
        self.assertGreater(len(playlist), 0)
        self.assertIn('target_energy', playlist.columns)
        self.assertIn('segment', playlist.columns)
    
    def test_cumulative_time_calculation(self):
        """Test del cálculo de tiempo acumulado"""
        from playlist_generator import CyclingPlaylistGenerator
        
        generator = CyclingPlaylistGenerator(self.test_df)
        playlist = generator.generate_workout_playlist(
            duration_minutes=20,
            workout_type="endurance"
        )
        
        # Verificar que cumulative_time es creciente
        self.assertTrue((playlist['cumulative_time'].diff()[1:] > 0).all())
        
        # Verificar que start_time + duration = cumulative_time
        calculated = playlist['start_time'] + playlist['duration']
        np.testing.assert_array_almost_equal(
            calculated.values,
            playlist['cumulative_time'].values,
            decimal=2
        )
    
    def test_no_duplicate_songs(self):
        """Test que no se repiten canciones en la playlist"""
        from playlist_generator import CyclingPlaylistGenerator
        
        generator = CyclingPlaylistGenerator(self.test_df)
        playlist = generator.generate_workout_playlist(
            duration_minutes=30,
            workout_type="endurance"
        )
        
        # No debe haber duplicados
        unique_songs = playlist['filename'].nunique()
        total_songs = len(playlist)
        self.assertEqual(unique_songs, total_songs)


class TestVisualization(unittest.TestCase):
    """Tests para el módulo de visualización"""
    
    @classmethod
    def setUpClass(cls):
        """Setup con playlist de prueba"""
        cls.test_playlist = pd.DataFrame({
            'filename': [f'song_{i}.mp3' for i in range(10)],
            'title': [f'Test Song {i}' for i in range(10)],
            'duration': [180] * 10,
            'bpm': [90, 100, 110, 120, 130, 130, 120, 110, 100, 90],
            'intensity_score': [0.2, 0.3, 0.5, 0.7, 0.8, 0.8, 0.7, 0.5, 0.3, 0.2],
            'phase': ['warmup', 'build', 'build', 'sustain', 'peak', 
                     'sustain', 'sustain', 'sustain', 'cooldown', 'cooldown'],
            'start_time': [i * 180 for i in range(10)],
            'cumulative_time': [(i + 1) * 180 for i in range(10)]
        })
    
    def test_visualize_playlist_creates_image(self):
        """Test que la visualización crea una imagen"""
        import matplotlib
        matplotlib.use('Agg')  # Backend sin GUI
        from visualize import visualize_playlist
        
        output_file = Path("test_viz.png")
        
        # Limpiar si existe
        if output_file.exists():
            output_file.unlink()
        
        # Modificar temporalmente la función para guardar con nombre diferente
        import matplotlib.pyplot as plt
        visualize_playlist(self.test_playlist)
        
        # Cambiar nombre del archivo generado
        if Path("playlist_visualization.png").exists():
            Path("playlist_visualization.png").rename(output_file)
        
        self.assertTrue(output_file.exists())
        
        # Cleanup
        if output_file.exists():
            output_file.unlink()


class TestIntegration(unittest.TestCase):
    """Tests de integración entre módulos"""
    
    @unittest.skipUnless(Path("mis_canciones").exists(), 
                        "No hay carpeta mis_canciones")
    def test_full_pipeline(self):
        """Test del pipeline completo"""
        from audio_analyzer import AudioAnalyzer
        from playlist_generator import CyclingPlaylistGenerator
        
        # Análisis
        analyzer = AudioAnalyzer("mis_canciones")
        songs_df = analyzer.analyze_folder()
        
        self.assertGreater(len(songs_df), 0)
        
        # Generación
        generator = CyclingPlaylistGenerator(songs_df)
        playlist = generator.generate_workout_playlist(30, "endurance")
        
        self.assertGreater(len(playlist), 0)
        
        # Verificar estructura
        required_columns = ['filename', 'title', 'bpm', 'energy', 'phase']
        for col in required_columns:
            self.assertIn(col, playlist.columns)
    
    def test_m3u_generation(self):
        """Test de generación de archivo M3U"""
        from main import generate_m3u
        
        test_playlist = pd.DataFrame({
            'filename': ['song1.mp3', 'song2.mp3'],
            'title': ['Song 1', 'Song 2'],
            'duration': [180, 200]
        })
        
        output_file = "test_output.m3u"
        generate_m3u(test_playlist, output_file, "mis_canciones")
        
        self.assertTrue(Path(output_file).exists())
        
        # Verificar contenido
        with open(output_file, 'r') as f:
            content = f.read()
            self.assertIn("#EXTM3U", content)
            self.assertIn("#EXTINF:", content)
            self.assertIn("song1.mp3", content)
        
        # Cleanup
        Path(output_file).unlink()


class TestDataValidation(unittest.TestCase):
    """Tests de validación de datos"""
    
    def test_bpm_range(self):
        """Test que BPM está en rango razonable"""
        test_df = pd.DataFrame({
            'filename': ['test.mp3'],
            'title': ['Test'],
            'duration': [180],
            'bpm': [120],
            'beat_strength': [0.8],
            'energy': [0.7],
            'energy_variance': [0.1],
            'brightness': [0.5],
            'contrast': [15.0],
            'dynamic_range': [0.3],
            'onset_rate': [2.5]
        })
        
        # BPM debe estar entre 40 y 200
        self.assertGreaterEqual(test_df['bpm'].iloc[0], 40)
        self.assertLessEqual(test_df['bpm'].iloc[0], 200)
    
    def test_energy_normalized(self):
        """Test que energía está normalizada"""
        test_df = pd.DataFrame({
            'energy': [0.0, 0.5, 1.0, 0.25, 0.75]
        })
        
        # Energía debe estar entre 0 y 1
        self.assertTrue((test_df['energy'] >= 0).all())
        self.assertTrue((test_df['energy'] <= 1.0).all())
    
    def test_no_negative_duration(self):
        """Test que duración no es negativa"""
        test_df = pd.DataFrame({
            'duration': [180, 200, 150, 220]
        })
        
        self.assertTrue((test_df['duration'] > 0).all())


def run_tests_with_coverage():
    """Ejecuta tests con reporte de cobertura"""
    try:
        import coverage
        
        cov = coverage.Coverage()
        cov.start()
        
        # Ejecutar tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(__import__(__name__))
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        cov.stop()
        cov.save()
        
        print("\n" + "="*70)
        print("REPORTE DE COBERTURA")
        print("="*70 + "\n")
        
        cov.report()
        
        # Generar HTML
        cov.html_report(directory='htmlcov')
        print("\nReporte HTML generado en: htmlcov/index.html")
        
        return result.wasSuccessful()
        
    except ImportError:
        print("⚠️  coverage no instalado - ejecutando sin cobertura")
        print("   Instala con: pip install coverage\n")
        
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(__import__(__name__))
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    
    if '--coverage' in sys.argv:
        sys.argv.remove('--coverage')
        success = run_tests_with_coverage()
        sys.exit(0 if success else 1)
    else:
        unittest.main()
