# infra/db/metadata.py
# Import the existing metadata from database models
from .models.database_models import metadata

# Export for Alembic
__all__ = ["metadata"]