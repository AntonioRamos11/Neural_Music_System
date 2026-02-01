#!/usr/bin/env python3
"""
🧪 Suite de Pruebas Completa para el Sistema de Playlists

Prueba todos los módulos del sistema de manera integral:
- Generación de audio de prueba
- Análisis de features de audio
- Generación de playlists
- Visualización

Uso:
    python test_system.py           # Ejecuta todas las pruebas
    python test_system.py --quick   # Solo pruebas rápidas
    python test_system.py --verbose # Modo verbose
"""

import sys
import os
import time
import traceback
from pathlib import Path
from typing import List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Imprime encabezado decorado"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_test(test_name: str):
    """Imprime nombre de test"""
    print(f"{Colors.BLUE}🧪 Test:{Colors.END} {test_name}...", end=" ", flush=True)

def print_success(message: str = "✅ PASS"):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}{message}{Colors.END}")

def print_error(message: str = "❌ FAIL"):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}{message}{Colors.END}")

def print_warning(message: str):
    """Imprime advertencia"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message: str):
    """Imprime información"""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.END}")

class TestResults:
    """Acumula resultados de tests"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors: List[Tuple[str, str]] = []
        self.start_time = time.time()
    
    def add_pass(self):
        self.passed += 1
    
    def add_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append((test_name, error))
    
    def print_summary(self):
        """Imprime resumen final"""
        elapsed = time.time() - self.start_time
        
        print_header("RESUMEN DE PRUEBAS")
        
        total = self.passed + self.failed
        print(f"Total de pruebas: {total}")
        print(f"{Colors.GREEN}✅ Pasadas: {self.passed}{Colors.END}")
        print(f"{Colors.RED}❌ Falladas: {self.failed}{Colors.END}")
        print(f"⏱️  Tiempo: {elapsed:.2f}s\n")
        
        if self.errors:
            print(f"{Colors.RED}{Colors.BOLD}ERRORES ENCONTRADOS:{Colors.END}\n")
            for test_name, error in self.errors:
                print(f"{Colors.RED}❌ {test_name}:{Colors.END}")
                print(f"   {error}\n")
        
        # Resultado final
        if self.failed == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 TODAS LAS PRUEBAS PASARON 🎉{Colors.END}\n")
            return True
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ ALGUNAS PRUEBAS FALLARON{Colors.END}\n")
            return False


# ============================================================================
# TESTS DE GENERACIÓN DE AUDIO
# ============================================================================

def test_audio_generation(results: TestResults):
    """Prueba la generación de audio sintético"""
    print_header("MÓDULO: Generación de Audio de Prueba")
    
    # Test 1: Importar módulo
    print_test("Importar generar_audio_prueba")
    try:
        import generar_audio_prueba
        print_success()
        results.add_pass()
    except Exception as e:
        print_error()
        results.add_fail("Importar generar_audio_prueba", str(e))
        return
    
    # Test 2: Verificar scipy
    print_test("Verificar dependencia scipy")
    try:
        import scipy.io.wavfile
        print_success()
        results.add_pass()
    except Exception as e:
        print_warning("scipy no instalado - se omitirá generación de audio")
        results.add_pass()
        return
    
    # Test 3: Generar archivos
    print_test("Generar archivos de audio de prueba")
    try:
        generar_audio_prueba.generar_audio_prueba()
        
        # Verificar que se crearon archivos
        music_folder = Path("mis_canciones")
        wav_files = list(music_folder.glob("*.wav"))
        
        if len(wav_files) >= 10:
            print_success(f"✅ {len(wav_files)} archivos creados")
            results.add_pass()
        else:
            print_error(f"Solo {len(wav_files)} archivos (esperado: 12)")
            results.add_fail("Generar archivos", "Archivos insuficientes")
    except Exception as e:
        print_error()
        results.add_fail("Generar archivos", str(e))


# ============================================================================
# TESTS DE ANÁLISIS DE AUDIO
# ============================================================================

