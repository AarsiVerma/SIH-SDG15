"""VR-002 — language catalog contract tests.

Loads config/language_catalog.yaml and asserts:
- all required language keys exist
- every risk-layer message body requests verification
- forbidden terms never appear in message title/body
- forbidden terms list is exactly as specified in docs/LANGUAGE.md
"""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
CATALOG = ROOT / "config" / "language_catalog.yaml"

REQUIRED_KEYS = {
    "person_detected",
    "vehicle_detected",
    "animal_detected",
    "smoke_detected",
    "fire_detected",
    "suspicious_activity",
    "suspicious_activity_high_risk",
    "wildlife_unusual_movement",
    "camera_tampering_suspected",
    "camera_failure_suspected",
    "ranger_sos",
    "restricted_zone_activity",
}

EXPECTED_FORBIDDEN = ["poacher", "poaching", "criminal", "guilty", "smuggler", "terrorist"]

RISK_LAYER_KEYS = {
    "fire_detected",
    "suspicious_activity",
    "suspicious_activity_high_risk",
    "wildlife_unusual_movement",
    "camera_tampering_suspected",
    "camera_failure_suspected",
    "ranger_sos",
    "restricted_zone_activity",
}


def _load() -> dict:
    return yaml.safe_load(CATALOG.read_text())


def test_all_required_keys_present():
    data = _load()
    assert set(data["messages"].keys()) == REQUIRED_KEYS


def test_risk_layer_messages_request_verification():
    data = _load()
    for key in RISK_LAYER_KEYS:
        body = data["messages"][key]["body"]
        assert "verification" in body.lower(), f"{key} body must request verification"


def test_forbidden_terms_do_not_appear_in_copy():
    data = _load()
    forbidden = data["forbidden_terms"]
    for key, msg in data["messages"].items():
        text = f"{msg['title']} {msg['body']}".lower()
        for term in forbidden:
            assert term not in text, f"forbidden term '{term}' in message {key}"


def test_forbidden_terms_list_matches_docs():
    data = _load()
    assert set(data["forbidden_terms"]) == set(EXPECTED_FORBIDDEN)


def test_evidence_and_wildlife_disclaimers():
    data = _load()
    assert "subject to applicable procedures" in data["disclaimers"]["evidence"]
    assert "ranger verification" in data["disclaimers"]["wildlife"]