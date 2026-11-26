import logging
import sys
from pathlib import Path


def _make_console_safe(stream) -> None:
    """Make a console stream tolerate characters it cannot encode.

    Windows consoles frequently use a non-UTF-8 code page (for example
    cp936). LLM output can contain characters such as U+2011 that would
    otherwise raise UnicodeEncodeError inside logging and print a noisy
    traceback.

    Args:
        stream: The stream used by the console handler.
    """
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is None:
        return
    try:
        reconfigure(errors="replace")
    except Exception:
        pass


def setup_logger(
    name: str = "excel_agent",
    level: int = logging.INFO,
    log_file: str | None = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    _make_console_safe(sys.stdout)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_path), encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()
