"""
Unit tests for core models - targeting 100% coverage for easy wins
"""

from datetime import datetime

from src.shared_kernel.domain.entities.common import BaseEntity, TimestampedEntity


class TestBaseEntity:
    """Test BaseEntity model - should achieve 100% coverage"""

    def test_base_entity_creation_with_defaults(self):
        """Test creating BaseEntity with default values"""
        entity = BaseEntity()

        assert entity.id is None
        assert entity.created_at is None
        assert entity.updated_at is None

    def test_base_entity_creation_with_values(self):
        """Test creating BaseEntity with explicit values"""
        now = datetime.now()
        entity = BaseEntity(id=123, created_at=now, updated_at=now)

        assert entity.id == 123
        assert entity.created_at == now
        assert entity.updated_at == now

    def test_base_entity_equality(self):
        """Test BaseEntity equality comparison"""
        now = datetime.now()
        entity1 = BaseEntity(id=1, created_at=now, updated_at=now)
        entity2 = BaseEntity(id=1, created_at=now, updated_at=now)
        entity3 = BaseEntity(id=2, created_at=now, updated_at=now)

        assert entity1 == entity2
        assert entity1 != entity3

    def test_base_entity_repr(self):
        """Test BaseEntity string representation"""
        entity = BaseEntity(id=123)
        repr_str = repr(entity)

        assert "BaseEntity" in repr_str
        assert "id=123" in repr_str


class TestTimestampedEntity:
    """Test TimestampedEntity model - should achieve 100% coverage"""

    def test_timestamped_entity_creation(self):
        """Test creating TimestampedEntity"""
        entity = TimestampedEntity()

        # Inherited from BaseEntity
        assert entity.id is None
        assert entity.created_at is None
        assert entity.updated_at is None

    def test_timestamped_entity_inheritance(self):
        """Test that TimestampedEntity inherits from BaseEntity"""
        entity = TimestampedEntity(id=456)

        assert isinstance(entity, BaseEntity)
        assert entity.id == 456

    def test_timestamped_entity_with_timestamps(self):
        """Test TimestampedEntity with timestamp values"""
        now = datetime.now()
        entity = TimestampedEntity(id=789, created_at=now, updated_at=now)

        assert entity.id == 789
        assert entity.created_at == now
        assert entity.updated_at == now

    def test_timestamped_entity_dataclass_behavior(self):
        """Test dataclass functionality"""
        now = datetime.now()
        entity1 = TimestampedEntity(id=1, created_at=now)
        entity2 = TimestampedEntity(id=1, created_at=now)
        entity3 = TimestampedEntity(id=2, created_at=now)

        # Test equality
        assert entity1 == entity2
        assert entity1 != entity3

        # Test that it's a proper dataclass
        assert hasattr(entity1, "__dataclass_fields__")
