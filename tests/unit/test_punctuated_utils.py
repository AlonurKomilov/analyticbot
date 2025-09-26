"""
Unit tests for punctuated utility - targeting 100% coverage
"""
import pytest
from src.utils.punctuated import Singleton


class TestSingleton:
    """Test Singleton utility class - should achieve 100% coverage"""

    def test_singleton_creation(self):
        """Test creating a Singleton instance"""
        class TestClass:
            def __init__(self, value):
                self.value = value
        
        singleton = Singleton(TestClass, "test_value")
        
        assert singleton._cls == TestClass
        assert singleton._args == ("test_value",)
        assert singleton._kwargs == {}
        assert singleton._instance is None

    def test_singleton_with_kwargs(self):
        """Test Singleton with keyword arguments"""
        class TestClass:
            def __init__(self, value, name=None):
                self.value = value
                self.name = name
        
        singleton = Singleton(TestClass, "test_value", name="test_name")
        
        assert singleton._cls == TestClass
        assert singleton._args == ("test_value",)
        assert singleton._kwargs == {"name": "test_name"}

    def test_singleton_call_creates_instance(self):
        """Test that calling singleton creates an instance"""
        class TestClass:
            def __init__(self, value):
                self.value = value
        
        singleton = Singleton(TestClass, "test_value")
        
        # First call should create instance
        instance = singleton()
        
        assert instance is not None
        assert isinstance(instance, TestClass)
        assert instance.value == "test_value"
        assert singleton._instance is instance

    def test_singleton_call_returns_same_instance(self):
        """Test that multiple calls return the same instance"""
        class TestClass:
            def __init__(self, value):
                self.value = value
                self.call_count = 0
            
            def increment(self):
                self.call_count += 1
        
        singleton = Singleton(TestClass, "test_value")
        
        # First call
        instance1 = singleton()
        instance1.increment()
        
        # Second call should return same instance
        instance2 = singleton()
        
        assert instance1 is instance2
        assert instance2.call_count == 1  # Proves it's the same instance

    def test_singleton_with_complex_kwargs(self):
        """Test Singleton with complex keyword arguments"""
        class TestClass:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs
        
        singleton = Singleton(
            TestClass, 
            "arg1", "arg2",
            key1="value1", 
            key2="value2"
        )
        
        instance = singleton()
        
        assert instance.args == ("arg1", "arg2")
        assert instance.kwargs == {"key1": "value1", "key2": "value2"}

    def test_singleton_no_args(self):
        """Test Singleton with no arguments"""
        class TestClass:
            def __init__(self):
                self.created = True
        
        singleton = Singleton(TestClass)
        
        assert singleton._args == ()
        assert singleton._kwargs == {}
        
        instance = singleton()
        assert instance.created is True

    def test_singleton_preserves_instance_state(self):
        """Test that singleton preserves instance state between calls"""
        class Counter:
            def __init__(self):
                self.count = 0
            
            def increment(self):
                self.count += 1
                return self.count
        
        singleton = Singleton(Counter)
        
        # First access and modification
        instance1 = singleton()
        count1 = instance1.increment()
        
        # Second access should show preserved state
        instance2 = singleton()
        count2 = instance2.increment()
        
        assert instance1 is instance2
        assert count1 == 1
        assert count2 == 2
        assert instance2.count == 2
