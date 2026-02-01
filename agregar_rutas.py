#!/usr/bin/env python3
"""
Script para agregar rutas completas al análisis existente
Sin necesidad de re-analizar todas las canciones
"""

import pandas as pd
from pathlib import Path
from tqdm import tqdm

def find_file_path(filename: str, music_folder: Path) -> str:
    """Busca la ruta completa de un archivo en la carpeta de música"""
    # Buscar recursivamente
    for filepath in music_folder.rglob(filename):
        return str(filepath.resolve())
    
    # Si no se encuentra, retornar path vacío
    return ""

def add_filepaths_to_analysis(
    csv_file: str,
    music_folder: str,
    output_file: str = None
):
    """
    Agrega columna filepath al análisis existente
    
    Args:
        csv_file: Archivo CSV con el análisis (ej: csv/song_analysis.csv)
        music_folder: Carpeta raíz de la música
        output_file: Archivo de salida (si None, sobrescribe el original)
    """
    
    print("="*70)
    print("🔧 AGREGANDO RUTAS COMPLETAS AL ANÁLISIS")
    print("="*70)
    
    # Leer CSV existente
    print(f"\n📂 Leyendo: {csv_file}")
    df = pd.read_csv(csv_file)
    print(f"   {len(df)} canciones encontradas")
    
    # Verificar si ya tiene filepath
    if 'filepath' in df.columns:
        print("\n⚠️  El archivo ya tiene columna 'filepath'")
        response = input("¿Recalcular rutas? (s/n): ")
        if response.lower() != 's':
            print("Operación cancelada")
            return
    
    # Buscar rutas
    music_path = Path(music_folder)
    print(f"\n🔍 Buscando rutas en: {music_path}")
    
    filepaths = []
    not_found = []
    
    for filename in tqdm(df['filename'], desc="Buscando archivos", unit="archivo"):
        filepath = find_file_path(filename, music_path)
        filepaths.append(filepath)
        if not filepath:
            not_found.append(filename)
    
    # Agregar columna
    df['filepath'] = filepaths
    
    # Reordenar columnas (filepath después de filename)
    cols = df.columns.tolist()
    if 'filepath' in cols:
        cols.remove('filepath')
        filename_idx = cols.index('filename')
        cols.insert(filename_idx + 1, 'filepath')
        df = df[cols]
    
    # Guardar
    output = output_file or csv_file
    df.to_csv(output, index=False)
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN")
    print("="*70)
    print(f"✅ Rutas agregadas: {len(df) - len(not_found)}")
    
    if not_found:
        print(f"⚠️  Archivos no encontrados: {len(not_found)}")
        print("\nPrimeros 5 archivos no encontrados:")
        for f in not_found[:5]:
            print(f"   - {f}")
        if len(not_found) > 5:
            print(f"   ... y {len(not_found) - 5} más")
    
    print(f"\n💾 Guardado en: {output}")
    print("="*70)
    
    return df

if __name__ == "__main__":
    # Configuración
    CSV_FILE = "csv/song_analysis.csv"
    MUSIC_FOLDER = "/home/pwn/Music/Musica xioami/Music"
    
    # Verificar que existe el CSV
    if not Path(CSV_FILE).exists():
        print(f"❌ No se encuentra: {CSV_FILE}")
        print("\nArchivos CSV disponibles:")
        for csv in Path("csv").glob("*.csv"):
            print(f"   - {csv}")
        exit(1)
    
    # Ejecutar
    add_filepaths_to_analysis(CSV_FILE, MUSIC_FOLDER)
    
    print("\n✨ ¡Listo! Ahora puedes generar playlists con rutas correctas")
