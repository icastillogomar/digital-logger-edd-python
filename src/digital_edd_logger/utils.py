import os
import sys
from datetime import datetime, timezone, timedelta


class Colors:
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def _supports_color() -> bool:
    if os.getenv("NO_COLOR"):
        return False
    if os.getenv("FORCE_COLOR"):
        return True
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _colorize(text: str, color: str) -> str:
    if _supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text


def log_error(message: str) -> None:
    prefix = _colorize("[digital-edd-logger] ERROR:", Colors.RED + Colors.BOLD)
    print(f"{prefix} {message}", file=sys.stderr)


def log_warning(message: str) -> None:
    prefix = _colorize("[digital-edd-logger] WARNING:", Colors.YELLOW + Colors.BOLD)
    print(f"{prefix} {message}", file=sys.stderr)


def log_info(message: str) -> None:
    prefix = _colorize("[digital-edd-logger]", Colors.CYAN)
    print(f"{prefix} {message}")


def is_production() -> bool:
    env = os.getenv("ENV", "").lower()
    return env in ("prod", "production", "qas", "qa")


def get_mexico_time_as_utc() -> str:
    mexico_tz = timezone(timedelta(hours=-6))
    now = datetime.now(mexico_tz)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"
