"""
Configuration management for Sentience
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """Centralized configuration management"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config.json")
        self.config: Dict[str, Any] = {}
        self._load_config()
        
    def _load_config(self) -> None:
        """Load configuration from environment and/or config file"""
        # Load .env file if it exists
        load_dotenv()
        
        # Try to load from config file first
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        # Override with environment variables
        env_mapping = {
            'client_id': 'EVE_CLIENT_ID',
            'client_secret': 'EVE_CLIENT_SECRET',
            'callback_url': 'EVE_CALLBACK_URL',
            'openai_api_key': 'OPENAI_API_KEY',
        }
        
        for key, env_var in env_mapping.items():
            env_value = os.getenv(env_var)
            if env_value:
                self.config[key] = env_value
                
        # Set defaults
        defaults = {
            'callback_url': 'http://localhost:8000/callback',
            'cache_ttl': 300,
            'log_level': 'INFO',
        }
        
        for key, default_value in defaults.items():
            if key not in self.config:
                self.config[key] = default_value
                
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
        
    def save(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            
    def validate(self) -> bool:
        """Validate required configuration values"""
        required_keys = ['client_id', 'client_secret', 'openai_api_key']
        missing_keys = [key for key in required_keys if not self.get(key)]
        
        if missing_keys:
            logger.error(f"Missing required configuration: {', '.join(missing_keys)}")
            return False
            
        return True
        
    def setup_logging(self) -> None:
        """Configure logging based on config"""
        log_level = self.get('log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create global config instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config