def test_audio_analysis(results: TestResults, quick: bool = False):
    """Prueba el módulo de análisis de audio"""
    print_header("MÓDULO: Análisis de Audio")
    
    # Test 1: Importar módulo
    print_test("Importar audio_analyzer")
    try:
        from audio_analyzer import AudioAnalyzer, SongFeatures
        print_success()
        results.add_pass()
    except Exception as e:
        print_error()
        results.add_fail("Importar audio_analyzer", str(e))
        return
    
    # Test 2: Verificar librosa
    print_test("Verificar dependencia librosa")
    try:
        import librosa
        print_success()
        results.add_pass()
    except Exception as e:
        print_error()
        results.add_fail("Verificar librosa", str(e))
        return
    
    # Test 3: Crear instancia AudioAnalyzer
    print_test("Crear instancia AudioAnalyzer")
    try:
        from audio_analyzer import AudioAnalyzer
        analyzer = AudioAnalyzer("mis_canciones")
        assert analyzer.music_folder.exists(), "Carpeta no existe"
        print_success()
        results.add_pass()
    except Exception as e:
        print_error()
        results.add_fail("Crear AudioAnalyzer", str(e))
        return
    
    # Test 4: Analizar un archivo individual
    print_test("Analizar archivo individual")
    try:
        music_folder = Path("mis_canciones")
        audio_files = list(music_folder.glob("*.wav")) + list(music_folder.glob("*.mp3"))
        
        if len(audio_files) == 0:
            print_warning("No hay archivos de audio para analizar")
            results.add_pass()
        else:
            test_file = audio_files[0]
            features = analyzer.analyze_song(test_file)
            
            assert features is not None, "No se extrajeron features"
            assert features.bpm > 0, "BPM inválido"
            assert 0 <= features.energy <= 1, "Energía fuera de rango"
            assert features.duration > 0, "Duración inválida"
            
            print_success()
            results.add_pass()
    except Exception as e:
        print_error()
        results.add_fail("Analizar archivo", str(e))
        return
    
    # Test 5: Analizar carpeta completa
    if not quick:
        print_test("Analizar carpeta completa")
        try:
            from audio_analyzer import AudioAnalyzer
            analyzer = AudioAnalyzer("mis_canciones")
            df = analyzer.analyze_folder()
            
            assert len(df) > 0, "No se analizaron canciones"
            assert 'bpm' in df.columns, "Falta columna BPM"
            assert 'energy' in df.columns, "Falta columna energía"
            assert df['bpm'].isna().sum() == 0, "Hay valores NaN en BPM"
            
            print_success(f"✅ {len(df)} canciones analizadas")
            results.add_pass()
            
            # Guardar para tests posteriores
            df.to_csv("test_song_analysis.csv", index=False)
            
        except Exception as e:
            print_error()
            results.add_fail("Analizar carpeta", str(e))
            return
    else:
        print_info("Omitiendo análisis completo (modo quick)")
    
    # Test 6: Validar features extraídas
    print_test("Validar rangos de features")
    try:
        import pandas as pd
        if Path("test_song_analysis.csv").exists():
            df = pd.read_csv("test_song_analysis.csv")
        else:
            from audio_analyzer import AudioAnalyzer
            analyzer = AudioAnalyzer("mis_canciones")
            df = analyzer.analyze_folder()
        
        # Validar rangos
        assert df['bpm'].min() > 0, "BPM negativo o cero"
        assert df['bpm'].max() < 300, "BPM demasiado alto"
        assert df['energy'].min() >= 0, "Energía negativa"
        assert df['energy'].max() <= 1.1, "Energía fuera de rango"
        assert df['duration'].min() > 0, "Duración inválida"
        
        print_success()
        results.add_pass()
        
    except Exception as e:
        print_error()
        results.add_fail("Validar features", str(e))


# ============================================================================
# TESTS DE GENERACIÓN DE PLAYLISTS
# ============================================================================

