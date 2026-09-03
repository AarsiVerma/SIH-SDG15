"""Config tests."""
import os
from pathlib import Path

import pytest

from app.core.config import Settings, get_settings, check_secret_key


def test_settings_load_from_env(monkeypatch):
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("SAMPLE_FPS", "5.0")
    s = Settings()
    assert s.debug is True
    assert s.sample_fps == 5.0


def test_get_settings_cached():
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2


def test_secret_key_check_in_production(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SECRET_KEY", "changeme-in-production")
    # clear lru_cache so new env is picked up
    get_settings.cache_clear()
    with pytest.raises(RuntimeError):
        check_secret_key()


def test_env_example_exists():
    assert Path(".env.example").exists()