#!/usr/bin/env python3
"""
Ejemplos de uso del sistema de análisis de audio optimizado

Demuestra:
1. Uso básico con caché y procesamiento paralelo
2. Análisis secuencial para debugging
3. Análisis sin caché
4. Comparación de rendimiento
"""

from audio_analyzer import AudioAnalyzer
from pathlib import Path
import time


def ejemplo_basico():
    """Uso básico con todas las optimizaciones"""
    print("=" * 70)
    print("EJEMPLO 1: Uso básico (con caché + paralelo)")
    print("=" * 70)
    
    # Crear analizador con configuración por defecto
    analyzer = AudioAnalyzer("mis_canciones")
    
    # Analizar carpeta (automáticamente usa caché y paralelo)
    df = analyzer.analyze_folder()
    
    # Mostrar resultados
    print(f"\nCanciones analizadas: {len(df)}")
    if len(df) > 0:
        print("\nPrimeras 3 canciones:")
        print(df[['title', 'bpm', 'energy', 'duration']].head(3))
    
    return df


def ejemplo_sin_cache():
    """Análisis forzado sin usar caché"""
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Sin caché (fuerza re-análisis)")
    print("=" * 70)
    
    # Deshabilitar caché
    analyzer = AudioAnalyzer("mis_canciones", use_cache=False)
    df = analyzer.analyze_folder()
    
    print(f"\nCanciones analizadas: {len(df)}")
    return df


def ejemplo_secuencial():
    """Análisis secuencial para debugging"""
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Modo secuencial (para debugging)")
    print("=" * 70)
    
    analyzer = AudioAnalyzer("mis_canciones")
    df = analyzer.analyze_folder(use_parallel=False)
    
    print(f"\nCanciones analizadas: {len(df)}")
    return df


def ejemplo_control_procesos():
    """Control manual del número de procesos paralelos"""
    print("\n" + "=" * 70)
    print("EJEMPLO 4: Control de procesos paralelos")
    print("=" * 70)
    
    # Usar solo 2 procesos (útil si tienes pocos cores o poca RAM)
    analyzer = AudioAnalyzer("mis_canciones")
    df = analyzer.analyze_folder(n_jobs=2)
    
    print(f"\nCanciones analizadas: {len(df)}")
    return df


def ejemplo_cancion_individual():
    """Analizar una sola canción"""
    print("\n" + "=" * 70)
    print("EJEMPLO 5: Análisis de canción individual")
    print("=" * 70)
    
    analyzer = AudioAnalyzer("mis_canciones")
    
    # Buscar primera canción MP3
    music_folder = Path("mis_canciones")
    mp3_files = list(music_folder.glob("*.mp3"))
    
    if mp3_files:
        song_path = mp3_files[0]
        print(f"\nAnalizando: {song_path.name}")
        
        features = analyzer.analyze_song(song_path)
        
        if features:
            print(f"\nResultados:")
            print(f"  Título: {features.title}")
            print(f"  Duración: {features.duration:.1f}s")
            print(f"  BPM: {features.bpm:.1f}")
            print(f"  Energía: {features.energy:.2f}")
            print(f"  Brillo: {features.brightness:.2f}")
    else:
        print("No se encontraron archivos MP3")


def benchmark_comparativo():
    """Compara rendimiento de diferentes configuraciones"""
    print("\n" + "=" * 70)
    print("BENCHMARK: Comparación de rendimiento")
    print("=" * 70)
    
    # Limpiar caché para prueba justa
    cache_file = Path("csv/audio_cache.json")
    if cache_file.exists():
        cache_file.unlink()
        print("Caché limpiado para benchmark justo\n")
    
    results = {}
    
    # Test 1: Paralelo sin caché
    print("\n[1/3] Paralelo sin caché...")
    start = time.time()
    analyzer1 = AudioAnalyzer("mis_canciones", use_cache=False)
    df1 = analyzer1.analyze_folder(use_parallel=True)
    results['paralelo_sin_cache'] = time.time() - start
    
    # Test 2: Secuencial sin caché
    print("\n[2/3] Secuencial sin caché...")
    start = time.time()
    analyzer2 = AudioAnalyzer("mis_canciones", use_cache=False)
    df2 = analyzer2.analyze_folder(use_parallel=False)
    results['secuencial_sin_cache'] = time.time() - start
    
    # Test 3: Con caché (segunda ejecución)
    print("\n[3/3] Con caché (segunda ejecución)...")
    start = time.time()
    analyzer3 = AudioAnalyzer("mis_canciones", use_cache=True)
    df3 = analyzer3.analyze_folder()
    results['con_cache'] = time.time() - start
    
    # Mostrar resultados
    print("\n" + "=" * 70)
    print("RESULTADOS DEL BENCHMARK")
    print("=" * 70)
    print(f"Canciones procesadas: {len(df1)}\n")
    
    baseline = results['secuencial_sin_cache']
    for key, tiempo in results.items():
        speedup = baseline / tiempo if tiempo > 0 else 0
        print(f"{key:25s}: {tiempo:6.2f}s  (speedup: {speedup:.1f}x)")
    
    print("\n💡 Recomendación:")
    print("   - Usa el modo por defecto (caché + paralelo) para mejor rendimiento")
    print("   - Primera ejecución: beneficio del procesamiento paralelo")
    print("   - Ejecuciones subsiguientes: beneficio masivo del caché")


def main():
    """Ejecuta todos los ejemplos"""
    print("\n🎵 EJEMPLOS DE USO - AUDIO ANALYZER OPTIMIZADO")
    print("=" * 70)
    
    # Verificar que existe la carpeta de música
    if not Path("mis_canciones").exists():
        print("❌ Error: No existe la carpeta 'mis_canciones'")
        print("   Crea la carpeta y agrega archivos de audio para continuar")
        return
    
    try:
        # Ejemplo básico (el más común)
        ejemplo_basico()
        
        # Otros ejemplos (comentados para no repetir análisis)
        # Descomenta los que quieras probar:
        
        # ejemplo_sin_cache()
        # ejemplo_secuencial()
        # ejemplo_control_procesos()
        # ejemplo_cancion_individual()
        
        # Benchmark completo (toma más tiempo)
        # benchmark_comparativo()
        
        print("\n" + "=" * 70)
        print("✅ Ejemplos completados exitosamente")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