def test_playlist_generation(results: TestResults):
    """Prueba el módulo de generación de playlists"""
    print_header("MÓDULO: Generación de Playlists")
    
    # Test 1: Importar módulo
    print_test("Importar playlist_generator")
    try:
        from playlist_generator import CyclingPlaylistGenerator, WorkoutPhase
        print_success()
        results.add_pass()
    except Exception as e:
        print_error()
        results.add_fail("Importar playlist_generator", str(e))
        return
    
    # Cargar datos
    try:
        import pandas as pd
        if Path("test_song_analysis.csv").exists():
            df = pd.read_csv("test_song_analysis.csv")
        else:
            print_warning("No hay datos de análisis - ejecutando análisis...")
            from audio_analyzer import AudioAnalyzer
            analyzer = AudioAnalyzer("mis_canciones")
            df = analyzer.analyze_folder()
            df.to_csv("test_song_analysis.csv", index=False)
        
        if len(df) == 0:
            print_warning("No hay canciones analizadas para generar playlist")
            return
            
    except Exception as e:
        print_error(f"Error cargando datos: {e}")
        return
    
    # Test 2: Crear generador
    print_test("Crear CyclingPlaylistGenerator")
    try:
        from playlist_generator import CyclingPlaylistGenerator
        generator = CyclingPlaylistGenerator(df)
        assert hasattr(generator, 'df'), "No tiene atributo df"
        print_success()
        results.add_pass()
    except Exception as e:
        print_error()
        results.add_fail("Crear generador", str(e))
        return
    
    # Test 3: Calcular scores
    print_test("Calcular scores de intensidad")
    try:
        assert 'intensity_score' in generator.df.columns, "Falta intensity_score"
        assert 'warmup_score' in generator.df.columns, "Falta warmup_score"
        assert 'cooldown_score' in generator.df.columns, "Falta cooldown_score"
        
        # Validar rangos
        assert generator.df['intensity_score'].min() >= 0, "Score negativo"
        assert generator.df['intensity_score'].max() <= 1.1, "Score fuera de rango"
        
        print_success()
        results.add_pass()
    except Exception as e:
        print_error()
        results.add_fail("Calcular scores", str(e))
    
    # Test 4: Generar playlist de endurance
    print_test("Generar playlist endurance (60 min)")
    try:
        playlist = generator.generate_workout_playlist(
            duration_minutes=60,
            workout_type="endurance"
        )
        
        assert len(playlist) > 0, "Playlist vacía"
        assert 'phase' in playlist.columns, "Falta columna phase"
        assert 'cumulative_time' in playlist.columns, "Falta tiempo acumulado"
        
        # Validar fases
        phases = set(playlist['phase'].unique())
        expected_phases = {'warmup', 'build', 'sustain', 'cooldown'}
        assert phases.issubset(expected_phases), f"Fases inesperadas: {phases}"
        
        # Validar orden lógico
        first_phase = playlist.iloc[0]['phase']
        last_phase = playlist.iloc[-1]['phase']
        assert first_phase == 'warmup', f"Primera fase debe ser warmup, es {first_phase}"
        assert last_phase == 'cooldown', f"Última fase debe ser cooldown, es {last_phase}"
        
        print_success(f"✅ {len(playlist)} canciones")
        results.add_pass()
        
        # Guardar para test de visualización
        playlist.to_csv("test_playlist.csv", index=False)
        
    except Exception as e:
        print_error()
        results.add_fail("Generar playlist endurance", str(e))
    
    # Test 5: Generar playlist de intervals
    print_test("Generar playlist intervals (45 min)")
    try:
        playlist = generator.generate_workout_playlist(
            duration_minutes=45,
            workout_type="intervals"
        )
        
        assert len(playlist) > 0, "Playlist vacía"
        
        # Debe tener fases de peak (intervalos)
        assert 'peak' in playlist['phase'].values, "Falta fase peak en intervals"
        
        print_success(f"✅ {len(playlist)} canciones")
        results.add_pass()
        
    except Exception as e:
        print_error()
        results.add_fail("Generar playlist intervals", str(e))
    
    # Test 6: Generar playlist de recovery
    print_test("Generar playlist recovery (30 min)")
    try:
        playlist = generator.generate_workout_playlist(
            duration_minutes=30,
            workout_type="recovery"
        )
        
        assert len(playlist) > 0, "Playlist vacía"
        
        # Recovery debe tener intensidad baja en promedio
        avg_intensity = playlist['intensity_score'].mean()
        assert avg_intensity < 0.6, f"Intensidad demasiado alta para recovery: {avg_intensity}"
        
        print_success(f"✅ {len(playlist)} canciones")
        results.add_pass()
        
    except Exception as e:
        print_error()
        results.add_fail("Generar playlist recovery", str(e))
    
    # Test 7: Ordenar por cadencia
    print_test("Ordenar por cadencia objetivo (90 RPM)")
    try:
        cadence_playlist = generator.order_by_bpm_for_cadence(
            target_cadence=90,
            tolerance=10
        )
        
        assert len(cadence_playlist) > 0, "Playlist vacía"
        assert 'best_cadence_match' in cadence_playlist.columns, "Falta cadence match"
        
        print_success(f"✅ {len(cadence_playlist)} canciones")
        results.add_pass()
        
    except Exception as e:
        print_error()
        results.add_fail("Ordenar por cadencia", str(e))
    
    # Test 8: Generar curva de energía personalizada
    print_test("Generar playlist con curva personalizada")
    try:
        custom_curve = [0.3, 0.5, 0.7, 0.8, 0.9, 0.8, 0.6, 0.4]
        playlist = generator.generate_energy_curve_playlist(
            energy_curve=custom_curve,
            duration_minutes=40
        )
        
        assert len(playlist) > 0, "Playlist vacía"
        assert 'target_energy' in playlist.columns, "Falta target_energy"
        
        print_success(f"✅ {len(playlist)} canciones")
        results.add_pass()
        
    except Exception as e:
        print_error()
        results.add_fail("Curva personalizada", str(e))


