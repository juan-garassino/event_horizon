"""
Legacy adapter for backward compatibility with existing code.

This adapter provides compatibility with the original src/ structure
while using the new eventHorizon framework underneath.
"""
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd


class LegacyAdapter:
    """Adapter for backward compatibility with existing code."""
    
    def __init__(self, mass: float = 1.0, inclination: float = 80.0, accretion_rate: float = 1e-8):
        """Initialize legacy adapter."""
        self.mass = mass
        self.inclination = inclination
        self.accretion_rate = accretion_rate
    
    def generate_image_data(self, *args, **kwargs) -> pd.DataFrame:
        """Generate image data compatible with original interface."""
        pass
    
    def calculate_impact_parameter(self, *args, **kwargs):
        """Calculate impact parameter using legacy interface."""
        pass
    
    def create_isoradial(self, *args, **kwargs):
        """Create isoradial using legacy interface."""
        pass
    
    def create_isoredshift(self, *args, **kwargs):
        """Create isoredshift using legacy interface."""
        pass
    
    def plot_black_hole(self, *args, **kwargs):
        """Plot black hole using legacy interface."""
        pass