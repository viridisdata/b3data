import configparser
import os
from pathlib import Path

DATA_DIR = Path(os.getenv("DATA_DIR", "~/data")).expanduser()
DEFAULT_OUTPUT_DIR = DATA_DIR / "raw" / "b3" / "cotacaohistorica"

CONFIG_DIR = Path(os.getenv("CONFIG_DIR", "~/.config")).expanduser()

_config_filepath = CONFIG_DIR / "b3-cotacaohistorica" / "config.ini"
if not _config_filepath.exists():
    raise FileNotFoundError("Configuration file not found")
_config = configparser.ConfigParser()
_config.read(_config_filepath)

USER_AGENT = _config["DEFAULT"]["USER_AGENT"]

HTTP_HEADERS = {
    "User-Agent": USER_AGENT,
}