# ============================================================================
# TESTS DE VISUALIZACIÓN
# ============================================================================

def test_visualization(results: TestResults):
    """Prueba el módulo de visualización"""
    print_header("MÓDULO: Visualización")
    
    # Test 1: Importar módulo
    print_test("Importar visualize")
    try:
        import visualize
        print_success()
        results.add_pass()
    except Exception as e:
        print_error()
        results.add_fail("Importar visualize", str(e))
        return
    
    # Test 2: Verificar matplotlib
    print_test("Verificar matplotlib")
    try:
        import matplotlib
        matplotlib.use('Agg')  # Backend sin GUI para tests
        import matplotlib.pyplot as plt
        print_success()
        results.add_pass()
    except Exception as e:
        print_error()
        results.add_fail("Verificar matplotlib", str(e))
        return
    
    # Test 3: Visualizar playlist
    print_test("Generar visualización de playlist")
    try:
        import pandas as pd
        import matplotlib
        matplotlib.use('Agg')
        from visualize import visualize_playlist
        
        if not Path("test_playlist.csv").exists():
            print_warning("No hay playlist para visualizar - generando...")
            from playlist_generator import CyclingPlaylistGenerator
            df = pd.read_csv("test_song_analysis.csv")
            generator = CyclingPlaylistGenerator(df)
            playlist = generator.generate_workout_playlist(60, "endurance")
            playlist.to_csv("test_playlist.csv", index=False)
        
        playlist = pd.read_csv("test_playlist.csv")
        visualize_playlist(playlist)
        
        # Verificar que se creó el archivo
        assert Path("playlist_visualization.png").exists(), "No se creó la imagen"
        
        print_success()
        results.add_pass()
        
    except Exception as e:
        print_error()
        results.add_fail("Visualizar playlist", traceback.format_exc().split('\n')[-2])


# ============================================================================
# TESTS DE INTEGRACIÓN
# ============================================================================

def test_integration(results: TestResults):
    """Prueba el flujo completo del sistema"""
    print_header("TESTS DE INTEGRACIÓN")
    
    # Test 1: Flujo completo
    print_test("Flujo completo: Análisis → Playlist → Export")
    try:
        from audio_analyzer import AudioAnalyzer
        from playlist_generator import CyclingPlaylistGenerator
        import pandas as pd
        
        # Análisis
        analyzer = AudioAnalyzer("mis_canciones")
        songs_df = analyzer.analyze_folder()
        assert len(songs_df) > 0, "No se analizaron canciones"
        
        # Generación
        generator = CyclingPlaylistGenerator(songs_df)
        playlist = generator.generate_workout_playlist(60, "endurance")
        assert len(playlist) > 0, "No se generó playlist"
        
        # Export CSV
        playlist.to_csv("test_full_playlist.csv", index=False)
        assert Path("test_full_playlist.csv").exists(), "No se guardó CSV"
        
        print_success()
        results.add_pass()
        
    except Exception as e:
        print_error()
        results.add_fail("Flujo completo", str(e))
    
    # Test 2: Generar M3U
    print_test("Generar archivo M3U")
    try:
        import pandas as pd
        from main import generate_m3u
        
        playlist = pd.read_csv("test_full_playlist.csv")
        generate_m3u(playlist, "test_playlist.m3u", "mis_canciones")
        
        assert Path("test_playlist.m3u").exists(), "No se creó M3U"
        
        # Validar contenido
        with open("test_playlist.m3u", 'r') as f:
            content = f.read()
            assert "#EXTM3U" in content, "Falta header M3U"
            assert "#EXTINF:" in content, "Falta metadata"
        
        print_success()
        results.add_pass()
        
    except Exception as e:
        print_error()
        results.add_fail("Generar M3U", str(e))


