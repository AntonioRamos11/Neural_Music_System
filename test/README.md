# 🧪 Test Suite - Music Cycling System

Suite de pruebas completa y organizada para el sistema de playlists de ciclismo.

## 📁 Estructura

```
test/
├── __init__.py                      # Inicialización del paquete
├── helpers.py                       # Utilidades compartidas
├── run_all.py                       # Runner principal
│
├── unit/                            # Tests unitarios
│   ├── test_audio_analyzer.py      # Tests de AudioAnalyzer
│   ├── test_playlist_generator.py  # Tests de PlaylistGenerator
│   └── test_visualize.py           # Tests de visualización
│
├── integration/                     # Tests de integración
│   ├── test_full_pipeline.py       # Pipeline completo
│   └── test_m3u_export.py          # Exportación M3U
│
├── data/                            # Tests de validación
│   └── test_data_validation.py     # Validación de datos
│
└── fixtures/                        # Datos de prueba
    └── (archivos de prueba)
```

## 🚀 Ejecutar Tests

### Opción 1: Con Python unittest

```bash
# Todos los tests
python -m unittest discover test/

# Tests específicos
python -m unittest test.unit.test_audio_analyzer
python -m unittest test.integration.test_full_pipeline
python -m unittest test.data.test_data_validation

# Un test específico
python -m unittest test.unit.test_audio_analyzer.TestSongFeatures.test_creation
```

### Opción 2: Con el runner personalizado

```bash
# Todos los tests
python test/run_all.py

# Solo unitarios
python test/run_all.py --unit

# Solo integración
python test/run_all.py --integration

# Con cobertura de código
python test/run_all.py --coverage

# Tests rápidos
python test/run_all.py --fast
```

### Opción 3: Con pytest (si está instalado)

```bash
# Instalar pytest
pip install pytest pytest-cov

# Ejecutar tests
pytest test/
pytest test/ -v
pytest test/unit/
pytest test/ --tb=short

# Con cobertura
pytest test/ --cov=. --cov-report=html
```

### Opción 4: Con el script bash completo

```bash
# Script con verificación de dependencias y generación de audio
./run_tests.sh
./run_tests.sh quick
./run_tests.sh coverage
```

## 📊 Categorías de Tests

### 🔬 Tests Unitarios (`test/unit/`)

Tests aislados de componentes individuales:

#### `test_audio_analyzer.py`
- ✅ Creación de SongFeatures
- ✅ Valores por defecto
- ✅ Creación de AudioAnalyzer
- ✅ Análisis de archivos individuales
- ✅ Conversión a DataFrame
- ✅ Validación de columnas

#### `test_playlist_generator.py`
- ✅ Enum WorkoutPhase
- ✅ Creación de CyclingPlaylistGenerator
- ✅ Cálculo de scores
- ✅ Normalización de features
- ✅ Generación de playlists (endurance, intervals, recovery)
- ✅ Ordenamiento por cadencia
- ✅ Curvas de energía personalizadas
- ✅ Sin canciones duplicadas

#### `test_visualize.py`
- ✅ Generación de visualizaciones
- ✅ Creación de archivos PNG

### 🔗 Tests de Integración (`test/integration/`)

Tests del flujo completo entre módulos:

#### `test_full_pipeline.py`
- ✅ Pipeline completo: Análisis → Playlist → Export
- ✅ Guardar y cargar CSV
- ✅ Múltiples tipos de workout

#### `test_m3u_export.py`
- ✅ Generación de archivos M3U
- ✅ Formato correcto
- ✅ Metadata completa

### 📈 Tests de Datos (`test/data/`)

Tests de validación de calidad de datos:

#### `test_data_validation.py`
- ✅ Rangos válidos (BPM, energía, duración)
- ✅ Tipos de datos correctos
- ✅ Sin valores NaN
- ✅ Consistencia temporal
- ✅ Fases válidas
- ✅ Estructura de playlist

## 🛠️ Helpers Disponibles

El módulo `test/helpers.py` proporciona utilidades:

### Generación de Datos de Prueba
```python
from test.helpers import create_test_song_dataframe, create_test_playlist

# Crear DataFrame de canciones
songs_df = create_test_song_dataframe(n_songs=20)

# Crear playlist de prueba
playlist = create_test_playlist(n_songs=10)
```

### Context Managers
```python
from test.helpers import TemporaryMusicFolder, SuppressOutput

# Carpeta temporal con audio
with TemporaryMusicFolder(n_songs=5) as folder:
    # Usar folder...
    pass

# Suprimir output durante tests
with SuppressOutput():
    # Código ruidoso...
    pass
```

### Assertions Personalizadas
```python
from test.helpers import (
    assert_valid_bpm,
    assert_valid_energy,
    assert_playlist_structure,
    assert_time_progression
)

assert_valid_bpm(120)
assert_valid_energy(0.7)
assert_playlist_structure(playlist_df)
assert_time_progression(playlist_df)
```

