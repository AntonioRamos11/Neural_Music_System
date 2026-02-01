"""
Configuraciones de Playlists para Ciclismo

Este módulo define diferentes tipos de playlists optimizadas para ciclismo
según intensidad, duración y estilo musical.
"""

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class PlaylistConfig:
    """Configuración de una playlist"""
    name: str
    duration: int  # minutos
    workout_type: str
    description: str
    bpm_range: tuple  # (min, max)
    energy_range: tuple  # (min, max)
    
class CyclingPlaylistTemplates:
    """Templates de playlists para diferentes tipos de ciclismo"""
    
    # =========================================================================
    # PLAYLISTS POR DURACIÓN
    # =========================================================================
    
    QUICK_SESSION = PlaylistConfig(
        name="Sesión Rápida",
        duration=30,
        workout_type="intervals",
        description="Entrenamiento corto e intenso - perfecto para HIIT",
        bpm_range=(140, 180),
        energy_range=(0.7, 1.0)
    )
    
    STANDARD_RIDE = PlaylistConfig(
        name="Rodada Estándar",
        duration=60,
        workout_type="endurance",
        description="Ritmo constante, ideal para fitness general",
        bpm_range=(120, 150),
        energy_range=(0.5, 0.8)
    )
    
    LONG_RIDE = PlaylistConfig(
        name="Rodada Larga",
        duration=90,
        workout_type="endurance",
        description="Resistencia prolongada con variaciones de ritmo",
        bpm_range=(110, 145),
        energy_range=(0.4, 0.7)
    )
    
    ULTRA_ENDURANCE = PlaylistConfig(
        name="Ultra Resistencia",
        duration=120,
        workout_type="endurance",
        description="Para rodadas de 2+ horas, ritmo sostenible",
        bpm_range=(100, 140),
        energy_range=(0.4, 0.6)
    )
    
    MARATHON = PlaylistConfig(
        name="Maratón",
        duration=180,
        workout_type="endurance",
        description="3 horas de música variada para ciclismo de montaña",
        bpm_range=(100, 150),
        energy_range=(0.3, 0.7)
    )
    
    # =========================================================================
    # PLAYLISTS POR INTENSIDAD
    # =========================================================================
    
    RECOVERY = PlaylistConfig(
        name="Recuperación Activa",
        duration=45,
        workout_type="recovery",
        description="Ritmo suave para días de descanso activo",
        bpm_range=(90, 120),
        energy_range=(0.2, 0.5)
    )
    
    TEMPO = PlaylistConfig(
        name="Tempo Training",
        duration=60,
        workout_type="endurance",
        description="Ritmo umbral, esfuerzo sostenido moderado-alto",
        bpm_range=(130, 155),
        energy_range=(0.6, 0.8)
    )
    
    INTERVALS = PlaylistConfig(
        name="Intervalos Alta Intensidad",
        duration=45,
        workout_type="intervals",
        description="Explosiones de energía con recuperaciones",
        bpm_range=(140, 180),
        energy_range=(0.7, 1.0)
    )
    
    SWEET_SPOT = PlaylistConfig(
        name="Sweet Spot",
        duration=60,
        workout_type="endurance",
        description="Zona de entrenamiento óptima (85-90% FTP)",
        bpm_range=(125, 145),
        energy_range=(0.6, 0.75)
    )
    
    # =========================================================================
    # PLAYLISTS POR ESTILO MUSICAL
    # =========================================================================
    
    ROCK_POWER = PlaylistConfig(
        name="Rock Power",
        duration=60,
        workout_type="intervals",
        description="Rock energético para entrenamientos intensos",
        bpm_range=(130, 170),
        energy_range=(0.7, 1.0)
    )
    
    ELECTRONIC_DRIVE = PlaylistConfig(
        name="Electronic Drive",
        duration=90,
        workout_type="endurance",
        description="Electrónica y dance para mantener el ritmo",
        bpm_range=(120, 145),
        energy_range=(0.6, 0.8)
    )
    
    POP_MOTIVATION = PlaylistConfig(
        name="Pop Motivation",
        duration=60,
        workout_type="endurance",
        description="Pop pegajoso y motivante",
        bpm_range=(115, 140),
        energy_range=(0.5, 0.8)
    )
    
    CHILL_VIBES = PlaylistConfig(
        name="Chill Vibes",
        duration=90,
        workout_type="recovery",
        description="Música relajante para rodadas tranquilas",
        bpm_range=(90, 120),
        energy_range=(0.3, 0.5)
    )
    
    LATIN_ENERGY = PlaylistConfig(
        name="Energía Latina",
        duration=60,
        workout_type="endurance",
        description="Ritmos latinos para mantener la motivación",
        bpm_range=(120, 150),
        energy_range=(0.6, 0.8)
    )
    
    OLDIES_CLASSICS = PlaylistConfig(
        name="Clásicos Nostálgicos",
        duration=90,
        workout_type="endurance",
        description="Éxitos clásicos que conoces y amas",
        bpm_range=(110, 140),
        energy_range=(0.4, 0.7)
    )
    
    # =========================================================================
    # PLAYLISTS ESPECIALIZADAS
    # =========================================================================
    
    CLIMB_POWER = PlaylistConfig(
        name="Poder de Subida",
        duration=45,
        workout_type="intervals",
        description="Para subidas largas y empinadas",
        bpm_range=(110, 135),
        energy_range=(0.7, 0.9)
    )
    
    SPRINT_TRAINING = PlaylistConfig(
        name="Entrenamiento de Sprints",
        duration=30,
        workout_type="intervals",
        description="Explosiones máximas de velocidad",
        bpm_range=(150, 190),
        energy_range=(0.8, 1.0)
    )
    
    MORNING_WAKE_UP = PlaylistConfig(
        name="Despertar Matutino",
        duration=45,
        workout_type="endurance",
        description="Para entrenamientos temprano en la mañana",
        bpm_range=(115, 135),
        energy_range=(0.5, 0.7)
    )
    
    EVENING_GRIND = PlaylistConfig(
        name="Rutina Nocturna",
        duration=60,
        workout_type="endurance",
        description="Después del trabajo, ritmo constante",
        bpm_range=(120, 145),
        energy_range=(0.6, 0.8)
    )
    
    RACE_DAY = PlaylistConfig(
        name="Día de Carrera",
        duration=120,
        workout_type="intervals",
        description="Para competencias y eventos",
        bpm_range=(130, 170),
        energy_range=(0.7, 0.95)
    )
    
    @classmethod
    def get_all_templates(cls) -> List[PlaylistConfig]:
        """Retorna todas las plantillas disponibles"""
        templates = []
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, PlaylistConfig):
                templates.append(attr)
        return templates
    
    @classmethod
    def get_by_duration(cls, duration: int) -> List[PlaylistConfig]:
        """Filtra plantillas por duración"""
        return [t for t in cls.get_all_templates() if t.duration == duration]
    
    @classmethod
    def get_by_type(cls, workout_type: str) -> List[PlaylistConfig]:
        """Filtra plantillas por tipo de entrenamiento"""
        return [t for t in cls.get_all_templates() if t.workout_type == workout_type]
    
    @classmethod
    def print_all_options(cls):
        """Imprime todas las opciones disponibles organizadas"""
        print("=" * 80)
        print("🎵 OPCIONES DE PLAYLISTS PARA CICLISMO")
        print("=" * 80)
        
        # Agrupar por categoría
        categories = {
            "⏱️  POR DURACIÓN": [
                cls.QUICK_SESSION, cls.STANDARD_RIDE, cls.LONG_RIDE, 
                cls.ULTRA_ENDURANCE, cls.MARATHON
            ],
            "💪 POR INTENSIDAD": [
                cls.RECOVERY, cls.TEMPO, cls.INTERVALS, cls.SWEET_SPOT
            ],
            "🎸 POR ESTILO MUSICAL": [
                cls.ROCK_POWER, cls.ELECTRONIC_DRIVE, cls.POP_MOTIVATION,
                cls.CHILL_VIBES, cls.LATIN_ENERGY, cls.OLDIES_CLASSICS
            ],
            "🎯 ESPECIALIZADAS": [
                cls.CLIMB_POWER, cls.SPRINT_TRAINING, cls.MORNING_WAKE_UP,
                cls.EVENING_GRIND, cls.RACE_DAY
            ]
        }
        
        for category, templates in categories.items():
            print(f"\n{category}")
            print("-" * 80)
            for i, template in enumerate(templates, 1):
                print(f"{i}. {template.name} ({template.duration} min)")
                print(f"   {template.description}")
                print(f"   BPM: {template.bpm_range[0]}-{template.bpm_range[1]} | "
                      f"Energía: {template.energy_range[0]:.1f}-{template.energy_range[1]:.1f}")
                print()

if __name__ == "__main__":
    CyclingPlaylistTemplates.print_all_options()
