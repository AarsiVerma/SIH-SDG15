# VANRAKSHA AI — Terminology Specification

The system never presents model inference as fact. All automated copy must be
written so that a reader understands the difference between what was observed
and what still requires human verification.

## Four Layers

| Layer | Meaning | Example |
|-------|---------|---------|
| Detection | What a model observed in one frame | "Person detected" |
| Inference | A synthesized observation across frames/context | "Restricted-zone activity detected" |
| Risk | Score + factors, never certainty | "High-risk suspicious activity detected; ranger verification required." |
| Human verification | Confirmed fact after an officer acts | "Suspicious activity confirmed by ranger" |

## Event language_key values

The following `language_key` values are the only event keys the system may emit
(auto-generated copy). Titles/bodies are resolved from `config/language_catalog.yaml`.

- `person_detected`
- `vehicle_detected`
- `animal_detected`
- `smoke_detected`
- `fire_detected`
- `suspicious_activity`
- `suspicious_activity_high_risk`
- `wildlife_unusual_movement`
- `camera_tampering_suspected`
- `camera_failure_suspected`
- `ranger_sos`
- `restricted_zone_activity`

## Forbidden terms

The following substrings must never appear in automated copy (titles, bodies,
banners, WebSocket payloads, notification text):

`poacher`, `poaching`, `criminal`, `guilty`, `smuggler`, `terrorist`

These words may appear ONLY inside comments or documentation that explains they
are forbidden. `backend/app/core/language.py` provides
`assert_copy_allowed(text)` used by tests and at publish time.

## Required wording

- **Evidence disclaimer**: "Timestamped evidence supporting investigation, subject to applicable procedures."
- **Wildlife**: species is always `unknown` unless a verified classifier sets it; display "Animal detected (species unverified)."
- **Unusual movement**: "Unusual movement detected; ranger verification recommended."
- **HIGH / CRITICAL risk**: every user-facing template must include verification language ("Ranger verification required." / "verification required").
- **Fire**: no spread physics; never claim direction/speed of spread.
- **Incidents**: AI may create and escalate incidents; AI may never set an incident to CLOSED.