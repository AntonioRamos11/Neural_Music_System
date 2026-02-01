# visualize.py
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def visualize_playlist(playlist: pd.DataFrame):
    """Visualiza la playlist generada"""
    
    if len(playlist) == 0:
        print("❌ No hay datos de playlist para visualizar")
        return
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    # Colores por fase
    phase_colors = {
        'warmup': '#FFB347',
        'build': '#87CEEB',
        'peak': '#FF6B6B',
        'sustain': '#98D8C8',
        'cooldown': '#B8B8D1'
    }
    
    colors = [phase_colors.get(p, '#CCCCCC') for p in playlist['phase']]
    x_positions = playlist['start_time'] / 60  # minutos
    
    # === Gráfico 1: BPM ===
    ax1 = axes[0]
    ax1.bar(x_positions, playlist['bpm'], 
            width=playlist['duration']/60, 
            color=colors, edgecolor='white', alpha=0.8)
    ax1.set_ylabel('BPM', fontsize=12)
    ax1.set_title('📊 Distribución de BPM en la Playlist', fontsize=14)
    ax1.axhline(y=playlist['bpm'].mean(), color='red', linestyle='--', 
                label=f'Promedio: {playlist["bpm"].mean():.0f}')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # === Gráfico 2: Intensidad ===
    ax2 = axes[1]
    ax2.bar(x_positions, playlist['intensity_score'], 
            width=playlist['duration']/60,
            color=colors, edgecolor='white', alpha=0.8)
    ax2.set_ylabel('Intensidad', fontsize=12)
    ax2.set_title('⚡ Curva de Intensidad', fontsize=14)
    ax2.set_ylim(0, 1)
    ax2.grid(axis='y', alpha=0.3)
    
    # Añade línea de tendencia
    try:
        from scipy.interpolate import interp1d
        x_smooth = np.linspace(0, x_positions.max(), 100)
        x_centers = x_positions + playlist['duration']/120
        f = interp1d(x_centers, playlist['intensity_score'], 
                     kind='quadratic', fill_value='extrapolate')
        ax2.plot(x_smooth, np.clip(f(x_smooth), 0, 1), 
                 'r-', linewidth=2, label='Tendencia')
        ax2.legend()
    except:
        # Si scipy no está disponible, continuar sin tendencia
        pass
    
    # === Gráfico 3: Timeline con nombres ===
    ax3 = axes[2]
    
    for i, (_, song) in enumerate(playlist.iterrows()):
        start = song['start_time'] / 60
        duration = song['duration'] / 60
        color = phase_colors.get(song['phase'], '#CCCCCC')
        
        ax3.barh(0, duration, left=start, height=0.5, 
                color=color, edgecolor='white')
        
        # Nombre de canción (rotado si no cabe)
        if duration > 2:
            ax3.text(start + duration/2, 0, song['title'][:20], 
                    ha='center', va='center', fontsize=8, rotation=45)
    
    ax3.set_xlim(0, playlist['cumulative_time'].max()/60)
    ax3.set_ylim(-0.5, 0.5)
    ax3.set_xlabel('Tiempo (minutos)', fontsize=12)
    ax3.set_title('🎵 Timeline de Canciones', fontsize=14)
    ax3.set_yticks([])
    
    # Leyenda de fases
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=c, label=p.capitalize()) 
                      for p, c in phase_colors.items()]
    ax3.legend(handles=legend_elements, loc='upper right', ncol=5)
    
    plt.tight_layout()
    plt.savefig('playlist_visualization.png', dpi=150, bbox_inches='tight')
    print("\n📊 Visualización guardada en 'playlist_visualization.png'")
    
    try:
        plt.show()
    except:
        print("   (Ejecución sin display gráfico)")

def main():
    """Función principal para visualizar"""
    try:
        playlist = pd.read_csv("workout_playlist.csv")
        print("🔍 Cargando playlist desde 'workout_playlist.csv'...")
        print(f"   Encontradas {len(playlist)} canciones")
        visualize_playlist(playlist)
    except FileNotFoundError:
        print("❌ Error: No se encontró 'workout_playlist.csv'")
        print("   Ejecuta primero 'python main.py' para generar la playlist")
    except Exception as e:
        print(f"❌ Error al visualizar: {e}")

if __name__ == "__main__":
    main()
