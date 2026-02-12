import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILE_PATH = Path("/app/logs/mermaid_ai.log")
LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)


def setup_logger(name: str = __name__, log_level: int = logging.INFO) -> logging.Logger:
    """
    Настройка логгера: все логи только в файл с ротацией.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if not logger.hasHandlers():
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = RotatingFileHandler(
            filename=str(LOG_FILE_PATH),
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding="utf-8",
            delay=True,
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
