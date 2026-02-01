# main.py
from audio_analyzer import AudioAnalyzer
from playlist_generator import CyclingPlaylistGenerator
import pandas as pd

def main():
    # === CONFIGURACIÓN ===
    MUSIC_FOLDER = "./mis_canciones"  # 📁 Cambia esto a tu carpeta
    WORKOUT_DURATION = 60  # minutos
    WORKOUT_TYPE = "endurance"  # "endurance", "intervals", "recovery"
    
    print("=" * 60)
    print("🎵 CYCLING MUSIC MIXER 🚴")
    print("=" * 60)
    
    # === PASO 1: Analizar canciones ===
    print("\n📊 PASO 1: Analizando tus canciones...\n")
    
    analyzer = AudioAnalyzer(MUSIC_FOLDER)
    songs_df = analyzer.analyze_folder()
    
    if len(songs_df) == 0:
        print("\n❌ No se encontraron canciones para analizar.")
        print(f"   Verifica que la carpeta '{MUSIC_FOLDER}' contenga archivos MP3/WAV/FLAC")
        return None
    
    # Guarda análisis para no repetir
    songs_df.to_csv("song_analysis.csv", index=False)
    print("\n💾 Análisis guardado en 'song_analysis.csv'")
    
    # === PASO 2: Mostrar estadísticas ===
    print("\n📈 ESTADÍSTICAS DE TU BIBLIOTECA:")
    print("-" * 40)
    print(f"  Total canciones: {len(songs_df)}")
    print(f"  Duración total: {songs_df['duration'].sum()/60:.1f} minutos")
    print(f"  BPM promedio: {songs_df['bpm'].mean():.0f}")
    print(f"  BPM rango: {songs_df['bpm'].min():.0f} - {songs_df['bpm'].max():.0f}")
    print(f"  Energía promedio: {songs_df['energy'].mean():.2f}")
    
    # === PASO 3: Generar playlist ===
    print(f"\n🎯 PASO 2: Generando playlist para {WORKOUT_TYPE}...\n")
    
    generator = CyclingPlaylistGenerator(songs_df)
    playlist = generator.generate_workout_playlist(
        duration_minutes=WORKOUT_DURATION,
        workout_type=WORKOUT_TYPE
    )
    
    if len(playlist) == 0:
        print("\n❌ No se pudo generar la playlist.")
        return None
    
    # === PASO 4: Mostrar playlist ===
    print("🎵 PLAYLIST GENERADA:")
    print("=" * 60)
    
    for i, (_, song) in enumerate(playlist.iterrows(), 1):
        start_min = song['start_time'] / 60
        phase = song['phase'].upper()
        intensity = song['intensity_score']
        
        # Emoji según fase
        phase_emoji = {
            'warmup': '🔥',
            'build': '📈',
            'peak': '⚡',
            'sustain': '💪',
            'cooldown': '❄️'
        }.get(song['phase'], '🎵')
        
        # Barra de intensidad
        intensity_bar = '█' * int(intensity * 10) + '░' * (10 - int(intensity * 10))
        
        print(f"{i:2}. [{start_min:5.1f}min] {phase_emoji} {song['title'][:35]:35}")
        print(f"    BPM: {song['bpm']:3.0f} | Energía: [{intensity_bar}] | {phase}")
        print()
    
    total_duration = playlist['duration'].sum() / 60
    print("=" * 60)
    print(f"⏱️  Duración total: {total_duration:.1f} minutos")
    
    # === PASO 5: Guardar playlist ===
    playlist.to_csv("workout_playlist.csv", index=False)
    print("\n💾 Playlist guardada en 'workout_playlist.csv'")
    
    # === PASO 6: Generar archivo M3U (para reproductores) ===
    generate_m3u(playlist, "workout_playlist.m3u", MUSIC_FOLDER)
    print("💾 Archivo M3U guardado en 'workout_playlist.m3u'")
    
    print("\n✅ ¡Listo! Ejecuta 'python visualize.py' para ver gráficos")
    
    return playlist

def generate_m3u(playlist: pd.DataFrame, output_file: str, music_folder: str):
    """Genera archivo M3U para importar en reproductores"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for _, song in playlist.iterrows():
            duration = int(song['duration'])
            f.write(f"#EXTINF:{duration},{song['title']}\n")
            f.write(f"{music_folder}/{song['filename']}\n")

if __name__ == "__main__":
    playlist = main()
