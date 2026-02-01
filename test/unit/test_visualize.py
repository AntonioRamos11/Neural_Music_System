"""
Tests para visualize.py

Tests específicos para:
- Generación de visualizaciones
- Gráficos de BPM
- Gráficos de intensidad
- Timeline
"""

import unittest
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from test.helpers import create_test_playlist, skip_if_no_matplotlib


class TestVisualization(unittest.TestCase):
    """Tests para el módulo de visualización"""
    
    def setUp(self):
        """Setup"""
        self.test_playlist = create_test_playlist(n_songs=10)
    
    @skip_if_no_matplotlib()
    def test_import_module(self):
        """Test: Importar módulo visualize"""
        try:
            import visualize
            self.assertTrue(True)
        except ImportError:
            self.fail("No se pudo importar visualize")
    
    @skip_if_no_matplotlib()
    def test_visualize_playlist_runs(self):
        """Test: visualize_playlist se ejecuta sin errores"""
        import matplotlib
        matplotlib.use('Agg')  # Backend sin GUI
        from visualize import visualize_playlist
        
        try:
            visualize_playlist(self.test_playlist)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"visualize_playlist falló: {e}")
    
    @skip_if_no_matplotlib()
    def test_creates_output_file(self):
        """Test: Se crea archivo de salida"""
        import matplotlib
        matplotlib.use('Agg')
        from visualize import visualize_playlist
        
        output_file = Path("playlist_visualization.png")
        
        # Limpiar si existe
        if output_file.exists():
            output_file.unlink()
        
        visualize_playlist(self.test_playlist)
        
        self.assertTrue(output_file.exists())
        
        # Cleanup
        if output_file.exists():
            output_file.unlink()


if __name__ == '__main__':
    unittest.main()
