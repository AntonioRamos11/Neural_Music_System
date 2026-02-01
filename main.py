# main.py
from audio_analyzer import AudioAnalyzer
from playlist_generator import CyclingPlaylistGenerator
import pandas as pd
from pathlib import Path
#/home/pwn/Music/Musica xioami/Music
def main():
    # === CONFIGURACIÓN ===
    MUSIC_FOLDER = "/home/pwn/Music/Musica xioami/Music"  # 📁 Cambia esto a tu carpeta
    WORKOUT_DURATION = 60  # minutos
    WORKOUT_TYPE = "endurance"  # "endurance", "intervals", "recovery"
    
    # Crear directorios si no existen
    Path("csv").mkdir(exist_ok=True)
    Path("playlists").mkdir(exist_ok=True)
    
    print("=" * 60)
    print("🎵 CYCLING MUSIC MIXER 🚴")
    print("=" * 60)
    
    # === PASO 1: Analizar canciones ===
    print("\n📊 PASO 1: Analizando tus canciones...\n")
    
    analysis_file = "csv/song_analysis.csv"
    
    # Verificar si ya existe análisis
    if Path(analysis_file).exists():
        print(f"💾 Cargando análisis existente desde '{analysis_file}'...")
        songs_df = pd.read_csv(analysis_file)
        print(f"✅ {len(songs_df)} canciones cargadas\n")
        
        # Verificar que tenga la columna filepath
        if 'filepath' not in songs_df.columns:
            print("⚠️  El análisis no tiene rutas completas")
            print("   Ejecuta: python3 agregar_rutas.py")
            return None
        
        # Filtrar canciones sin filepath
        missing = songs_df['filepath'].isna().sum()
        if missing > 0:
            print(f"⚠️  {missing} canciones sin ruta (eliminadas)")
            songs_df = songs_df[songs_df['filepath'].notna()].copy()
            print(f"✅ {len(songs_df)} canciones disponibles\n")
    else:
        print("⚡ Usando procesamiento paralelo + caché para máxima velocidad\n")
        
        # El nuevo AudioAnalyzer usa caché y procesamiento paralelo automáticamente
        analyzer = AudioAnalyzer(MUSIC_FOLDER, cache_file="csv/audio_cache.json")
        songs_df = analyzer.analyze_folder()
        
        if len(songs_df) == 0:
            print("\n❌ No se encontraron canciones para analizar.")
            print(f"   Verifica que la carpeta '{MUSIC_FOLDER}' contenga archivos MP3/WAV/FLAC")
            return None
        
        # Guarda análisis en carpeta csv/
        songs_df.to_csv(analysis_file, index=False)
        print(f"\n💾 Análisis guardado en '{analysis_file}'")
    
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
    playlist_csv = f"csv/playlist_{WORKOUT_TYPE}_{WORKOUT_DURATION}min.csv"
    playlist.to_csv(playlist_csv, index=False)
    print(f"\n💾 Playlist CSV guardada en '{playlist_csv}'")
    
    # === PASO 6: Generar archivo M3U (para reproductores) ===
    playlist_m3u = f"playlists/playlist_{WORKOUT_TYPE}_{WORKOUT_DURATION}min.m3u"
    generate_m3u(playlist, playlist_m3u, MUSIC_FOLDER)
    print(f"💾 Archivo M3U guardado en '{playlist_m3u}'")
    
    print("\n✅ ¡Listo! Ejecuta 'python visualize.py' para ver gráficos")
    
    return playlist

def generate_m3u(playlist: pd.DataFrame, output_file: str, music_folder: str):
    """Genera archivo M3U para importar en reproductores"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for _, song in playlist.iterrows():
            duration = int(song['duration'])
            f.write(f"#EXTINF:{duration},{song['title']}\n")
            # Usar filepath (ruta completa) en lugar de music_folder + filename
            f.write(f"{song['filepath']}\n")

if __name__ == "__main__":
    playlist = main()
