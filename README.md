# 🎵 Mixer Automático de Canciones por Métricas para Ciclismo 🚴

Sistema inteligente que analiza tus archivos MP3 y genera playlists optimizadas automáticamente para entrenamientos de ciclismo.

/home/pwn/Music/Musica xioami/Music/bass english
Path_musica  =  /home/pwn/Music/Musica xioami/Music
## 🎯 ¿Qué hace?

```
📁 Tus MP3s → 🔬 Extraer métricas → 🤖 Modelo de ordenamiento → 🎵 Playlist optimizada
```

- **Analiza** automáticamente tus canciones (BPM, energía, ritmo, etc.)
- **Genera** playlists estructuradas para diferentes tipos de workout
- **Optimiza** el orden según intensidad, cadencia y fases de entrenamiento
- **Visualiza** gráficamente la curva de intensidad y BPM

## 🚀 Instalación Rápida

### 1. Instalar dependencias                                                

```bash
pip install -r requirements.txt
```

### 2. Preparar tus canciones

Crea una carpeta con tus archivos de audio:

```
📁 mis_canciones/
   ├── cancion1.mp3
   ├── cancion2.mp3
   ├── cancion3.mp3
   └── ...
```

Formatos soportados: `.mp3`, `.wav`, `.flac`

### 3. Ejecutar

```bash
python main.py
```

## 📊 Features Extraídas

El sistema analiza automáticamente:

| Feature | Descripción | Uso |
|---------|-------------|-----|
| **BPM** | Tempo de la canción | Sincronizar con cadencia de pedaleo |
| **Energy** | Intensidad general | Determinar fases del workout |
| **Beat Strength** | Claridad del ritmo | Mantener cadencia constante |
| **Brightness** | Frecuencias altas | Canciones "brillantes" = más motivación |
| **Onset Rate** | Golpes por segundo | Complejidad rítmica |
| **Dynamic Range** | Variación de volumen | Evitar canciones muy variables |
| **Spectral Contrast** | Diferencia entre picos y valles | Textura musical |

## 🏋️ Tipos de Workout

### Endurance (Resistencia)
```python
workout_type = "endurance"
```
- 🔥 Warmup (10%)
- 📈 Build (20%)
- 💪 Sustain (50%)
- ❄️ Cooldown (20%)

### Intervals (Intervalos)
```python
workout_type = "intervals"
```
- 🔥 Warmup (15%)
- ⚡ [Peak → Recovery] × 4 (70%)
- ❄️ Cooldown (15%)

### Recovery (Recuperación)
```python
workout_type = "recovery"
```
- 🔥 Warmup (20%)
- 💪 Sustain (60%)
- ❄️ Cooldown (20%)

## 🎛️ Configuración

Edita las variables en `main.py`:

```python
# === CONFIGURACIÓN ===
MUSIC_FOLDER = "./mis_canciones"      # 📁 Carpeta con tus MP3s
WORKOUT_DURATION = 60                 # ⏱️ Minutos
WORKOUT_TYPE = "endurance"            # 🏋️ Tipo de workout
```

## 📈 Ejemplo de Uso

```bash
$ python main.py

============================================================
🎵 CYCLING MUSIC MIXER 🚴
============================================================

📊 PASO 1: Analizando tus canciones...

🔍 Buscando MP3s en: ./mis_canciones
📁 Encontrados: 25 archivos

  Analizando: song1.mp3...
  Analizando: song2.mp3...
  ...

✅ Analizadas: 25 canciones

📈 ESTADÍSTICAS DE TU BIBLIOTECA:
----------------------------------------
  Total canciones: 25
  Duración total: 95.3 minutos
  BPM promedio: 128
  BPM rango: 95 - 175
  Energía promedio: 0.68

🎯 PASO 2: Generando playlist para endurance...

🎵 PLAYLIST GENERADA:
============================================================
 1. [ 0.0min] 🔥 Chill Intro Song                          
    BPM: 95  | Energía: [███░░░░░░░] | WARMUP

 2. [ 3.5min] 📈 Building Energy                           
    BPM: 110 | Energía: [█████░░░░░] | BUILD

 3. [ 7.2min] 💪 High Power Track                          
    BPM: 128 | Energía: [████████░░] | SUSTAIN
...
```

## 📊 Visualización

Genera gráficos automáticamente:

```bash
python visualize.py
```

Crea:
- 📊 Distribución de BPM a lo largo del tiempo
- ⚡ Curva de intensidad
- 🎵 Timeline con nombres de canciones

## 📁 Archivos Generados

Después de ejecutar, tendrás:

```
📁 music_system/
   ├── song_analysis.csv          # Análisis de todas las canciones
   ├── workout_playlist.csv       # Playlist generada
   ├── workout_playlist.m3u       # Para importar en reproductores
   └── playlist_visualization.png # Gráficos
```

### Importar en Reproductores

El archivo `.m3u` puede importarse en:
- VLC Media Player
- Windows Media Player
- iTunes / Apple Music
- Foobar2000
- Winamp

## 🔧 Uso Avanzado

### 1. Generar por Cadencia Específica

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
```

### 2. Curva de Energía Personalizada

```python
# Energía personalizada: Arranque lento → Pico → Descenso
energy_curve = [0.3, 0.5, 0.7, 0.9, 0.9, 0.7, 0.5, 0.3]

playlist = generator.generate_energy_curve_playlist(
    energy_curve=energy_curve,
    duration_minutes=60
)
```

### 3. Re-analizar Sin Procesar Todo

Si ya tienes `song_analysis.csv`, puedes saltarte el análisis:

```python
import pandas as pd
from playlist_generator import CyclingPlaylistGenerator

# Carga análisis previo
songs_df = pd.read_csv("song_analysis.csv")

# Genera nueva playlist
generator = CyclingPlaylistGenerator(songs_df)
playlist = generator.generate_workout_playlist(
    duration_minutes=45,
    workout_type="intervals"
)
```

## 🎓 Cómo Funciona

### 1. Extracción de Features (Librosa)

```python
# Carga audio
y, sr = librosa.load(filepath, sr=22050)

# Detecta BPM y beats
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

# Energía RMS
rms = librosa.feature.rms(y=y)

# Spectral features
centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
```

### 2. Scoring de Intensidad

```python
intensity_score = (
    energy_norm * 0.35 +      # Energía general
    bpm_norm * 0.25 +          # Tempo
    beat_strength * 0.20 +     # Claridad del ritmo
    onset_rate_norm * 0.20     # Complejidad
)
```

### 3. Selección de Canciones

Para cada fase del workout:
1. Filtra canciones no usadas
2. Calcula score según objetivo de la fase
3. Ordena por score
4. Selecciona hasta llenar duración

## 🐛 Troubleshooting

### Error: `librosa` no se instala

```bash
# En Linux, puede requerir dependencias del sistema
sudo apt-get install libsndfile1

# Luego instala librosa
pip install librosa
```

### Error: No encuentra canciones

Verifica que:
- La carpeta `./mis_canciones` existe
- Tiene archivos `.mp3`, `.wav` o `.flac`
- Los archivos no están corruptos

```python
# En main.py, cambia la ruta:
MUSIC_FOLDER = "/ruta/completa/a/tus/canciones"
```

### Canciones analizadas incorrectamente

Algunos MP3s pueden tener metadata que confunde el análisis:
- Usa archivos de buena calidad (>128 kbps)
- Evita archivos con silencios largos al inicio/final

## 📝 Requisitos del Sistema

- **Python**: 3.8 o superior
- **RAM**: Mínimo 2GB (4GB recomendado)
- **Espacio**: ~500MB para librerías

## � Tests

El proyecto incluye una suite completa de pruebas:

```bash
# Ejecutar todos los tests
python test/run_all.py

# Tests rápidos
python test/run_all.py --fast

# Con cobertura de código
python test/run_all.py --coverage

# Tests unitarios solamente
python test/run_all.py --unit
```

**Estructura de tests:**
- ✅ **87 tests unitarios** - Componentes individuales
- ✅ **15 tests de integración** - Flujo completo
- ✅ **25 tests de validación** - Calidad de datos

Ver [TESTING.md](TESTING.md) y [test/README.md](test/README.md) para más detalles.

## �🤝 Contribuir

Ideas para mejorar:

- [ ] Integración con Spotify API
- [ ] Interfaz gráfica con Streamlit
- [ ] Más tipos de workout (HIIT, Sprint, etc.)
- [ ] Exportar a GPX con zonas de frecuencia cardíaca
- [ ] Detección automática de género musical

## 📜 Licencia

Código libre para uso personal. Si usas este proyecto, ¡comparte tus playlists! 🎵

## 🙏 Agradecimientos

Basado en:
- [Librosa](https://librosa.org/) - Análisis de audio
- Investigación en Music Information Retrieval (MIR)

---

**¡A rodar! 🚴💨**
# Neural_Music_System
