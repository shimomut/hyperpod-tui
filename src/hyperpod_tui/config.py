"""Configuration management for HyperPod TUI."""

import os
import json
from pathlib import Path
from typing import Dict, Any


DEFAULT_CONFIG = {
    "key_bindings": {
        "quit": ["q", "Q"],
        "enter": ["\n", "\r"],
        "back": ["\b", "KEY_BACKSPACE", "\x7f", "\x08"],
        "expand_details": ["}"],
        "shrink_details": ["{"],
        "up": ["KEY_UP", "k"],
        "down": ["KEY_DOWN", "j"],
        "left": ["KEY_LEFT", "h"],
        "right": ["KEY_RIGHT", "l"],
        "page_up": ["KEY_PPAGE"],
        "page_down": ["KEY_NPAGE"],
        "home": ["KEY_HOME"],
        "end": ["KEY_END"],
        "delete": ["KEY_DC"],
        "clear_filter": ["KEY_DC", "x"],
        "refresh": ["r", "R", "KEY_F5"]
    },
    "ui": {
        "default_details_height": 0.3,  # 30% of screen height
        "min_details_height": 3,
        "max_details_height": 0.8,  # 80% of screen height
        "filter_prompt": "Filter: ",
        "search_prompt": "Filter: ",
        "colors": {
            "header": "cyan",
            "footer": "cyan", 
            "selected": "reverse",
            "border": "white",
            "error": "red",
            "info": "green"
        }
    },
    "aws": {
        "region": "us-east-1",
        "profile": None  # Use default profile
    }
}


class Config:
    """Configuration manager for HyperPod TUI."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".hyperpod-tui"
        self.config_file = self.config_dir / "config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if not self.config_file.exists():
            self._create_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            # Merge with defaults to ensure all keys exist
            return self._merge_config(DEFAULT_CONFIG, config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG.copy()
    
    def _create_default_config(self):
        """Create default configuration file."""
        self.config_dir.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
    
    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config with defaults."""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key: str, default=None):
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def save(self):
        """Save current configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)


# Global config instance
config = Config()