"""
Tests for configuration management
"""

import logging
import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from sentience.utils.config import Config, get_config


class TestConfig:
    """Test cases for Config class"""
    
    @pytest.fixture
    def temp_config_file(self, tmp_path):
        """Create a temporary config file"""
        config_path = tmp_path / "test_config.json"
        config_data = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "callback_url": "http://localhost:8000/callback",
            "openai_api_key": "test_openai_key"
        }
        config_path.write_text(json.dumps(config_data))
        return config_path
    
    @pytest.fixture
    def env_vars(self):
        """Set up test environment variables"""
        env_vars = {
            'EVE_CLIENT_ID': 'env_client_id',
            'EVE_CLIENT_SECRET': 'env_client_secret',
            'EVE_CALLBACK_URL': 'http://localhost:9000/callback',
            'OPENAI_API_KEY': 'env_openai_key'
        }
        with patch.dict(os.environ, env_vars, clear=False):
            yield env_vars
    
    def test_config_initialization_default_path(self):
        """Test Config initialization with default path"""
        config = Config()
        assert config.config_path == Path("config.json")
        assert isinstance(config.config, dict)
    
    def test_config_initialization_custom_path(self, tmp_path):
        """Test Config initialization with custom path"""
        custom_path = tmp_path / "custom_config.json"
        config = Config(config_path=custom_path)
        assert config.config_path == custom_path
    
    def test_load_config_from_file(self, temp_config_file):
        """Test loading configuration from file"""
        config = Config(config_path=temp_config_file)
        
        assert config.get('client_id') == 'test_client_id'
        assert config.get('client_secret') == 'test_client_secret'
        assert config.get('callback_url') == 'http://localhost:8000/callback'
        assert config.get('openai_api_key') == 'test_openai_key'
    
    def test_load_config_from_env(self, env_vars):
        """Test loading configuration from environment variables"""
        # Create config with non-existent file to force env loading
        config = Config(config_path=Path("non_existent.json"))
        
        assert config.get('client_id') == 'env_client_id'
        assert config.get('client_secret') == 'env_client_secret'
        assert config.get('callback_url') == 'http://localhost:9000/callback'
        assert config.get('openai_api_key') == 'env_openai_key'
    
    def test_env_overrides_file(self, temp_config_file, env_vars):
        """Test environment variables override file values"""
        config = Config(config_path=temp_config_file)
        
        # Environment values should override file values
        assert config.get('client_id') == 'env_client_id'
        assert config.get('client_secret') == 'env_client_secret'
        assert config.get('callback_url') == 'http://localhost:9000/callback'
        assert config.get('openai_api_key') == 'env_openai_key'
    
    def test_default_values(self):
        """Test default configuration values"""
        config = Config(config_path=Path("non_existent.json"))
        
        assert config.get('cache_ttl') == 300
        assert config.get('log_level') == 'INFO'
        assert config.get('callback_url') == 'http://localhost:8000/callback'
    
    def test_get_with_default(self):
        """Test getting configuration value with default"""
        config = Config(config_path=Path("non_existent.json"))
        
        assert config.get('non_existent_key') is None
        assert config.get('non_existent_key', 'default_value') == 'default_value'
    
    def test_set_value(self):
        """Test setting configuration value"""
        config = Config(config_path=Path("non_existent.json"))
        
        config.set('test_key', 'test_value')
        assert config.get('test_key') == 'test_value'
        
        config.set('test_number', 42)
        assert config.get('test_number') == 42
    
    def test_save_config(self, tmp_path):
        """Test saving configuration to file"""
        config_path = tmp_path / "save_test.json"
        config = Config(config_path=config_path)
        
        # Set some values
        config.set('client_id', 'saved_client_id')
        config.set('client_secret', 'saved_secret')
        
        # Save config
        config.save()
        
        # Verify file was created and contains correct data
        assert config_path.exists()
        saved_data = json.loads(config_path.read_text())
        assert saved_data['client_id'] == 'saved_client_id'
        assert saved_data['client_secret'] == 'saved_secret'
    
    def test_save_config_error_handling(self):
        """Test error handling when saving config fails"""
        config = Config(config_path=Path("/invalid/path/config.json"))
        
        # Should not raise exception
        config.save()
    
    def test_validate_valid_config(self):
        """Test validation with all required values present"""
        config = Config(config_path=Path("non_existent.json"))
        config.set('client_id', 'test_id')
        config.set('client_secret', 'test_secret')
        config.set('openai_api_key', 'test_key')
        
        assert config.validate() is True
    
    def test_validate_missing_required(self):
        """Test validation with missing required values"""
        config = Config(config_path=Path("non_existent.json"))
        config.set('client_id', 'test_id')
        # Missing client_secret and openai_api_key
        
        assert config.validate() is False
    
    def test_validate_empty_values(self):
        """Test validation with empty string values"""
        config = Config(config_path=Path("non_existent.json"))
        config.set('client_id', '')
        config.set('client_secret', 'test_secret')
        config.set('openai_api_key', 'test_key')
        
        assert config.validate() is False
    
    @patch('logging.basicConfig')
    def test_setup_logging(self, mock_logging_config):
        """Test logging setup"""
        config = Config(config_path=Path("non_existent.json"))
        config.set('log_level', 'DEBUG')
        
        config.setup_logging()
        
        mock_logging_config.assert_called_once()
        call_args = mock_logging_config.call_args[1]
        assert call_args['level'] == logging.DEBUG
        assert '%(asctime)s' in call_args['format']
        assert '%(levelname)s' in call_args['format']
    
    def test_dotenv_loading(self):
        """Test .env file loading"""
        env_content = """
EVE_CLIENT_ID=dotenv_client_id
EVE_CLIENT_SECRET=dotenv_secret
OPENAI_API_KEY=dotenv_openai_key
"""
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=env_content)):
                with patch('dotenv.load_dotenv') as mock_load_dotenv:
                    config = Config(config_path=Path("non_existent.json"))
                    mock_load_dotenv.assert_called_once()


class TestGetConfig:
    """Test cases for get_config function"""
    
    def test_get_config_singleton(self):
        """Test get_config returns singleton instance"""
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2
    
    def test_get_config_instance_type(self):
        """Test get_config returns Config instance"""
        config = get_config()
        assert isinstance(config, Config)
