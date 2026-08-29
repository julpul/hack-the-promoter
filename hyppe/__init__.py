"""hyppe -- klient i narzedzia do hackathonu "Hack the Promoter" (iGEM Warsaw 2026)."""

from .client import ApiError, Client, rownolegle
from .config import Config, load_dotenv

__all__ = ["Client", "ApiError", "Config", "load_dotenv", "rownolegle"]
__version__ = "0.1.0"
