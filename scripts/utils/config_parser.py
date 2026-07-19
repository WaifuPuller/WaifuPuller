import yaml
from pathlib import Path
from typing import Dict, Any

def load_config(config_name: str) -> Dict[str, Any]:
    """Loads a YAML configuration file from the config/ directory."""
    config_path = Path("config") / f"{config_name}.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file {config_path} not found.")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_all_configs() -> Dict[str, Dict[str, Any]]:
    """Loads all known configuration files."""
    return {
        "profile": load_config("profile"),
        "theme": load_config("theme"),
        "tech_stack": load_config("tech_stack"),
        "projects": load_config("projects"),
        "animations": load_config("animations"),
        "portrait": load_config("portrait"),
    }
