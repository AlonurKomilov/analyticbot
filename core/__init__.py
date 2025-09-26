# Compatibility layer - deprecated, use src/ imports
import warnings
warnings.warn('core/ imports are deprecated, use src/ instead', DeprecationWarning)

# Re-export from new locations
from src.shared_kernel.domain.entities.base import *
from src.shared_kernel.application.services import *