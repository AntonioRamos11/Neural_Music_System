#!/usr/bin/env python3
"""
Script para probar las mejoras de velocidad en el análisis de audio
"""
from audio_analyzer import AudioAnalyzer
import time

def test_analysis_speed():
    """Prueba el análisis con y sin optimizaciones"""
    
    print("=" * 70)
    print("🚀 TEST DE VELOCIDAD - ANÁLISIS DE AUDIO")
    print("=" * 70)
    print()
    
    # Test 1: Con caché y paralelo (modo normal)
    print("📊 Test 1: Con caché + procesamiento paralelo (OPTIMIZADO)")
    print("-" * 70)
    start = time.time()
    analyzer1 = AudioAnalyzer("mis_canciones", use_cache=True)
    df1 = analyzer1.analyze_folder(use_parallel=True)
    time1 = time.time() - start
    print(f"\n⏱️  Tiempo: {time1:.2f} segundos")
    print(f"📊 Canciones analizadas: {len(df1)}")
    print()
    
    # Test 2: Sin caché, con paralelo
    print("=" * 70)
    print("📊 Test 2: Sin caché + procesamiento paralelo")
    print("-" * 70)
    print("(Borrando caché para forzar re-análisis...)")
    import os
    if os.path.exists("csv/audio_cache.json"):
        os.remove("csv/audio_cache.json")
    
    start = time.time()
    analyzer2 = AudioAnalyzer("mis_canciones", use_cache=False)
    df2 = analyzer2.analyze_folder(use_parallel=True)
    time2 = time.time() - start
    print(f"\n⏱️  Tiempo: {time2:.2f} segundos")
    print(f"📊 Canciones analizadas: {len(df2)}")
    print()
    
    # Test 3: Sin caché, secuencial (modo antiguo)
    print("=" * 70)
    print("📊 Test 3: Sin caché + secuencial (MODO ANTIGUO)")
    print("-" * 70)
    start = time.time()
    analyzer3 = AudioAnalyzer("mis_canciones", use_cache=False)
    df3 = analyzer3.analyze_folder(use_parallel=False)
    time3 = time.time() - start
    print(f"\n⏱️  Tiempo: {time3:.2f} segundos")
    print(f"📊 Canciones analizadas: {len(df3)}")
    print()
    
    # Resumen
    print("=" * 70)
    print("📈 RESUMEN DE MEJORAS")
    print("=" * 70)
    if time3 > 0:
        speedup_parallel = time3 / time2
        speedup_cache = time3 / time1
        print(f"🚀 Mejora con procesamiento paralelo: {speedup_parallel:.1f}x más rápido")
        print(f"💾 Mejora con caché (2da ejecución): {speedup_cache:.1f}x más rápido")
        print()
        print(f"Tiempo original:  {time3:.1f}s")
        print(f"Con paralelo:     {time2:.1f}s (ahorro: {time3-time2:.1f}s)")
        print(f"Con caché:        {time1:.1f}s (ahorro: {time3-time1:.1f}s)")
    print("=" * 70)

if __name__ == "__main__":
    test_analysis_speed()
