# Compatibility layer - deprecated
import warnings
warnings.warn('infra/ imports are deprecated, use src/ instead', DeprecationWarning)

# Re-export from new locations
from src.shared_kernel.infrastructure import *