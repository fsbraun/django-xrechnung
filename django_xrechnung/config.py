"""
Configuration module for django-xrechnung.

This module provides configuration options that can be customized
through Django settings or pyproject.toml.
"""

from django.conf import settings
from typing import Dict, Any
import os


class XRechnungConfig:
    """Configuration class for django-xrechnung app."""
    
    # Default configuration values
    DEFAULT_CONFIG = {
        "CURRENCY": "EUR",
        "DEFAULT_TAX_RATE": 19.00,
        "PAGINATION_SIZE": 20,
        "XML_VALIDATION": True,
        "REQUIRE_TAX_ID": False,
        "DATE_FORMAT": "%Y-%m-%d",
        "DECIMAL_PLACES": 2,
        "MAX_INVOICE_NUMBER_LENGTH": 100,
        "ALLOW_NEGATIVE_AMOUNTS": False,
        "XML_NAMESPACE": {
            "ubl": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        }
    }
    
    def __init__(self):
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from Django settings and pyproject.toml."""
        config = self.DEFAULT_CONFIG.copy()
        
        # Load from Django settings if available
        django_config = getattr(settings, "DJANGO_XRECHNUNG", {})
        config.update(django_config)
        
        # Load from pyproject.toml if available
        pyproject_config = self._load_from_pyproject()
        if pyproject_config:
            config.update(pyproject_config)
        
        return config
    
    def _load_from_pyproject(self) -> Dict[str, Any]:
        """Load configuration from pyproject.toml file."""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                # Fallback if neither tomllib nor tomli is available
                return {}
        
        try:
            # Look for pyproject.toml in the project root
            project_root = getattr(settings, "BASE_DIR", os.getcwd())
            pyproject_path = os.path.join(project_root, "pyproject.toml")
            
            if os.path.exists(pyproject_path):
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                
                # Extract django-xrechnung specific configuration
                tool_config = data.get("tool", {})
                return tool_config.get("django-xrechnung", {})
        
        except Exception:
            # If there's any error reading the file, continue with defaults
            pass
        
        return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def __getattr__(self, name: str) -> Any:
        """Allow accessing config values as attributes."""
        if name.upper() in self._config:
            return self._config[name.upper()]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    @property
    def currency(self) -> str:
        """Get the default currency."""
        return self.get("CURRENCY", "EUR")
    
    @property
    def default_tax_rate(self) -> float:
        """Get the default tax rate."""
        return self.get("DEFAULT_TAX_RATE", 19.00)
    
    @property
    def pagination_size(self) -> int:
        """Get the pagination size for list views."""
        return self.get("PAGINATION_SIZE", 20)
    
    @property
    def xml_validation(self) -> bool:
        """Get whether XML validation is enabled."""
        return self.get("XML_VALIDATION", True)
    
    @property
    def require_tax_id(self) -> bool:
        """Get whether tax ID is required."""
        return self.get("REQUIRE_TAX_ID", False)


# Global configuration instance
config = XRechnungConfig()