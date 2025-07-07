import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path

from .settings import settings

if settings.ENV.lower() == "development":
    log_level = "DEBUG"
else:
    log_level = "INFO"


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

numeric_level = getattr(logging, log_level)

file_handler = RotatingFileHandler(
    LOG_DIR / "app.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding='utf-8'
)
file_handler.setLevel(numeric_level)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(numeric_level)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger = logging.getLogger("app")
logger.setLevel(numeric_level)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.propagate = False