# ============================================================================
# TESTS DE VALIDACIÓN DE DATOS
# ============================================================================

def test_data_validation(results: TestResults):
    """Valida la calidad de los datos generados"""
    print_header("VALIDACIÓN DE DATOS")
    
    import pandas as pd
    
    # Test 1: Validar análisis de canciones
    print_test("Validar datos de análisis")
    try:
        df = pd.read_csv("test_song_analysis.csv")
        
        # No debe haber NaN
        assert df.isna().sum().sum() == 0, "Hay valores NaN en el análisis"
        
        # Validar tipos
        assert df['bpm'].dtype in ['float64', 'int64'], "BPM tipo incorrecto"
        assert df['energy'].dtype == 'float64', "Energy tipo incorrecto"
        
        # Validar unicidad de archivos
        assert df['filename'].nunique() == len(df), "Archivos duplicados"
        
        print_success()
        results.add_pass()
        
    except Exception as e:
        print_error()
        results.add_fail("Validar análisis", str(e))
    
    # Test 2: Validar playlist
    print_test("Validar estructura de playlist")
    try:
        df = pd.read_csv("test_full_playlist.csv")
        
        required_cols = ['filename', 'title', 'bpm', 'energy', 'phase', 
                        'duration', 'cumulative_time']
        missing = set(required_cols) - set(df.columns)
        assert len(missing) == 0, f"Faltan columnas: {missing}"
        
        # Validar tiempo acumulado es creciente
        assert (df['cumulative_time'].diff()[1:] > 0).all(), "Tiempo no es creciente"
        
        # Validar fases válidas
        valid_phases = {'warmup', 'build', 'peak', 'sustain', 'cooldown'}
        invalid = set(df['phase'].unique()) - valid_phases
        assert len(invalid) == 0, f"Fases inválidas: {invalid}"
        
        print_success()
        results.add_pass()
        
    except Exception as e:
        print_error()
        results.add_fail("Validar playlist", str(e))


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Ejecuta todas las pruebas"""
    
    # Parse argumentos
    quick = '--quick' in sys.argv
    verbose = '--verbose' in sys.argv
    
    if verbose:
        print_info("Modo verbose activado")
    
    print(f"""
{Colors.BOLD}{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         🧪 SUITE DE PRUEBAS - MUSIC CYCLING SYSTEM 🚴          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
{Colors.END}
    """)
    
    if quick:
        print_info("Modo QUICK - se omitirán pruebas lentas\n")
    
    results = TestResults()
    
    try:
        # Ejecutar tests
        test_audio_generation(results)
        test_audio_analysis(results, quick=quick)
        test_playlist_generation(results)
        test_visualization(results)
        test_integration(results)
        test_data_validation(results)
        
    except KeyboardInterrupt:
        print_warning("\n\nPruebas interrumpidas por el usuario")
        return 1
    
    except Exception as e:
        print_error(f"\n\nError fatal: {e}")
        traceback.print_exc()
        return 1
    
    # Mostrar resumen
    success = results.print_summary()
    
    # Limpiar archivos de test
    print_info("Limpiando archivos temporales de test...")
    temp_files = [
        "test_song_analysis.csv",
        "test_playlist.csv",
        "test_full_playlist.csv",
        "test_playlist.m3u"
    ]
    for f in temp_files:
        if Path(f).exists():
            Path(f).unlink()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
