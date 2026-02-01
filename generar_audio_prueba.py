#!/usr/bin/env python3
"""
🎵 Generador de Audio de Prueba

Crea archivos de audio sintéticos para probar el sistema sin MP3s reales.
Útil para testing y demos.
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')

def generar_audio_prueba():
    """Genera archivos WAV de prueba con diferentes características"""
    
    try:
        import scipy.io.wavfile as wav
    except ImportError:
        print("❌ Se requiere scipy para generar audio de prueba")
        print("   Instala con: pip install scipy")
        return
    
    print("🎵 Generando archivos de audio de prueba...\n")
    
    sample_rate = 22050  # Hz
    duration = 180  # 3 minutos por canción
    
    # Definir canciones de prueba con diferentes características
    canciones = [
        # (nombre, bpm, energia, frecuencia_base)
        ("warmup_chill", 85, 0.3, 200),
        ("warmup_moderate", 95, 0.4, 250),
        ("build_energy_1", 110, 0.5, 300),
        ("build_energy_2", 120, 0.6, 350),
        ("sustain_power_1", 128, 0.7, 400),
        ("sustain_power_2", 135, 0.75, 450),
        ("sustain_power_3", 140, 0.8, 500),
        ("peak_intensity_1", 150, 0.85, 550),
        ("peak_intensity_2", 160, 0.9, 600),
        ("peak_max", 170, 0.95, 650),
        ("cooldown_1", 100, 0.5, 300),
        ("cooldown_2", 90, 0.3, 200),
    ]
    
    import os
    os.makedirs("mis_canciones", exist_ok=True)
    
    for nombre, bpm, energia, freq_base in canciones:
        # Calcula samples
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples)
        
        # Genera ritmo (beats)
        beat_freq = bpm / 60  # beats por segundo
        beat_signal = np.sin(2 * np.pi * beat_freq * t)
        
        # Genera tonos
        tono1 = np.sin(2 * np.pi * freq_base * t)
        tono2 = np.sin(2 * np.pi * freq_base * 1.5 * t) * 0.5
        tono3 = np.sin(2 * np.pi * freq_base * 2 * t) * 0.3
        
        # Combina señales
        audio = (tono1 + tono2 + tono3) * 0.3
        
        # Añade "beats" más marcados según energía
        audio += beat_signal * energia * 0.5
        
        # Añade variación de energía
        envelope = 1 + 0.3 * np.sin(2 * np.pi * 0.1 * t)  # Variación lenta
        audio *= envelope
        
        # Normaliza a 16-bit
        audio = np.int16(audio * energia * 32767)
        
        # Guarda WAV
        filename = f"mis_canciones/{nombre}.wav"
        wav.write(filename, sample_rate, audio)
        
        print(f"✅ {filename:50} | BPM: {bpm:3d} | Energía: {energia:.2f}")
    
    print(f"\n✅ ¡{len(canciones)} archivos de prueba generados!")
    print(f"📁 Ubicación: mis_canciones/")
    print(f"\n🚀 Ahora ejecuta: python main.py")

def limpiar_archivos_prueba():
    """Elimina los archivos de prueba generados"""
    import os
    import glob
    
    archivos = glob.glob("mis_canciones/*.wav")
    
    if not archivos:
        print("ℹ️  No hay archivos de prueba para eliminar")
        return
    
    print(f"🗑️  Eliminando {len(archivos)} archivos de prueba...")
    
    for archivo in archivos:
        try:
            os.remove(archivo)
            print(f"   ✅ {archivo}")
        except Exception as e:
            print(f"   ❌ Error en {archivo}: {e}")
    
    print("\n✅ Archivos de prueba eliminados")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        limpiar_archivos_prueba()
    else:
        generar_audio_prueba()
        print("\n💡 Para eliminar archivos de prueba: python generar_audio_prueba.py clean")
