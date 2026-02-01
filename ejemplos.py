#!/usr/bin/env python3
"""
🎵 Ejemplo de Uso Avanzado: Generación de Múltiples Playlists
"""

from audio_analyzer import AudioAnalyzer
from playlist_generator import CyclingPlaylistGenerator
import pandas as pd

def generar_todas_las_playlists():
    """Genera múltiples tipos de playlists de una vez"""
    
    print("🔍 Cargando análisis de canciones...")
    
    # Intenta cargar análisis previo
    try:
        songs_df = pd.read_csv("song_analysis.csv")
        print(f"✅ Cargadas {len(songs_df)} canciones desde cache")
    except FileNotFoundError:
        print("📊 No hay cache, analizando canciones...")
        analyzer = AudioAnalyzer("./mis_canciones")
        songs_df = analyzer.analyze_folder()
        songs_df.to_csv("song_analysis.csv", index=False)
    
    if len(songs_df) == 0:
        print("❌ No hay canciones para procesar")
        return
    
    generator = CyclingPlaylistGenerator(songs_df)
    
    # === 1. Workout de Resistencia (60 min) ===
    print("\n🏃 Generando: Endurance 60min...")
    playlist_endurance = generator.generate_workout_playlist(
        duration_minutes=60,
        workout_type="endurance"
    )
    playlist_endurance.to_csv("playlist_endurance_60min.csv", index=False)
    print(f"   ✅ {len(playlist_endurance)} canciones")
    
    # === 2. Intervalos HIIT (45 min) ===
    print("\n⚡ Generando: Intervals 45min...")
    playlist_intervals = generator.generate_workout_playlist(
        duration_minutes=45,
        workout_type="intervals"
    )
    playlist_intervals.to_csv("playlist_intervals_45min.csv", index=False)
    print(f"   ✅ {len(playlist_intervals)} canciones")
    
    # === 3. Recuperación (30 min) ===
    print("\n❄️  Generando: Recovery 30min...")
    playlist_recovery = generator.generate_workout_playlist(
        duration_minutes=30,
        workout_type="recovery"
    )
    playlist_recovery.to_csv("playlist_recovery_30min.csv", index=False)
    print(f"   ✅ {len(playlist_recovery)} canciones")
    
    # === 4. Por Cadencia Específica (90 RPM) ===
    print("\n🎯 Generando: Cadencia 90 RPM...")
    playlist_cadence = generator.order_by_bpm_for_cadence(
        target_cadence=90,
        tolerance=10
    )
    playlist_cadence.to_csv("playlist_cadence_90rpm.csv", index=False)
    print(f"   ✅ {len(playlist_cadence)} canciones")
    
    # === 5. Curva Personalizada ===
    print("\n🎨 Generando: Curva personalizada...")
    # Pirámide de energía
    curva_piramide = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3]
    playlist_custom = generator.generate_energy_curve_playlist(
        energy_curve=curva_piramide,
        duration_minutes=60
    )
    playlist_custom.to_csv("playlist_custom_piramide.csv", index=False)
    print(f"   ✅ {len(playlist_custom)} canciones")
    
    # === Resumen ===
    print("\n" + "="*60)
    print("📊 RESUMEN - Playlists Generadas:")
    print("="*60)
    print(f"  1. playlist_endurance_60min.csv     ({len(playlist_endurance)} canciones)")
    print(f"  2. playlist_intervals_45min.csv     ({len(playlist_intervals)} canciones)")
    print(f"  3. playlist_recovery_30min.csv      ({len(playlist_recovery)} canciones)")
    print(f"  4. playlist_cadence_90rpm.csv       ({len(playlist_cadence)} canciones)")
    print(f"  5. playlist_custom_piramide.csv     ({len(playlist_custom)} canciones)")
    print("="*60)
    print("\n✅ ¡Todas las playlists generadas exitosamente!")

def analizar_biblioteca():
    """Muestra estadísticas detalladas de tu biblioteca"""
    
    try:
        df = pd.read_csv("song_analysis.csv")
    except FileNotFoundError:
        print("❌ Ejecuta primero 'python main.py' para analizar tus canciones")
        return
    
    print("\n" + "="*60)
    print("📊 ANÁLISIS DETALLADO DE TU BIBLIOTECA")
    print("="*60)
    
    print(f"\n📁 Total de canciones: {len(df)}")
    print(f"⏱️  Duración total: {df['duration'].sum()/3600:.1f} horas")
    
    print("\n🎵 BPM:")
    print(f"   Promedio: {df['bpm'].mean():.0f}")
    print(f"   Rango: {df['bpm'].min():.0f} - {df['bpm'].max():.0f}")
    print(f"   Mediana: {df['bpm'].median():.0f}")
    
    print("\n⚡ Energía:")
    print(f"   Promedio: {df['energy'].mean():.2f}")
    print(f"   Rango: {df['energy'].min():.2f} - {df['energy'].max():.2f}")
    
    print("\n🎼 Top 5 canciones más energéticas:")
    top_energy = df.nlargest(5, 'energy')[['title', 'bpm', 'energy']]
    for i, (_, song) in enumerate(top_energy.iterrows(), 1):
        print(f"   {i}. {song['title'][:40]:40} | BPM: {song['bpm']:3.0f} | E: {song['energy']:.2f}")
    
    print("\n😌 Top 5 canciones más relajadas:")
    top_chill = df.nsmallest(5, 'energy')[['title', 'bpm', 'energy']]
    for i, (_, song) in enumerate(top_chill.iterrows(), 1):
        print(f"   {i}. {song['title'][:40]:40} | BPM: {song['bpm']:3.0f} | E: {song['energy']:.2f}")
    
    print("\n🎯 Distribución por rangos de BPM:")
    rangos = [
        (60, 90, "Muy lento"),
        (90, 110, "Lento"),
        (110, 130, "Moderado"),
        (130, 150, "Rápido"),
        (150, 200, "Muy rápido")
    ]
    for min_bpm, max_bpm, label in rangos:
        count = len(df[(df['bpm'] >= min_bpm) & (df['bpm'] < max_bpm)])
        pct = count / len(df) * 100
        bar = '█' * int(pct / 5)
        print(f"   {min_bpm:3d}-{max_bpm:3d} BPM ({label:12}): {bar:20} {count:3d} ({pct:5.1f}%)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        analizar_biblioteca()
    else:
        generar_todas_las_playlists()
        print("\n💡 Tip: Ejecuta 'python ejemplos.py stats' para ver estadísticas detalladas")
