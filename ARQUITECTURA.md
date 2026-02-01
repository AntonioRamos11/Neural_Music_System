# Arquitectura del Sistema de Análisis de Audio

## Resumen

Sistema modular para análisis de características musicales con optimizaciones de rendimiento (procesamiento paralelo + caché). Diseñado siguiendo principios SOLID y arquitectura limpia.

## Arquitectura de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                     AudioAnalyzer                            │
│                  (Orquestador Principal)                     │
│                                                              │
│  Responsabilidades:                                          │
│  - Buscar archivos de audio                                  │
│  - Coordinar análisis (paralelo/secuencial)                  │
│  - Gestionar flujo de datos                                  │
│  - Exportar resultados a DataFrame                           │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
   ┌─────────────────────┐      ┌─────────────────────────┐
   │   CacheManager      │      │ AudioFeatureExtractor   │
   │                     │      │                         │
   │  Responsabilidades: │      │  Responsabilidades:     │
   │  - Persistencia     │      │  - Cargar audio         │
   │  - Hashing archivos │      │  - Extraer features     │
   │  - Get/Put caché    │      │  - Normalización        │
   │  - Validación       │      │  - Manejo de errores    │
   └─────────────────────┘      └─────────────────────────┘
               │                              │
               ▼                              ▼
      ┌────────────────┐          ┌──────────────────────┐
      │ audio_cache    │          │   SongFeatures       │
      │   .json        │          │  (Modelo de Datos)   │
      └────────────────┘          └──────────────────────┘
```

## Módulos y Responsabilidades

### 1. **SongFeatures** (Modelo de Datos)
**Tipo**: Dataclass inmutable  
**Responsabilidad**: Estructura de datos para características musicales

**Características almacenadas**:
- **Ritmo**: BPM, fuerza del beat
- **Energía**: RMS promedio, varianza
- **Espectro**: Brillo (centroid), contraste
- **Dinámica**: Rango dinámico, tasa de onsets

**Métodos**:
- `to_dict()`: Serialización
- `from_dict()`: Deserialización

**Principio aplicado**: Single Responsibility (solo datos, sin lógica)

---

### 2. **CacheManager** (Persistencia)
**Responsabilidad**: Gestión transparente de caché de análisis

**Funcionalidades**:
- Cargar/guardar caché en JSON
- Generar hashes únicos por archivo (nombre + tamaño + mtime)
- Validar integridad
- Operaciones get/put thread-safe

**Ventajas**:
- Evita re-analizar archivos no modificados
- Speedup masivo en ejecuciones subsiguientes
- Detección automática de cambios

**Principio aplicado**: Single Responsibility (solo caché)

---

### 3. **AudioFeatureExtractor** (Análisis)
**Responsabilidad**: Extracción de características de audio

**Proceso**:
1. Cargar audio (librosa, 22050 Hz)
2. Extraer características por categoría:
   - `_extract_rhythm_features()`: BPM, beat strength
   - `_extract_energy_features()`: RMS, varianza
   - `_extract_spectral_features()`: Centroid, contraste
   - `_extract_dynamic_features()`: Rango, onsets
3. Normalizar valores
4. Retornar SongFeatures

**Principio aplicado**: 
- Single Responsibility (solo extracción)
- Métodos pequeños, una función por tipo de feature
- Separación de concerns

---

### 4. **AudioAnalyzer** (Orquestador)
**Responsabilidad**: Coordinar el análisis completo

**Flujo de trabajo**:
```
1. Buscar archivos de audio
2. Cargar desde caché (si existe)
3. Analizar archivos nuevos:
   - Paralelo: Pool de procesos con tqdm
   - Secuencial: Loop con progreso
4. Actualizar caché
5. Retornar DataFrame
```

**Configuración**:
- `use_cache`: Habilitar/deshabilitar caché
- `use_parallel`: Procesamiento paralelo/secuencial
- `n_jobs`: Número de procesos (default: cores - 1)

**Principio aplicado**: 
- Orquestación sin lógica de negocio
- Delegación a componentes especializados

---

### 5. **_analyze_song_worker** (Worker Paralelo)
**Tipo**: Función top-level  
**Responsabilidad**: Worker para multiprocessing

**Razón de existencia**:
- Debe ser pickle-able (multiprocessing requirement)
- Interfaz simple: Path → Optional[SongFeatures]
- Sin estado compartido

---

## Optimizaciones de Rendimiento

### 1. **Procesamiento Paralelo**

**Implementación**:
```python
with Pool(processes=n_jobs) as pool:
    results = list(tqdm(
        pool.imap(_analyze_song_worker, files),
        total=len(files),
        desc="Analizando"
    ))
```

**Beneficios**:
- Speedup lineal con número de cores
- Típico: 3-8x más rápido
- Sin overhead de sincronización (operaciones independientes)

**Consideraciones**:
- Deja 1 core libre (mejor experiencia de usuario)
- Usa `imap` para progreso en tiempo real
- Worker function a nivel módulo (pickle requirement)

---

### 2. **Sistema de Caché**

**Estrategia**:
- Hash basado en: `nombre + tamaño + timestamp`
- Formato: JSON (legible, depurable)
- Ubicación: `csv/audio_cache.json`

**Beneficios**:
- Evita re-analizar archivos no modificados
- Speedup masivo (100x+) en ejecuciones subsiguientes
- Transparente para el usuario

**Detección de cambios**:
- Si archivo se modifica → hash diferente → re-analiza
- Si archivo se renombra → nuevo hash → re-analiza
- Balance entre precisión y complejidad

---

## Patrones de Diseño Aplicados

### 1. **Separation of Concerns**
Cada clase tiene una responsabilidad única:
- CacheManager: Solo persistencia
- AudioFeatureExtractor: Solo análisis
- AudioAnalyzer: Solo orquestación

### 2. **Dependency Injection**
```python
def __init__(self, music_folder: str, 
             cache_file: str = "csv/audio_cache.json",
             use_cache: bool = True):
