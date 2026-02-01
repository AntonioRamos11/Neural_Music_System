#!/usr/bin/env python3
"""
Generador de Múltiples Playlists

Genera varias playlists simultáneamente usando las plantillas definidas.
"""

from audio_analyzer import AudioAnalyzer
from playlist_generator import CyclingPlaylistGenerator
from playlist_templates import CyclingPlaylistTemplates, PlaylistConfig
import pandas as pd
from pathlib import Path
from typing import List

def generate_m3u(playlist: pd.DataFrame, output_file: str):
    """Genera archivo M3U para importar en reproductores"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for _, song in playlist.iterrows():
            duration = int(song['duration'])
            f.write(f"#EXTINF:{duration},{song['title']}\n")
            f.write(f"{song['filepath']}\n")

def generate_playlist(
    songs_df: pd.DataFrame,
    config: PlaylistConfig,
    output_prefix: str = "playlists"
):
    """
    Genera una playlist según configuración
    
    Args:
        songs_df: DataFrame con canciones analizadas
        config: Configuración de la playlist
        output_prefix: Carpeta de salida
    """
    print(f"\n{'='*70}")
    print(f"🎵 Generando: {config.name} ({config.duration} min)")
    print(f"   {config.description}")
    print(f"{'='*70}")
    
    # Crear generador
    generator = CyclingPlaylistGenerator(songs_df)
    
    # Generar playlist (todos usan el mismo método)
    playlist = generator.generate_workout_playlist(
        duration_minutes=config.duration,
        workout_type=config.workout_type
    )
    
    if len(playlist) == 0:
        print("⚠️  No se pudo generar (canciones insuficientes)")
        return None
    
    # Nombres de archivo seguros
    safe_name = config.name.lower().replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    
    # Guardar CSV
    csv_file = f"csv/playlist_{safe_name}_{config.duration}min.csv"
    playlist.to_csv(csv_file, index=False)
    
    # Guardar M3U
    m3u_file = f"{output_prefix}/playlist_{safe_name}_{config.duration}min.m3u"
    generate_m3u(playlist, m3u_file)
    
    # Resumen
    total_duration = playlist['duration'].sum() / 60
    print(f"✅ {len(playlist)} canciones | {total_duration:.1f} min")
    print(f"   CSV: {csv_file}")
    print(f"   M3U: {m3u_file}")
    
    return playlist

def main():
    """Genera múltiples playlists"""
    
    # Configuración
    MUSIC_FOLDER = "/home/pwn/Music/Musica xioami/Music"
    
    # Crear directorios
    Path("csv").mkdir(exist_ok=True)
    Path("playlists").mkdir(exist_ok=True)
    
    print("="*70)
    print("🎵 GENERADOR DE MÚLTIPLES PLAYLISTS PARA CICLISMO")
    print("="*70)
    
    # Paso 1: Analizar canciones (usa caché automáticamente)
    print("\n📊 PASO 1: Cargando biblioteca musical...")
    
    analysis_file = "csv/song_analysis.csv"
    
    # Verificar si ya existe análisis
    if Path(analysis_file).exists():
        print(f"💾 Cargando análisis existente desde '{analysis_file}'...\n")
        songs_df = pd.read_csv(analysis_file)
        
        # Filtrar canciones sin filepath
        if 'filepath' in songs_df.columns:
            missing = songs_df['filepath'].isna().sum()
            if missing > 0:
                print(f"⚠️  {missing} canciones sin ruta (eliminadas)")
                songs_df = songs_df[songs_df['filepath'].notna()].copy()
        
        print(f"✅ {len(songs_df)} canciones disponibles")
    else:
        print("⚠️  No se encuentra análisis existente")
        print(f"   Ejecuta primero: python3 main.py")
        print(f"   O: python3 agregar_rutas.py")
        return
    
    if len(songs_df) == 0:
        print("\n❌ No hay canciones disponibles.")
        return
    
    # Paso 2: Seleccionar plantillas a generar
    print("\n" + "="*70)
    print("📋 PASO 2: Seleccionando playlists a generar...")
    print("="*70)
    
    # OPCIÓN A: Generar todas las playlists
    # templates = CyclingPlaylistTemplates.get_all_templates()
    
    # OPCIÓN B: Generar playlists seleccionadas (recomendado)
    templates = [
        # Por duración
        CyclingPlaylistTemplates.QUICK_SESSION,      # 30 min
        CyclingPlaylistTemplates.STANDARD_RIDE,      # 60 min
        CyclingPlaylistTemplates.LONG_RIDE,          # 90 min
        CyclingPlaylistTemplates.ULTRA_ENDURANCE,    # 120 min
        CyclingPlaylistTemplates.MARATHON,           # 180 min
        
        # Por intensidad
        CyclingPlaylistTemplates.RECOVERY,           # Suave
        CyclingPlaylistTemplates.INTERVALS,          # Intenso
        
        # Por estilo
        CyclingPlaylistTemplates.ROCK_POWER,         # Rock
        CyclingPlaylistTemplates.ELECTRONIC_DRIVE,   # Electrónica
        CyclingPlaylistTemplates.OLDIES_CLASSICS,    # Clásicos
        
        # Especializadas
        CyclingPlaylistTemplates.CLIMB_POWER,        # Subidas
        CyclingPlaylistTemplates.RACE_DAY,           # Carrera
    ]
    
    print(f"Generando {len(templates)} playlists:\n")
    for i, t in enumerate(templates, 1):
        print(f"  {i}. {t.name} ({t.duration} min)")
    
    # Paso 3: Generar todas las playlists
    print("\n" + "="*70)
    print("🎵 PASO 3: Generando playlists...")
    print("="*70)
    
    generated = 0
    failed = 0
    
    for template in templates:
        result = generate_playlist(songs_df, template)
        if result is not None:
            generated += 1
        else:
            failed += 1
    
    # Resumen final
    print("\n" + "="*70)
    print("📊 RESUMEN FINAL")
    print("="*70)
    print(f"✅ Playlists generadas: {generated}")
    if failed > 0:
        print(f"⚠️  Playlists fallidas: {failed}")
    print(f"\n📁 Archivos guardados en:")
    print(f"   - CSV: csv/playlist_*.csv")
    print(f"   - M3U: playlists/playlist_*.m3u")
    print("\n💡 Importa los archivos .m3u a tu reproductor favorito!")
    print("="*70)

if __name__ == "__main__":
    main()
