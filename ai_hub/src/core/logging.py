from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(log_dir: Path) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("ai_hub")
    logger.setLevel(logging.INFO)
    fh = RotatingFileHandler(log_dir / "ai-hub.log", maxBytes=2_000_000, backupCount=3)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger
