# 🎵 Cycling Music Mixer - Información del Proyecto

## 📂 Estructura del Proyecto

```
music_system/
│
├── 📄 README.md                      # Documentación completa
├── 📄 QUICKSTART.md                  # Guía de inicio rápido
├── 📄 requirements.txt               # Dependencias Python
├── 📄 .gitignore                     # Archivos ignorados por git
│
├── 🎵 SCRIPTS PRINCIPALES
│   ├── audio_analyzer.py             # Extrae features de audio
│   ├── playlist_generator.py         # Genera playlists optimizadas
│   ├── main.py                       # Script principal
│   ├── visualize.py                  # Visualización gráfica
│   └── ejemplos.py                   # Ejemplos de uso avanzado
│
├── 🛠️ UTILIDADES
│   ├── generar_audio_prueba.py       # Genera audio sintético para testing
│   └── comandos.sh                   # Script con comandos útiles
│
├── 📁 CARPETAS
│   └── mis_canciones/                # Aquí van tus MP3/WAV/FLAC
│       └── README.txt
│
└── 📊 ARCHIVOS GENERADOS (creados al ejecutar)
    ├── song_analysis.csv             # Análisis de canciones
    ├── workout_playlist.csv          # Playlist generada
    ├── workout_playlist.m3u          # Playlist para reproductores
    └── playlist_visualization.png    # Gráficos
```

## 🔬 Módulos Principales

### 1. audio_analyzer.py
**Propósito**: Extrae características musicales de archivos de audio

**Clases**:
- `SongFeatures`: Dataclass con todas las métricas de una canción
- `AudioAnalyzer`: Analiza carpetas completas de música

**Features extraídas**:
- BPM (tempo)
- Beat strength (claridad del ritmo)
- Energy (intensidad)
- Brightness (frecuencias altas)
- Spectral contrast
- Dynamic range
- Onset rate (complejidad rítmica)

**Uso**:
```python
analyzer = AudioAnalyzer("./mis_canciones")
songs_df = analyzer.analyze_folder()
```

### 2. playlist_generator.py
**Propósito**: Genera playlists optimizadas según objetivos

**Clases**:
- `WorkoutPhase`: Enum con fases (WARMUP, BUILD, PEAK, SUSTAIN, COOLDOWN)
- `CyclingPlaylistGenerator`: Generador principal

**Métodos principales**:
- `generate_workout_playlist()`: Genera según tipo de workout
- `generate_energy_curve_playlist()`: Sigue curva personalizada
- `order_by_bpm_for_cadence()`: Ordena por cadencia objetivo

**Uso**:
```python
generator = CyclingPlaylistGenerator(songs_df)
playlist = generator.generate_workout_playlist(
    duration_minutes=60,
    workout_type="endurance"
)
```

### 3. main.py
**Propósito**: Orquesta todo el proceso

**Flujo**:
1. Analiza canciones en carpeta
2. Calcula estadísticas
3. Genera playlist según configuración
4. Guarda CSV y M3U
5. Muestra resultado en consola

### 4. visualize.py
**Propósito**: Crea visualizaciones gráficas

**Gráficos**:
- Distribución de BPM a lo largo del tiempo
- Curva de intensidad
- Timeline con nombres de canciones

## ⚙️ Configuración

### Variables principales en main.py

```python
MUSIC_FOLDER = "./mis_canciones"     # Carpeta con música
WORKOUT_DURATION = 60                # Minutos
WORKOUT_TYPE = "endurance"           # Tipo de workout
```

### Tipos de workout disponibles

| Tipo | Estructura | Uso ideal |
|------|-----------|-----------|
| `endurance` | Warmup → Build → Sustain → Cooldown | Rodadas largas, base |
| `intervals` | Warmup → [Peak/Recovery]×4 → Cooldown | HIIT, entrenamientos intervalados |
| `recovery` | Warmup → Sustain suave → Cooldown | Recuperación activa |

## 🧮 Algoritmos de Scoring

### Intensity Score
```python
intensity = (
    energy * 0.35 +          # Peso mayor a energía
    bpm_norm * 0.25 +        # Tempo influye
    beat_strength * 0.20 +   # Claridad del ritmo
    onset_rate * 0.20        # Complejidad
)
```

