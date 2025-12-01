import yaml
from pathlib import Path

def load_config(path: str = "config/config.yaml") -> dict:
    """
    Load a YAML configuration file and return its contents as a dictionary.
    Parameters
    ----------
    path : str, optional
        Path to the YAML configuration file to load. Defaults to "config/config.yaml".
    Returns
    -------
    dict
        Parsed configuration data.
    Raises
    ------
    FileNotFoundError
        If the file at `path` does not exist.
    yaml.YAMLError
        If the file cannot be parsed as valid YAML.
    """
    
    with open(path) as f:
        return yaml.safe_load(f)
config = load_config()