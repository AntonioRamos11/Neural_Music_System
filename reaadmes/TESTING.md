# 🧪 Guía Rápida de Tests

## 📦 Instalación

Primero instala las dependencias:

```bash
pip install -r requirements.txt
```

## 🚀 Ejecución Rápida

```bash
# 1. Generar audio de prueba (una sola vez)
python generar_audio_prueba.py

# 2. Ejecutar tests rápidos
python test/run_all.py --fast

# 3. Ejecutar todos los tests
python test/run_all.py

# 4. Con cobertura
python test/run_all.py --coverage
```

## 📁 Estructura de Tests

```
test/
├── unit/               # Tests de componentes individuales
│   ├── test_audio_analyzer.py
│   ├── test_playlist_generator.py
│   └── test_visualize.py
│
├── integration/        # Tests de integración
│   ├── test_full_pipeline.py
│   └── test_m3u_export.py
│
├── data/              # Tests de validación de datos
│   └── test_data_validation.py
│
├── helpers.py         # Utilidades compartidas
└── run_all.py         # Runner principal
```

## ✅ Tests Disponibles

### Tests Unitarios (87 tests)
- **AudioAnalyzer**: 12 tests - Extracción de features
- **PlaylistGenerator**: 45 tests - Generación de playlists
- **Visualize**: 5 tests - Gráficos

### Tests de Integración (15 tests)
- Pipeline completo
- Exportación M3U
- Flujos de múltiples módulos

### Tests de Datos (25 tests)
- Validación de rangos
- Tipos correctos
- Consistencia temporal

## 🎯 Ejemplos de Uso

### Ejecutar categoría específica

```bash
# Solo unitarios
python -m unittest discover test/unit/

# Solo integración
python -m unittest discover test/integration/

# Solo validación
python -m unittest discover test/data/
```

### Ejecutar archivo específico

```bash
python -m unittest test.unit.test_audio_analyzer
python -m unittest test.unit.test_playlist_generator
```

### Ejecutar test específico

```bash
python -m unittest test.unit.test_audio_analyzer.TestSongFeatures.test_creation
```

## 📊 Ver Resultados

Los tests mostrarán:
- ✅ Número de tests que pasaron
- ❌ Tests fallidos con detalles
- ⏱️ Tiempo de ejecución
- 📈 Cobertura de código (si usas --coverage)

## 🐛 Troubleshooting

### Error: ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### Error: No hay archivos de audio
```bash
python generar_audio_prueba.py
```

### Tests muy lentos
```bash
python test/run_all.py --fast  # Solo tests rápidos
```

## 📚 Más Información

Ver [test/README.md](test/README.md) para documentación completa.
