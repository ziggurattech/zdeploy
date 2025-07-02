"""Configuration loader for zdeploy."""
# pylint: disable=too-many-instance-attributes

from dataclasses import dataclass
from json import loads
from os.path import isfile
from typing import Any, Dict, cast

from zdeploy.utils import str2bool


@dataclass  # pylint: disable=too-many-instance-attributes
class Config:
    """Simple container for configuration settings."""

    configs: str = "configs"
    recipes: str = "recipes"
    cache: str = "cache"
    logs: str = "logs"
    installer: str = "apt-get install -y"
    force: bool = False
    user: str = "root"
    password: str | None = None
    port: int = 22


def load(cfg_path: str = "config.json") -> Config:
    """Load configuration from ``cfg_path`` or return defaults."""

    # Initiate an empty config dictionary in case a config file isn't present.
    cfg: Dict[str, Any] = {}

    if isfile(cfg_path):
        # Load data in JSON form.
        with open(cfg_path, "r", encoding="utf-8") as fp:
            cfg = loads(fp.read())

    # Set defaults
    cfg["configs"] = cfg.get("configs", Config.configs)
    cfg["recipes"] = cfg.get("recipes", Config.recipes)
    cfg["cache"] = cfg.get("cache", Config.cache)
    cfg["logs"] = cfg.get("logs", Config.logs)

    # Default installer is apt-get. This is used for virtual
    # recipes (recipes that aren't defined by a directory
    # structure).
    cfg["installer"] = cfg.get("installer", Config.installer)

    # Force is disabled by default. This sets the behavior to
    # only deploy undeployed recipes and/or pick up where a
    # previous deployment was halted or had crashed.
    force_value = cfg.get("force", Config.force)
    if isinstance(force_value, str):
        force_value = str2bool(force_value)
    cfg["force"] = force_value

    # Default username is root
    cfg["user"] = cfg.get("user", Config.user)

    # The default is no password (private key present)
    cfg["password"] = cfg.get("password", Config.password)

    cfg["port"] = cfg.get("port", Config.port)

    # Convert the dictionary into a Config instance to allow attribute access
    return Config(**cast(Dict[str, Any], cfg))
