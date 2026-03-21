"""
API call logger. Wraps OpenAI client to count and log all API calls.

Usage:
    from optim.api_logger import get_logged_client, get_logged_async_client, get_call_count

    client = get_logged_client()       # sync
    client = get_logged_async_client()  # async

    # Use client normally...

    print(f"Total API calls: {get_call_count()}")
"""

import os
import time
import threading
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

_LOG_FILE = Path(__file__).parent.parent / "api_calls.log"
_call_count = 0
_lock = threading.Lock()


def _log_call(model: str, call_type: str = "chat"):
    """Log an API call to file and increment counter."""
    global _call_count
    with _lock:
        _call_count += 1
        count = _call_count
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    line = f"{ts}\t{model}\t{call_type}\t{count}\n"
    with open(_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


def get_call_count() -> int:
    """Return total API calls made in this process."""
    return _call_count


def reset_log():
    """Reset the log file and counter."""
    global _call_count
    _call_count = 0
    if _LOG_FILE.exists():
        _LOG_FILE.unlink()
    with open(_LOG_FILE, "w", encoding="utf-8") as f:
        f.write("timestamp\tmodel\ttype\tcount\n")


def get_logged_client():
    """Get a sync OpenAI client that logs all calls."""
    from openai import OpenAI

    real_client = OpenAI(
        base_url=os.getenv("AZURE_FOUNDRY_BASE_URL"),
        api_key=os.getenv("AZURE_INFERENCE_CREDENTIAL"),
    )

    original_create = real_client.chat.completions.create

    def logged_create(*args, **kwargs):
        model = kwargs.get("model", args[0] if args else "unknown")
        _log_call(model)
        return original_create(*args, **kwargs)

    real_client.chat.completions.create = logged_create
    return real_client


def get_logged_async_client():
    """Get an async OpenAI client that logs all calls."""
    from openai import AsyncOpenAI

    real_client = AsyncOpenAI(
        base_url=os.getenv("AZURE_FOUNDRY_BASE_URL"),
        api_key=os.getenv("AZURE_INFERENCE_CREDENTIAL"),
    )

    original_create = real_client.chat.completions.create

    async def logged_create(*args, **kwargs):
        model = kwargs.get("model", args[0] if args else "unknown")
        _log_call(model)
        return await original_create(*args, **kwargs)

    real_client.chat.completions.create = logged_create
    return real_client


# Auto-initialize log file on import
if not _LOG_FILE.exists():
    reset_log()
