"""
Tests for caching functionality
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import patch

from sentience.cache import DataCache


class TestDataCache:
    """Test cases for DataCache"""
    
    @pytest.fixture
    def cache(self):
        """Create a DataCache instance with 5 second TTL for testing"""
        return DataCache(ttl_seconds=5)
    
    def test_cache_initialization(self):
        """Test cache initialization with custom TTL"""
        cache = DataCache(ttl_seconds=300)
        assert cache.ttl == timedelta(seconds=300)
        assert len(cache.cache) == 0
    
    def test_set_and_get(self, cache):
        """Test basic cache set and get operations"""
        test_data = {'key': 'value', 'number': 42}
        
        # Set data
        cache.set('test_key', test_data)
        
        # Get data immediately
        retrieved = cache.get('test_key')
        assert retrieved == test_data
        assert retrieved['key'] == 'value'
        assert retrieved['number'] == 42
    
    def test_cache_miss(self, cache):
        """Test cache miss returns None"""
        result = cache.get('non_existent_key')
        assert result is None
    
    def test_cache_expiration(self, cache):
        """Test cache expiration after TTL"""
        cache = DataCache(ttl_seconds=1)  # 1 second TTL for quick test
        
        # Set data
        cache.set('expire_test', 'test_value')
        
        # Verify data exists
        assert cache.get('expire_test') == 'test_value'
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Verify data expired
        assert cache.get('expire_test') is None
    
    def test_cache_expiration_with_mock(self, cache):
        """Test cache expiration using mocked time"""
        test_data = 'test_value'
        
        # Set initial time
        initial_time = datetime.utcnow()
        
        with patch('sentience.cache.datetime') as mock_datetime:
            # Set time for cache set
            mock_datetime.utcnow.return_value = initial_time
            cache.set('test_key', test_data)
            
            # Verify data exists at same time
            mock_datetime.utcnow.return_value = initial_time
            assert cache.get('test_key') == test_data
            
            # Move time forward but within TTL
            mock_datetime.utcnow.return_value = initial_time + timedelta(seconds=4)
            assert cache.get('test_key') == test_data
            
            # Move time past TTL
            mock_datetime.utcnow.return_value = initial_time + timedelta(seconds=6)
            assert cache.get('test_key') is None
    
    def test_cache_clear(self, cache):
        """Test clearing all cache entries"""
        # Add multiple entries
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        
        # Verify entries exist
        assert cache.get('key1') == 'value1'
        assert cache.get('key2') == 'value2'
        assert cache.get('key3') == 'value3'
        
        # Clear cache
        cache.clear()
        
        # Verify all entries removed
        assert cache.get('key1') is None
        assert cache.get('key2') is None
        assert cache.get('key3') is None
        assert len(cache.cache) == 0
    
    def test_cache_remove(self, cache):
        """Test removing specific cache entry"""
        # Add multiple entries
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        
        # Remove one entry
        cache.remove('key2')
        
        # Verify specific entry removed, others remain
        assert cache.get('key1') == 'value1'
        assert cache.get('key2') is None
        assert cache.get('key3') == 'value3'
    
    def test_cache_remove_non_existent(self, cache):
        """Test removing non-existent key doesn't raise error"""
        # Should not raise exception
        cache.remove('non_existent_key')
    
    def test_cache_update_existing_key(self, cache):
        """Test updating an existing cache entry"""
        # Set initial value
        cache.set('update_key', 'initial_value')
        assert cache.get('update_key') == 'initial_value'
        
        # Update with new value
        cache.set('update_key', 'updated_value')
        assert cache.get('update_key') == 'updated_value'
    
    def test_cache_with_complex_objects(self, cache):
        """Test caching complex objects"""
        complex_data = {
            'list': [1, 2, 3, 4, 5],
            'dict': {'nested': 'value', 'number': 42},
            'tuple': (10, 20, 30),
            'mixed': {
                'items': ['a', 'b', 'c'],
                'metadata': {
                    'count': 3,
                    'valid': True
                }
            }
        }
        
        cache.set('complex', complex_data)
        retrieved = cache.get('complex')
        
        assert retrieved == complex_data
        assert retrieved['list'] == [1, 2, 3, 4, 5]
        assert retrieved['dict']['nested'] == 'value'
        assert retrieved['tuple'] == (10, 20, 30)
        assert retrieved['mixed']['metadata']['count'] == 3
