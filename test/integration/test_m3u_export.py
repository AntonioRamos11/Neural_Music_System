"""
Tests de exportación M3U

Tests para:
- Generación de archivos M3U
- Formato correcto
- Metadata
"""

import unittest
import sys
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from test.helpers import create_test_playlist


class TestM3UExport(unittest.TestCase):
    """Tests para exportación a formato M3U"""
    
    def setUp(self):
        """Setup"""
        self.test_playlist = create_test_playlist(n_songs=5)
    
    def test_generate_m3u(self):
        """Test: Generar archivo M3U"""
        from main import generate_m3u
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.m3u', delete=False) as f:
            output_file = f.name
        
        try:
            generate_m3u(self.test_playlist, output_file, "mis_canciones")
            
            # Verificar que existe
            self.assertTrue(Path(output_file).exists())
            
            # Verificar contenido
            with open(output_file, 'r') as f:
                content = f.read()
                
                self.assertIn("#EXTM3U", content, "Falta header M3U")
                self.assertIn("#EXTINF:", content, "Falta metadata")
                
                # Debe contener los nombres de archivo
                for filename in self.test_playlist['filename']:
                    self.assertIn(filename, content)
        
        finally:
            # Cleanup
            if Path(output_file).exists():
                Path(output_file).unlink()
    
    def test_m3u_format(self):
        """Test: Formato M3U es correcto"""
        from main import generate_m3u
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.m3u', delete=False) as f:
            output_file = f.name
        
        try:
            generate_m3u(self.test_playlist, output_file, "mis_canciones")
            
            with open(output_file, 'r') as f:
                lines = f.readlines()
            
            # Primera línea debe ser el header
            self.assertTrue(lines[0].strip() == "#EXTM3U")
            
            # Contar líneas EXTINF y archivos
            extinf_count = sum(1 for line in lines if line.startswith("#EXTINF:"))
            # Archivos son las líneas que no empiezan con # y no están vacías
            file_count = sum(1 for line in lines if line.strip() and not line.startswith("#"))
            
            # Debe haber la misma cantidad de EXTINF que archivos
            self.assertEqual(extinf_count, file_count)
            
            # Debe coincidir con el número de canciones en la playlist
            self.assertEqual(extinf_count, len(self.test_playlist))
        
        finally:
            if Path(output_file).exists():
                Path(output_file).unlink()


if __name__ == '__main__':
    unittest.main()
