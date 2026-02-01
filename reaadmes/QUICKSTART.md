# 🚀 Quick Start Guide

## 📋 Instalación (5 minutos)

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

> **Nota**: Si tienes problemas con `librosa`, en Linux puede requerir:
> ```bash
> sudo apt-get install libsndfile1
> ```

### 2. Preparar tu música

Copia tus archivos MP3/WAV/FLAC a la carpeta `mis_canciones/`:

```bash
cp /ruta/a/tus/canciones/*.mp3 mis_canciones/
```

### 3. Ejecutar

```bash
python main.py
```

¡Listo! 🎉

---

## 🎯 Uso Básico

### Cambiar tipo de workout

Edita `main.py` línea 9:

```python
WORKOUT_TYPE = "endurance"  # Opciones: "endurance", "intervals", "recovery"
```

### Cambiar duración

Edita `main.py` línea 8:

```python
WORKOUT_DURATION = 60  # Cambiar a minutos deseados
```

### Ver gráficos

Después de ejecutar `main.py`:

```bash
python visualize.py
```

---

## 📊 Ejemplo Completo

```bash
# 1. Instalar
pip install -r requirements.txt

# 2. Copiar música
cp ~/Music/workout/*.mp3 mis_canciones/

# 3. Generar playlist
python main.py

# 4. Ver visualización
python visualize.py
```

**Archivos generados:**
- `song_analysis.csv` - Métricas de todas las canciones
- `workout_playlist.csv` - Playlist generada
- `workout_playlist.m3u` - Para importar en reproductores
- `playlist_visualization.png` - Gráficos

---

## 🔧 Personalización Avanzada

### Generar por cadencia específica

```python
from playlist_generator import CyclingPlaylistGenerator
import pandas as pd

songs_df = pd.read_csv("song_analysis.csv")
generator = CyclingPlaylistGenerator(songs_df)

# Playlist para mantener 90 RPM
playlist = generator.order_by_bpm_for_cadence(
    target_cadence=90,
    tolerance=10
)

playlist.to_csv("cadence_playlist.csv", index=False)
```

### Curva de energía personalizada

```python
# Define tu propia curva (0-1, donde 1 = máxima intensidad)
mi_curva = [0.3, 0.5, 0.7, 0.9, 0.9, 0.7, 0.5, 0.3]

playlist = generator.generate_energy_curve_playlist(
    energy_curve=mi_curva,
    duration_minutes=60
)
```

---

## 🐛 Problemas Comunes

### "No se encontraron canciones"

✅ Verifica:
- La carpeta `mis_canciones/` existe
- Contiene archivos `.mp3`, `.wav` o `.flac`
- Los nombres no tienen caracteres especiales extraños

### "Error al instalar librosa"

```bash
# En Linux/Ubuntu:
sudo apt-get install python3-dev libsndfile1

# En macOS:
brew install libsndfile

# Luego:
pip install librosa
```

### "No se puede mostrar el gráfico"

Esto es normal en servidores sin display. El archivo PNG se guarda igual:
```bash
ls -lh playlist_visualization.png
```

---

## ⚡ Tips

1. **Primera vez**: El análisis puede tardar 10-30 segundos por canción
2. **Re-usar análisis**: Si ya tienes `song_analysis.csv`, puedes generar múltiples playlists sin re-analizar
3. **Mejor calidad**: Usa archivos de al menos 128 kbps para mejor detección de BPM
4. **Probar diferentes tipos**: Genera 3 playlists (endurance, intervals, recovery) y elige tu favorita

---

**¿Más ayuda?** Lee el [README.md](README.md) completo
