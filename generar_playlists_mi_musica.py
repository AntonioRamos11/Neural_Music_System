#!/usr/bin/env python3
"""
🎵 Generador de Playlists para Mi Música

Analiza la música personal y genera playlists optimizadas para ciclismo.
"""

import sys
from pathlib import Path

# Añadir directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from audio_analyzer import AudioAnalyzer
from playlist_generator import CyclingPlaylistGenerator
import pandas as pd

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Imprime encabezado decorado"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")


def print_section(text: str):
    """Imprime sección"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'─'*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'─'*70}{Colors.END}\n")


def generate_m3u(playlist: pd.DataFrame, output_file: str, music_folder: str):
    """Genera archivo M3U para importar en reproductores"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for _, song in playlist.iterrows():
            duration = int(song['duration'])
            f.write(f"#EXTINF:{duration},{song['title']}\n")
            f.write(f"{music_folder}/{song['filename']}\n")


def main():
    """Main function"""
    
    # 🎯 CONFIGURACIÓN - Tu carpeta de música
    MUSIC_FOLDER = "/home/pwn/Music/Musica xioami/Music/bass english"
    
    # Verificar que existe
    music_path = Path(MUSIC_FOLDER)
    if not music_path.exists():
        print(f"{Colors.RED}❌ Error: No se encuentra la carpeta: {MUSIC_FOLDER}{Colors.END}")
        return 1
    
    print(f"""
{Colors.BOLD}{Colors.MAGENTA}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         🎵 GENERADOR DE PLAYLISTS - MI MÚSICA 🚴                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
{Colors.END}
    """)
    
    print(f"{Colors.CYAN}📁 Carpeta de música:{Colors.END}")
    print(f"   {MUSIC_FOLDER}\n")
    
    # === PASO 1: Analizar canciones ===
    print_section("🔬 PASO 1: Analizando tu Música")
    
    print(f"{Colors.YELLOW}⏳ Esto puede tomar algunos minutos dependiendo de la cantidad de archivos...{Colors.END}\n")
    
    analyzer = AudioAnalyzer(MUSIC_FOLDER)
    songs_df = analyzer.analyze_folder()
    
    if len(songs_df) == 0:
        print(f"{Colors.RED}❌ No se encontraron canciones para analizar{Colors.END}")
        return 1
    
    # Guardar análisis
    songs_df.to_csv("mi_musica_analisis.csv", index=False)
    print(f"\n{Colors.GREEN}✅ Análisis completado y guardado en 'mi_musica_analisis.csv'{Colors.END}")
    
    # === PASO 2: Mostrar estadísticas ===
    print_section("📊 ESTADÍSTICAS DE TU BIBLIOTECA")
    
    print(f"{Colors.BOLD}Total de canciones analizadas:{Colors.END} {len(songs_df)}")
    print(f"{Colors.BOLD}Duración total:{Colors.END} {songs_df['duration'].sum()/60:.1f} minutos ({songs_df['duration'].sum()/3600:.1f} horas)")
    print(f"\n{Colors.BOLD}BPM:{Colors.END}")
    print(f"  • Promedio: {songs_df['bpm'].mean():.0f}")
    print(f"  • Mínimo: {songs_df['bpm'].min():.0f}")
    print(f"  • Máximo: {songs_df['bpm'].max():.0f}")
    print(f"\n{Colors.BOLD}Energía:{Colors.END}")
    print(f"  • Promedio: {songs_df['energy'].mean():.2f}")
    print(f"  • Mínimo: {songs_df['energy'].min():.2f}")
    print(f"  • Máximo: {songs_df['energy'].max():.2f}")
    
    # Top 10 por energía
    print(f"\n{Colors.BOLD}{Colors.GREEN}🔥 Top 10 Canciones con Más Energía:{Colors.END}")
    top_energy = songs_df.nlargest(10, 'energy')
    for i, (_, song) in enumerate(top_energy.iterrows(), 1):
        print(f"  {i:2}. {song['title'][:50]:50} | BPM: {song['bpm']:3.0f} | 🔥 {song['energy']:.2f}")
    
    # === PASO 3: Generar Playlists ===
    print_section("🎯 PASO 2: Generando Playlists")
    
    generator = CyclingPlaylistGenerator(songs_df)
    
    # Tipos de workout disponibles
    workouts = [
        ("endurance", 60, "Entrenamiento de Resistencia (60 min)"),
        ("intervals", 45, "Intervalos de Alta Intensidad (45 min)"),
        ("recovery", 30, "Recuperación Activa (30 min)")
    ]
    
    print(f"{Colors.CYAN}Generando 3 tipos de playlist...{Colors.END}\n")
    
    for workout_type, duration, description in workouts:
        print(f"{Colors.YELLOW}⏳ Generando: {description}{Colors.END}")
        
        playlist = generator.generate_workout_playlist(
            duration_minutes=duration,
            workout_type=workout_type
        )
        
        # Guardar CSV
        csv_filename = f"playlist_{workout_type}_{duration}min.csv"
        playlist.to_csv(csv_filename, index=False)
        
        # Guardar M3U
        m3u_filename = f"playlist_{workout_type}_{duration}min.m3u"
        generate_m3u(playlist, m3u_filename, MUSIC_FOLDER)
        
        print(f"{Colors.GREEN}   ✅ {len(playlist)} canciones | {playlist['duration'].sum()/60:.1f} min{Colors.END}")
        print(f"      📄 CSV: {csv_filename}")
        print(f"      🎵 M3U: {m3u_filename}\n")
    
    # === PASO 4: Mostrar Preview de Playlist Principal ===
    print_section("🎵 PREVIEW: Playlist Endurance (60 min)")
    
    # Cargar la playlist endurance
    playlist = pd.read_csv("playlist_endurance_60min.csv")
    
    print(f"{Colors.BOLD}Duración total:{Colors.END} {playlist['duration'].sum()/60:.1f} minutos\n")
    
    # Mostrar primeras 15 canciones
    for i, (_, song) in enumerate(playlist.head(15).iterrows(), 1):
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
        
        print(f"{i:2}. [{start_min:5.1f}min] {phase_emoji} {song['title'][:40]:40}")
        print(f"    BPM: {song['bpm']:3.0f} | [{intensity_bar}] {phase:8}")
    
    if len(playlist) > 15:
        print(f"\n    ... y {len(playlist) - 15} canciones más\n")
    
    # === RESUMEN FINAL ===
    print_section("📋 RESUMEN")
    
    print(f"{Colors.GREEN}{Colors.BOLD}✅ COMPLETADO{Colors.END}\n")
    print(f"{Colors.BOLD}Archivos generados:{Colors.END}")
    print(f"  📊 mi_musica_analisis.csv - Análisis completo de tu música")
    print(f"  🎵 playlist_endurance_60min.csv/.m3u - Resistencia 60 min")
    print(f"  ⚡ playlist_intervals_45min.csv/.m3u - Intervalos 45 min")
    print(f"  ❄️  playlist_recovery_30min.csv/.m3u - Recuperación 30 min")
    
    print(f"\n{Colors.CYAN}{Colors.BOLD}💡 Cómo usar tus playlists:{Colors.END}")
    print(f"  1. Importa los archivos .m3u en tu reproductor favorito")
    print(f"  2. O usa los archivos .csv para análisis detallado")
    print(f"  3. ¡Disfruta tu entrenamiento con música optimizada! 🚴\n")
    
    print(f"{Colors.MAGENTA}╔══════════════════════════════════════════════════════════════════╗")
    print(f"║         🎉 PLAYLISTS GENERADAS EXITOSAMENTE 🎉                  ║")
    print(f"╚══════════════════════════════════════════════════════════════════╝{Colors.END}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
