"""String catalog + forbidden-term checker (VR-002 contract)."""
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = ROOT / "config" / "language_catalog.yaml"

FORBIDDEN_TERMS = ("poacher", "poaching", "criminal", "guilty", "smuggler", "terrorist")


def load_catalog() -> dict[str, Any]:
    return yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))


def assert_copy_allowed(text: str) -> None:
    """Raise if automated copy contains forbidden terms.

    Forbidden terms must only ever appear in comments/documentation that
    explains they are forbidden.
    """
    lowered = text.lower()
    for term in FORBIDDEN_TERMS:
        if term in lowered:
            raise ValueError(f"forbidden term in copy: {term!r}")


def message_for(language_key: str) -> dict[str, str]:
    catalog = load_catalog()
    try:
        return catalog["messages"][language_key]
    except KeyError:
        raise KeyError(f"language_key {language_key!r} missing from catalog") from None