# playlist_generator.py
import numpy as np
import pandas as pd
from typing import List, Literal
from enum import Enum

class WorkoutPhase(Enum):
    WARMUP = "warmup"
    BUILD = "build"
    PEAK = "peak"
    SUSTAIN = "sustain"
    COOLDOWN = "cooldown"

class CyclingPlaylistGenerator:
    """
    Genera playlists optimizadas para ciclismo
    basándose en las métricas de audio
    """
    
    def __init__(self, songs_df: pd.DataFrame):
        self.df = songs_df.copy()
        self._calculate_scores()
    
    def _calculate_scores(self):
        """Calcula scores para diferentes propósitos"""
        
        # Normaliza features a 0-1
        for col in ['bpm', 'energy', 'brightness', 'onset_rate', 'beat_strength']:
            if col in self.df.columns:
                min_val = self.df[col].min()
                max_val = self.df[col].max()
                if max_val > min_val:
                    self.df[f'{col}_norm'] = (self.df[col] - min_val) / (max_val - min_val)
                else:
                    self.df[f'{col}_norm'] = 0.5
        
        # Score de intensidad (para fases de trabajo)
        self.df['intensity_score'] = (
            self.df['energy_norm'] * 0.35 +
            self.df['bpm_norm'] * 0.25 +
            self.df['beat_strength'] * 0.20 +
            self.df['onset_rate_norm'] * 0.20
        )
        
        # Score de warmup (energía media, BPM moderado)
        self.df['warmup_score'] = 1 - abs(self.df['intensity_score'] - 0.4)
        
        # Score de cooldown (baja energía)
        self.df['cooldown_score'] = 1 - self.df['intensity_score']
        
        # Score de motivación (beat claro + energía alta)
        self.df['motivation_score'] = (
            self.df['beat_strength'] * 0.4 +
            self.df['energy_norm'] * 0.4 +
            self.df['brightness_norm'] * 0.2
        )
    
    def generate_workout_playlist(
        self,
        duration_minutes: int = 60,
        workout_type: Literal["endurance", "intervals", "recovery"] = "endurance"
    ) -> pd.DataFrame:
        """
        Genera playlist para un workout específico
        
        Args:
            duration_minutes: Duración deseada en minutos
            workout_type: Tipo de entrenamiento
        """
        
        target_duration = duration_minutes * 60  # a segundos
        
        if workout_type == "endurance":
            # Estructura: Warmup (10%) → Build (20%) → Sustain (50%) → Cooldown (20%)
            phases = [
                (WorkoutPhase.WARMUP, 0.10),
                (WorkoutPhase.BUILD, 0.20),
                (WorkoutPhase.SUSTAIN, 0.50),
                (WorkoutPhase.COOLDOWN, 0.20)
            ]
        elif workout_type == "intervals":
            # Estructura: Warmup (15%) → [Peak/Recovery]x4 (70%) → Cooldown (15%)
            phases = [
                (WorkoutPhase.WARMUP, 0.15),
                (WorkoutPhase.PEAK, 0.10),
                (WorkoutPhase.SUSTAIN, 0.08),
                (WorkoutPhase.PEAK, 0.10),
                (WorkoutPhase.SUSTAIN, 0.08),
                (WorkoutPhase.PEAK, 0.10),
                (WorkoutPhase.SUSTAIN, 0.08),
                (WorkoutPhase.PEAK, 0.10),
                (WorkoutPhase.SUSTAIN, 0.06),
                (WorkoutPhase.COOLDOWN, 0.15)
            ]
        else:  # recovery
            phases = [
                (WorkoutPhase.WARMUP, 0.20),
                (WorkoutPhase.SUSTAIN, 0.60),
                (WorkoutPhase.COOLDOWN, 0.20)
            ]
        
        playlist = []
        used_songs = set()
        current_duration = 0
        
        for phase, phase_ratio in phases:
            phase_duration = target_duration * phase_ratio
            phase_songs = self._select_songs_for_phase(
                phase, 
                phase_duration, 
                used_songs
            )
            
            for _, song in phase_songs.iterrows():
                playlist.append({
                    **song.to_dict(),
                    'phase': phase.value
                })
                used_songs.add(song['filename'])
                current_duration += song['duration']
        
        result = pd.DataFrame(playlist)
        
        # Añade tiempo acumulado
        result['cumulative_time'] = result['duration'].cumsum()
        result['start_time'] = result['cumulative_time'] - result['duration']
        
        return result
    
    def _select_songs_for_phase(
        self, 
        phase: WorkoutPhase, 
        target_duration: float,
        exclude: set
    ) -> pd.DataFrame:
        """Selecciona canciones para una fase específica"""
        
        # Filtra canciones no usadas
        available = self.df[~self.df['filename'].isin(exclude)].copy()
        
        if len(available) == 0:
            return pd.DataFrame()
        
        # Score según fase
        if phase == WorkoutPhase.WARMUP:
            available = available.sort_values('warmup_score', ascending=False)
        elif phase == WorkoutPhase.BUILD:
            # Ordena por intensidad creciente
            available = available.sort_values('intensity_score', ascending=True)
        elif phase == WorkoutPhase.PEAK:
            available = available.sort_values('intensity_score', ascending=False)
        elif phase == WorkoutPhase.SUSTAIN:
            # Intensidad media-alta con buen beat
            available['sustain_score'] = (
                available['motivation_score'] * 0.6 +
                (1 - abs(available['intensity_score'] - 0.7)) * 0.4
            )
            available = available.sort_values('sustain_score', ascending=False)
        else:  # COOLDOWN
            available = available.sort_values('cooldown_score', ascending=False)
        
        # Selecciona canciones hasta llenar duración
        selected = []
        current_duration = 0
        
        for _, song in available.iterrows():
            if current_duration >= target_duration:
                break
            selected.append(song)
            current_duration += song['duration']
        
        return pd.DataFrame(selected)
    
    def generate_energy_curve_playlist(
        self,
        energy_curve: List[float],
        duration_minutes: int = 60
    ) -> pd.DataFrame:
        """
        Genera playlist siguiendo una curva de energía personalizada
        
        Args:
            energy_curve: Lista de valores 0-1 representando energía deseada
                         (ej: [0.3, 0.5, 0.7, 0.9, 0.9, 0.7, 0.4])
            duration_minutes: Duración total
        """
        
        target_duration = duration_minutes * 60
        segment_duration = target_duration / len(energy_curve)
        
        playlist = []
        used_songs = set()
        
        for i, target_energy in enumerate(energy_curve):
            # Encuentra canción más cercana a la energía objetivo
            available = self.df[~self.df['filename'].isin(used_songs)].copy()
            
            if len(available) == 0:
                break
            
            # Score: qué tan cerca está de la energía objetivo
            available['match_score'] = 1 - abs(available['intensity_score'] - target_energy)
            
            # Bonus por beat claro (siempre bueno para ciclismo)
            available['match_score'] += available['beat_strength'] * 0.2
            
            best_match = available.sort_values('match_score', ascending=False).iloc[0]
            
            playlist.append({
                **best_match.to_dict(),
                'target_energy': target_energy,
                'segment': i + 1
            })
            used_songs.add(best_match['filename'])
        
        return pd.DataFrame(playlist)
    
    def order_by_bpm_for_cadence(
        self,
        target_cadence: int = 90,
        tolerance: int = 10
    ) -> pd.DataFrame:
        """
        Ordena canciones para mantener una cadencia objetivo
        
        BPM ideal = cadencia * 1 (pedaleada por beat)
                  o cadencia * 2 (2 beats por pedaleada)
        """
        
        df = self.df.copy()
        
        # Calcula qué tan bien matchea cada canción con la cadencia
        # Considera BPM directo o la mitad (para BPMs altos)
        df['cadence_match_1x'] = abs(df['bpm'] - target_cadence)
        df['cadence_match_2x'] = abs(df['bpm'] - target_cadence * 2)
        df['cadence_match_half'] = abs(df['bpm'] / 2 - target_cadence)
        
        df['best_cadence_match'] = df[
            ['cadence_match_1x', 'cadence_match_2x', 'cadence_match_half']
        ].min(axis=1)
        
        # Filtra por tolerancia
        good_matches = df[df['best_cadence_match'] <= tolerance].copy()
        
        if len(good_matches) == 0:
            print(f"⚠️ No hay canciones que matcheen cadencia {target_cadence} ± {tolerance}")
            good_matches = df.nsmallest(len(df) // 2, 'best_cadence_match')
        
        # Ordena por energía para crear progresión
        return good_matches.sort_values('intensity_score')