### Warmup Score
```python
warmup = 1 - abs(intensity - 0.4)  # Busca intensidad media-baja
```

### Cooldown Score
```python
cooldown = 1 - intensity  # Busca intensidad baja
```

### Motivation Score
```python
motivation = (
    beat_strength * 0.4 +    # Beat claro es clave
    energy * 0.4 +           # Energía alta
    brightness * 0.2         # Sonidos brillantes motivan
)
```

## 📊 Formatos de Salida

### song_analysis.csv
Columnas:
- `filename`: Nombre del archivo
- `title`: Título limpio
- `duration`: Duración en segundos
- `bpm`: Beats por minuto
- `beat_strength`: 0-1
- `energy`: 0-1
- `energy_variance`: Variación de energía
- `brightness`: 0-1
- `contrast`: Contraste espectral
- `dynamic_range`: Rango dinámico
- `onset_rate`: Golpes por segundo

### workout_playlist.csv
Columnas adicionales a song_analysis:
- `phase`: Fase del workout (warmup, build, peak, sustain, cooldown)
- `intensity_score`: Score de intensidad calculado
- `start_time`: Tiempo de inicio en segundos
- `cumulative_time`: Tiempo acumulado

### workout_playlist.m3u
Formato estándar M3U:
```
#EXTM3U
#EXTINF:180,Nombre Canción
./mis_canciones/cancion.mp3
...
```

## 🔧 Dependencias

| Librería | Versión | Uso |
|----------|---------|-----|
| librosa | >=0.10.0 | Análisis de audio |
| numpy | >=1.24.0 | Operaciones numéricas |
| pandas | >=2.0.0 | Manipulación de datos |
| matplotlib | >=3.7.0 | Visualización |
| scipy | >=1.11.0 | Procesamiento de señales |
| scikit-learn | >=1.3.0 | Normalización |
| seaborn | >=0.12.0 | Estética de gráficos |

## 🎓 Conceptos Técnicos

### BPM (Beats Per Minute)
Detectado usando `librosa.beat.beat_track()`:
- Analiza el onset envelope
- Encuentra periodicidad en los beats
- Retorna tempo y posiciones de beats

### RMS Energy
Root Mean Square de la amplitud:
```python
rms = librosa.feature.rms(y=y)
energy = np.mean(rms)
```

### Spectral Centroid (Brightness)
Centro de masa del espectro:
- Valores altos = sonidos brillantes (hi-hats, cymbals)
- Valores bajos = sonidos oscuros (bass, kicks)

### Onset Rate
Cantidad de eventos/golpes por segundo:
```python
onsets = librosa.onset.onset_detect(y=y, sr=sr)
onset_rate = len(onsets) / duration
```

## 📝 Notas de Implementación

### Performance
- Análisis: ~10-30 segundos por canción (3-5 minutos)
- Generación de playlist: <1 segundo
- Visualización: 1-2 segundos

### Limitaciones
- Archivos muy cortos (<30 seg) pueden dar resultados inexactos
- BPM muy variables (tempo rubato) puede confundir detector
- Archivos corruptos o con metadata extraña pueden fallar

### Optimizaciones Futuras
- [ ] Cache de análisis por hash de archivo
- [ ] Análisis paralelo de múltiples canciones
- [ ] Detección de género musical
- [ ] Integración con Spotify/Apple Music API
- [ ] Exportar a GPX con zonas de potencia

## 🤝 Cómo Contribuir

Ideas para mejorar:
1. Añadir más tipos de workout (HIIT, Sprint, Tempo)
2. Crear interfaz web con Streamlit/Flask
3. Integrar con sensores de potencia/cadencia
4. Añadir detección de drops/builds
5. Exportar a formato Zwift

## 📧 Contacto y Soporte

Para reportar bugs o sugerir mejoras:
- Crea un Issue en GitHub
- Envía un Pull Request
- Comparte tus playlists generadas

---

**Última actualización**: Enero 2026
**Versión**: 1.0.0
**Licencia**: MIT (libre para uso personal y comercial)
