"""
Fixtures - Datos de prueba reutilizables

Este módulo contiene datos y configuraciones de prueba
que pueden ser compartidos entre múltiples tests.
"""

# Datos de prueba comunes
SAMPLE_SONGS = [
    {
        'filename': 'warmup_song.mp3',
        'title': 'Gentle Warmup',
        'bpm': 85,
        'energy': 0.3,
        'phase': 'warmup'
    },
    {
        'filename': 'build_song.mp3',
        'title': 'Building Energy',
        'bpm': 110,
        'energy': 0.6,
        'phase': 'build'
    },
    {
        'filename': 'peak_song.mp3',
        'title': 'Maximum Power',
        'bpm': 150,
        'energy': 0.9,
        'phase': 'peak'
    }
]

WORKOUT_CONFIGS = {
    'endurance': {
        'duration': 60,
        'avg_intensity': 0.6,
        'phases': ['warmup', 'build', 'sustain', 'cooldown']
    },
    'intervals': {
        'duration': 45,
        'avg_intensity': 0.75,
        'phases': ['warmup', 'peak', 'sustain', 'cooldown']
    },
    'recovery': {
        'duration': 30,
        'avg_intensity': 0.4,
        'phases': ['warmup', 'sustain', 'cooldown']
    }
}
