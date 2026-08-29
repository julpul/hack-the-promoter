"""Konfiguracja: czytanie .env bez zewnetrznych zaleznosci."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_URL = "https://hyppe.futura.foundation"
DEFAULT_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"
)


def load_dotenv(path: Path | str | None = None, override: bool = False) -> dict:
    """Wczytuje proste pary KLUCZ=wartosc z .env do os.environ.

    Nie nadpisuje zmiennych juz ustawionych w srodowisku (chyba ze override=True),
    dzieki czemu `HYPPE_API_KEY=... python -m hyppe ...` zawsze wygrywa.
    """
    path = Path(path) if path else REPO_ROOT / ".env"
    wczytane: dict[str, str] = {}
    if not path.exists():
        return wczytane
    for linia in path.read_text(encoding="utf-8").splitlines():
        linia = linia.strip()
        if not linia or linia.startswith("#") or "=" not in linia:
            continue
        klucz, _, wartosc = linia.partition("=")
        klucz, wartosc = klucz.strip(), wartosc.strip().strip('"').strip("'")
        wczytane[klucz] = wartosc
        if override or klucz not in os.environ:
            os.environ[klucz] = wartosc
    return wczytane


@dataclass
class Config:
    api_key: str
    url: str = DEFAULT_URL
    timeout: float = 900.0
    retries: int = 6
    user_agent: str = DEFAULT_UA

    @classmethod
    def from_env(cls, api_key: str | None = None, url: str | None = None) -> "Config":
        load_dotenv()
        key = api_key or os.environ.get("HYPPE_API_KEY", "")
        if not key:
            raise RuntimeError(
                "Brak klucza API. Ustaw HYPPE_API_KEY w .env "
                "(cp .env.example .env) albo podaj --api-key."
            )
        return cls(
            api_key=key,
            url=url or os.environ.get("HYPPE_URL", DEFAULT_URL),
            timeout=float(os.environ.get("HYPPE_TIMEOUT", 900)),
            retries=int(os.environ.get("HYPPE_RETRIES", 6)),
            user_agent=os.environ.get("HYPPE_USER_AGENT") or DEFAULT_UA,
        )
