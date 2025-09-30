"""Adapters for integrating reference implementations."""

from .reference_adapter import UnifiedReferenceAdapter, ReferenceAdapter
from .legacy_adapter import LegacyAdapter

# Clean framework-native aliases
ClassicalAdapter = UnifiedReferenceAdapter
ParticleAdapter = UnifiedReferenceAdapter

# Legacy reference-specific aliases (deprecated)
BhsimAdapter = ClassicalAdapter
LuminetAdapter = ParticleAdapter

__all__ = [
    # Primary unified interfaces
    'UnifiedReferenceAdapter',
    'ReferenceAdapter',
    'LegacyAdapter',
    
    # Clean framework-native aliases
    'ClassicalAdapter',
    'ParticleAdapter',
    
    # Legacy compatibility (deprecated)
    'BhsimAdapter',
    'LuminetAdapter'
]