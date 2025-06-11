"""
Configuration Manager - Handle settings and credentials.
"""

import json
import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional

class ConfigManager:
    """Configuration management system."""
    
    def __init__(self) -> None:
        self.config_dir = Path.home() / ".bgpt"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger("bgpt.config")
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration."""
        return {
            "provider": "gemini",
            "theme": "default",
            "safety_level": "medium",
            "auto_execute": False,
            "save_history": True
        }
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def get_provider(self) -> str:
        """Get current AI provider."""
        return self._config.get("provider", "gemini")
    
    def set_provider(self, provider: str) -> None:
        """Set AI provider."""
        self._config["provider"] = provider
        self._save_config()
    
    def set_theme(self, theme: str) -> None:
        """Set UI theme."""
        self._config["theme"] = theme
        self._save_config()
    
    def set_safety_level(self, level: str) -> None:
        """Set safety level."""
        self._config["safety_level"] = level
        self._save_config()
    
    def get_theme(self) -> str:
        """Get current theme."""
        return self._config.get("theme", "default")
    
    def get_safety_level(self) -> str:
        """Get current safety level."""
        return self._config.get("safety_level", "medium")
    
    def run_setup_wizard(self) -> None:
        """Run interactive setup wizard."""
        print("🚀 Bgpt Setup Wizard")
        print("===================")
        
        # Provider selection
        print("\nChoose AI provider:")
        print("1. gemini (Google Gemini)")
        print("2. openai (OpenAI GPT)")
        print("3. anthropic (Claude)")
        print("4. local (Ollama)")
        
        choice = input("Enter choice [1]: ").strip() or "1"
        provider_map = {"1": "gemini", "2": "openai", "3": "anthropic", "4": "local"}
        provider = provider_map.get(choice, "gemini")
        self.set_provider(provider)
        
        # API key setup
        if provider in ["gemini", "openai", "anthropic"]:
            api_key = input(f"Enter {provider} API key (or press Enter to skip): ").strip()
            if api_key:
                self._store_api_key(provider, api_key)
        
        # Theme selection
        print("\nChoose theme:")
        print("1. default")
        print("2. dark")
        print("3. light")
        
        theme_choice = input("Enter choice [1]: ").strip() or "1"
        theme_map = {"1": "default", "2": "dark", "3": "light"}
        theme = theme_map.get(theme_choice, "default")
        self.set_theme(theme)
        
        # Safety level
        print("\nChoose safety level:")
        print("1. low")
        print("2. medium") 
        print("3. high")
        
        safety_choice = input("Enter choice [2]: ").strip() or "2"
        safety_map = {"1": "low", "2": "medium", "3": "high"}
        safety = safety_map.get(safety_choice, "medium")
        self.set_safety_level(safety)
        
        print("✅ Setup complete!")
    
    def _store_api_key(self, provider: str, api_key: str) -> None:
        """Store API key securely."""
        try:
            import keyring
            keyring.set_password("bgpt", provider, api_key)
            print(f"✅ {provider} API key stored securely")
        except Exception:
            # Fallback to environment variable suggestion
            print(f"⚠️  Please set environment variable: {provider.upper()}_API_KEY={api_key}")
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for provider."""
        try:
            import keyring
            key = keyring.get_password("bgpt", provider)
            if key:
                return key
        except Exception:
            pass
        return os.getenv(f"{provider.upper()}_API_KEY")
    
    def show_config(self) -> None:
        """Display current configuration."""
        print("Current Configuration:")
        print("=" * 20)
        for key, value in self._config.items():
            print(f"  {key}: {value}")
    
    def run_diagnostics(self) -> None:
        """Run system diagnostics."""
        print("🔍 System Diagnostics")
        print("=" * 20)
        
        # Check Python version
        import sys
        print(f"Python: {sys.version}")
        
        # Check core dependencies
        deps = {
            "rich": "Terminal UI",
            "click": "CLI framework", 
            "google-generativeai": "Gemini support",
            "openai": "OpenAI support"
        }
        
        for dep, description in deps.items():
            try:
                __import__(dep)
                print(f"✅ {dep}: installed ({description})")
            except ImportError:
                print(f"❌ {dep}: not installed ({description})")
        
        # Check API keys
        providers = ["gemini", "openai", "anthropic"]
        for provider in providers:
            key = self.get_api_key(provider)
            status = "configured" if key else "not configured"
            print(f"🔑 {provider} API key: {status}")
