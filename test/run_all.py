#!/usr/bin/env python3
"""
Runner principal para todos los tests

Ejecuta todos los tests organizados en la estructura test/

Uso:
    python -m test                      # Todos los tests
    python -m test.unit                 # Solo tests unitarios
    python -m test.integration          # Solo integración
    python -m test.data                 # Solo validación de datos
    
O con este script:
    python test/run_all.py              # Todos con reporte
    python test/run_all.py --unit       # Solo unitarios
    python test/run_all.py --fast       # Tests rápidos
    python test/run_all.py --coverage   # Con cobertura
"""

import sys
import unittest
from pathlib import Path

# Añadir directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_all_tests(verbosity=2):
    """Ejecuta todos los tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Cargar tests de cada módulo
    test_dir = Path(__file__).parent
    
    suite.addTests(loader.discover(str(test_dir / 'unit'), pattern='test_*.py'))
    suite.addTests(loader.discover(str(test_dir / 'integration'), pattern='test_*.py'))
    suite.addTests(loader.discover(str(test_dir / 'data'), pattern='test_*.py'))
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_unit_tests(verbosity=2):
    """Ejecuta solo tests unitarios"""
    loader = unittest.TestLoader()
    test_dir = Path(__file__).parent / 'unit'
    suite = loader.discover(str(test_dir), pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_integration_tests(verbosity=2):
    """Ejecuta solo tests de integración"""
    loader = unittest.TestLoader()
    test_dir = Path(__file__).parent / 'integration'
    suite = loader.discover(str(test_dir), pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_data_tests(verbosity=2):
    """Ejecuta solo tests de validación de datos"""
    loader = unittest.TestLoader()
    test_dir = Path(__file__).parent / 'data'
    suite = loader.discover(str(test_dir), pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_with_coverage():
    """Ejecuta tests con reporte de cobertura"""
    try:
        import coverage
    except ImportError:
        print("❌ coverage no instalado")
        print("   Instala con: pip install coverage")
        return False
    
    cov = coverage.Coverage(source=['audio_analyzer', 'playlist_generator', 'visualize', 'main'])
    cov.start()
    
    success = run_all_tests(verbosity=2)
    
    cov.stop()
    cov.save()
    
    print("\n" + "="*70)
    print("REPORTE DE COBERTURA")
    print("="*70 + "\n")
    
    cov.report()
    
    # Generar HTML
    cov.html_report(directory='htmlcov')
    print("\n📊 Reporte HTML: htmlcov/index.html")
    
    return success


def print_help():
    """Imprime ayuda"""
    print("""
🧪 Test Runner - Music Cycling System

Uso:
    python test/run_all.py [opciones]

Opciones:
    --all         Ejecutar todos los tests (por defecto)
    --unit        Solo tests unitarios
    --integration Solo tests de integración  
    --data        Solo tests de validación de datos
    --fast        Tests rápidos (unitarios + data)
    --coverage    Ejecutar con análisis de cobertura
    --help, -h    Mostrar esta ayuda

Ejemplos:
    python test/run_all.py
    python test/run_all.py --unit
    python test/run_all.py --coverage

También puedes usar pytest si está instalado:
    pytest test/
    pytest test/unit/
    pytest test/ -v --tb=short
""")


def main():
    """Main"""
    args = sys.argv[1:]
    
    if '--help' in args or '-h' in args:
        print_help()
        return 0
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           🧪 TEST SUITE - MUSIC CYCLING SYSTEM 🚴               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    if '--coverage' in args:
        success = run_with_coverage()
    elif '--unit' in args:
        print("📦 Ejecutando tests unitarios...\n")
        success = run_unit_tests()
    elif '--integration' in args:
        print("🔗 Ejecutando tests de integración...\n")
        success = run_integration_tests()
    elif '--data' in args:
        print("📊 Ejecutando tests de validación...\n")
        success = run_data_tests()
    elif '--fast' in args:
        print("⚡ Ejecutando tests rápidos...\n")
        success_unit = run_unit_tests(verbosity=1)
        success_data = run_data_tests(verbosity=1)
        success = success_unit and success_data
    else:
        print("🔍 Ejecutando todos los tests...\n")
        success = run_all_tests()
    
    if success:
        print("\n✅ TODOS LOS TESTS PASARON\n")
        return 0
    else:
        print("\n❌ ALGUNOS TESTS FALLARON\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
