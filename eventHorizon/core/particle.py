"""Particle dataclass and DataFrame conversion utility."""
from dataclasses import dataclass
from typing import Tuple, List
import pandas as pd


@dataclass
class Particle:
    """Data structure representing a single particle in the accretion disk."""
    radius: float
    angle: float
    temperature: float
    flux: float
    redshift_factor: float
    impact_parameter: float
    observed_alpha: float
    observed_x: float
    observed_y: float
    image_order: int
    brightness: float
    color: Tuple[float, float, float]
    particle_id: int = 0
    is_visible: bool = True


def particles_to_dataframe(particles: List[Particle]) -> pd.DataFrame:
    """Convert particle objects to DataFrame for visualization."""
    if not particles:
        return pd.DataFrame()
    data = []
    for p in particles:
        data.append({
            'X': p.observed_x, 'Y': p.observed_y,
            'radius': p.radius, 'angle': p.angle,
            'flux_o': p.flux, 'z_factor': p.redshift_factor,
            'impact_parameter': p.impact_parameter,
            'brightness': p.brightness, 'temperature': p.temperature,
            'is_visible': p.is_visible,
        })
    return pd.DataFrame(data)