### Decorators para Skip
```python
from test.helpers import skip_if_no_librosa, skip_if_no_scipy

@skip_if_no_librosa()
def test_audio_analysis():
    # Se saltea si no hay librosa
    pass
```

## 📋 Ejemplos de Uso

### Test Individual

```python
import unittest
from test.helpers import create_test_song_dataframe

class TestMyFeature(unittest.TestCase):
    def test_something(self):
        df = create_test_song_dataframe(n_songs=10)
        # Tu test aquí...
        self.assertEqual(len(df), 10)

if __name__ == '__main__':
    unittest.main()
```

### Test con Audio Sintético

```python
import unittest
from test.helpers import TemporaryMusicFolder, SuppressOutput
from audio_analyzer import AudioAnalyzer

class TestAudioAnalysis(unittest.TestCase):
    def test_analyze_folder(self):
        with TemporaryMusicFolder(n_songs=3) as folder:
            analyzer = AudioAnalyzer(str(folder))
            
            with SuppressOutput():
                df = analyzer.analyze_folder()
            
            self.assertGreater(len(df), 0)
```

## 🎯 Cobertura de Código

Generar reporte de cobertura:

```bash
# Con el runner personalizado
python test/run_all.py --coverage

# Con pytest
pytest test/ --cov=. --cov-report=html

# Con coverage directamente
coverage run -m unittest discover test/
coverage report
coverage html
```

Ver reporte HTML: `htmlcov/index.html`

## ⚡ Tests Rápidos vs Completos

### Tests Rápidos (< 10 segundos)
- Tests unitarios con datos sintéticos
- Validación de estructura
- Sin análisis de audio real

```bash
python test/run_all.py --fast
```

### Tests Completos (> 30 segundos)
- Incluye análisis de audio con librosa
- Generación de archivos de prueba
- Tests de integración completos

```bash
python test/run_all.py
```

## 🐛 Debugging Tests

### Ejecutar con más detalle

```bash
# Unittest verbose
python -m unittest discover test/ -v

# Pytest con traceback completo
pytest test/ -vv --tb=long

# Ver print statements
pytest test/ -s
```

### Ejecutar un solo test

```bash
# Unittest
python -m unittest test.unit.test_audio_analyzer.TestSongFeatures.test_creation

# Pytest
pytest test/unit/test_audio_analyzer.py::TestSongFeatures::test_creation
```

## 📝 Añadir Nuevos Tests

### 1. Decidir categoría
- `unit/` - Test de un componente aislado
- `integration/` - Test de múltiples componentes
- `data/` - Test de validación de datos

### 2. Crear archivo
```python
# test/unit/test_mi_modulo.py
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestMiModulo(unittest.TestCase):
    def test_algo(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
```

### 3. Usar helpers
```python
from test.helpers import create_test_song_dataframe, skip_if_no_librosa

@skip_if_no_librosa()
def test_con_librosa(self):
    df = create_test_song_dataframe()
    # ...
```

## 🔧 Dependencias para Tests

### Mínimas (siempre requeridas)
- numpy
- pandas

### Opcionales (tests se saltean si no están)
- librosa (análisis de audio)
- scipy (generación de audio sintético)
- matplotlib (visualización)
- coverage (cobertura de código)
- pytest (runner alternativo)

## 📈 CI/CD

Para integración continua, añade a tu `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python test/run_all.py --fast
```

## 🎓 Buenas Prácticas

1. **Tests aislados**: Cada test debe ser independiente
2. **Setup/Teardown**: Usar setUp() y tearDown() para preparar datos
3. **Nombres descriptivos**: `test_generate_endurance_playlist_30min()`
4. **Un concepto por test**: No mezclar múltiples validaciones
5. **Usar helpers**: Reutilizar utilidades de `test/helpers.py`
6. **Skip inteligente**: Usar decorators para dependencias opcionales
7. **Documentar**: Docstrings claros en cada test

## 📊 Estadísticas

```bash
# Contar tests
find test/ -name "test_*.py" -exec grep -c "def test_" {} + | awk '{s+=$1} END {print s}'

# Ver estructura
tree test/

# Métricas con pytest
pytest test/ --co  # Lista todos los tests
```

---

**Ejemplo de salida:**

```
🧪 TEST SUITE - MUSIC CYCLING SYSTEM 🚴

test_audio_analyzer.py ..................... [ 25%]
test_playlist_generator.py ................ [ 60%]
test_visualize.py .......................... [ 65%]
test_full_pipeline.py ..................... [ 80%]
test_m3u_export.py ........................ [ 85%]
test_data_validation.py ................... [100%]

✅ 87 tests passed in 5.32s

COBERTURA:
  audio_analyzer.py      95%
  playlist_generator.py  92%
  visualize.py           88%
  main.py               90%
```
