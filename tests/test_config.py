"""Tests for configuration management."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from hyperpod_tui.config import Config, DEFAULT_CONFIG


class TestConfig:
    """Test configuration management."""
    
    def test_default_config_creation(self):
        """Test that default config is created when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".hyperpod-tui"
            config_file = config_dir / "config.json"
            
            with patch('hyperpod_tui.config.Path.home', return_value=Path(temp_dir)):
                config = Config()
                
                assert config_file.exists()
                assert config.config == DEFAULT_CONFIG
    
    def test_config_loading(self):
        """Test loading existing configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".hyperpod-tui"
            config_dir.mkdir()
            config_file = config_dir / "config.json"
            
            # Create custom config
            custom_config = {
                "key_bindings": {
                    "quit": ["x"]
                },
                "ui": {
                    "default_details_height": 0.5
                }
            }
            
            with open(config_file, 'w') as f:
                json.dump(custom_config, f)
            
            with patch('hyperpod_tui.config.Path.home', return_value=Path(temp_dir)):
                config = Config()
                
                # Should merge with defaults
                assert config.get('key_bindings.quit') == ["x"]
                assert config.get('ui.default_details_height') == 0.5
                assert config.get('key_bindings.enter') == DEFAULT_CONFIG['key_bindings']['enter']
    
    def test_get_method(self):
        """Test the get method with dot notation."""
        config = Config()
        
        # Test existing keys
        assert config.get('ui.default_details_height') == 0.3
        assert config.get('key_bindings.quit') == ['q', 'Q']
        
        # Test non-existing keys
        assert config.get('nonexistent.key') is None
        assert config.get('nonexistent.key', 'default') == 'default'
    
    def test_invalid_json_fallback(self):
        """Test fallback to default config when JSON is invalid."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".hyperpod-tui"
            config_dir.mkdir()
            config_file = config_dir / "config.json"
            
            # Create invalid JSON
            with open(config_file, 'w') as f:
                f.write("invalid json content")
            
            with patch('hyperpod_tui.config.Path.home', return_value=Path(temp_dir)):
                config = Config()
                
                # Should fall back to defaults
                assert config.config == DEFAULT_CONFIG