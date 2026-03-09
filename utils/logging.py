import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging() -> logging.Logger:
    """Configure logging to file and console."""

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "app.log"

    logger = logging.getLogger('agents_test')
    logger.setLevel(logging.INFO)
    logger.propagate = True
    
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5_000_000,   # 5MB
        backupCount=3
    )
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