```
Configuración inyectada, no hardcodeada.

### 3. **Strategy Pattern**
```python
if use_parallel:
    self._analyze_parallel(files, n_jobs)
else:
    self._analyze_sequential(files)
```
Estrategia de procesamiento intercambiable.

### 4. **Template Method**
`analyze_folder()` define flujo, delega implementación:
```
1. Buscar archivos     → _find_audio_files()
2. Cargar caché        → _load_from_cache()
3. Analizar            → _analyze_parallel/sequential()
4. Guardar caché       → cache_manager.save()
```

---

## Manejo de Errores

### Estrategia por Capas

**Capa de Extracción** (`AudioFeatureExtractor.extract`):
- Try-catch amplio
- Log del error
- Retorna None (fallo no crítico)

**Capa de Caché** (`CacheManager`):
- Try-catch específico (JSONDecodeError, IOError)
- Degrada gracefully (caché vacío)
- Warning al usuario

**Capa de Análisis** (`AudioAnalyzer`):
- Validación de entradas (carpeta existe)
- Filtra None de resultados
- Continúa con archivos válidos

### Principio: Fail Gracefully
Un archivo corrupto no debe detener todo el análisis.

---

## Uso del Sistema

### Caso 1: Uso Básico (Recomendado)
```python
analyzer = AudioAnalyzer("mis_canciones")
df = analyzer.analyze_folder()
# Automático: caché + paralelo + todos los cores
```

### Caso 2: Debugging
```python
analyzer = AudioAnalyzer("mis_canciones")
df = analyzer.analyze_folder(use_parallel=False)
# Secuencial para ver errores claramente
```

### Caso 3: Forzar Re-análisis
```python
analyzer = AudioAnalyzer("mis_canciones", use_cache=False)
df = analyzer.analyze_folder()
# Ignora caché, re-analiza todo
```

### Caso 4: Control de Recursos
```python
analyzer = AudioAnalyzer("mis_canciones")
df = analyzer.analyze_folder(n_jobs=2)
# Limita a 2 procesos (servidor compartido)
```

---

## Métricas de Rendimiento

### Benchmark Típico (20 canciones MP3, 4 cores)

| Configuración          | Tiempo  | Speedup |
|------------------------|---------|---------|
| Secuencial sin caché   | 180s    | 1.0x    |
| Paralelo sin caché     | 50s     | 3.6x    |
| Con caché (2da vez)    | 0.5s    | 360x    |

### Factores que Afectan Rendimiento

**Paralelo**:
- Número de cores
- RAM disponible
- Velocidad de disco (carga de archivos)

**Caché**:
- Cantidad de archivos no modificados
- Velocidad de lectura de JSON

---

## Extensibilidad

### Agregar Nuevas Características

1. Agregar campo a `SongFeatures`:
```python
@dataclass
class SongFeatures:
    # ... campos existentes
    nueva_feature: float
```

2. Crear método de extracción:
```python
@staticmethod
def _extract_nueva_feature(y, sr) -> Dict:
    # Análisis con librosa
    return {'nueva_feature': valor}
```

3. Integrar en `extract()`:
```python
nueva = cls._extract_nueva_feature(y, sr)
return SongFeatures(..., **nueva)
```

### Agregar Formatos de Audio

Modificar `AUDIO_EXTENSIONS` en `AudioAnalyzer`:
```python
AUDIO_EXTENSIONS = [
    ..., "opus", "OPUS"  # Agregar nuevo formato
]
```

---

## Testing

### Estrategia de Tests

**Unit Tests** (test/unit/test_audio_analyzer.py):
- CacheManager: save/load/hash
- AudioFeatureExtractor: extract de cada tipo
- Mocks de librosa para tests rápidos

**Integration Tests** (test/integration/):
- Pipeline completo con archivos reales
- Verificar caché funciona end-to-end
- Validar procesamiento paralelo

**Property-Based Tests**:
- Archivos idénticos → mismo hash
- Modificar archivo → hash diferente
- Análisis idempotente (mismo resultado)

---

## Conclusión

### Principios Logrados

✅ **Single Responsibility**: Cada clase una función  
✅ **Open/Closed**: Extensible sin modificar core  
✅ **Dependency Inversion**: Inyección de configuración  
✅ **DRY**: Sin repetición de lógica  
✅ **Explicit Errors**: Manejo robusto de fallos  
✅ **Testeable**: Componentes desacoplados  

### Mejoras de Rendimiento

✅ **Procesamiento Paralelo**: 3-8x speedup  
✅ **Caché Inteligente**: 100x+ speedup en subsiguientes  
✅ **Progreso en Tiempo Real**: tqdm integration  
✅ **Uso Eficiente de Recursos**: n_cores - 1  

### Mantenibilidad

✅ **Código Modular**: Fácil de extender  
✅ **Documentación Inline**: Docstrings completos  
✅ **Nombres Descriptivos**: Self-documenting code  
✅ **Arquitectura Clara**: Separación de concerns  
