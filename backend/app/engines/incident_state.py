"""Incident state machine."""
from enum import Enum
from typing import Set

from app.models.enums import IncidentStatus, UserRole


# Valid transitions: (from_status, to_status) -> allowed_roles
TRANSITIONS = {
    (IncidentStatus.NEW, IncidentStatus.ACKNOWLEDGED): {UserRole.RANGER, UserRole.FOREST_OFFICER, UserRole.ADMIN},
    (IncidentStatus.NEW, IncidentStatus.INVESTIGATING): {UserRole.FOREST_OFFICER, UserRole.ADMIN},
    (IncidentStatus.ACKNOWLEDGED, IncidentStatus.INVESTIGATING): {UserRole.RANGER, UserRole.FOREST_OFFICER, UserRole.ADMIN},
    (IncidentStatus.ACKNOWLEDGED, IncidentStatus.DISPATCHED): {UserRole.FOREST_OFFICER, UserRole.ADMIN},
    (IncidentStatus.INVESTIGATING, IncidentStatus.DISPATCHED): {UserRole.FOREST_OFFICER, UserRole.ADMIN},
    (IncidentStatus.INVESTIGATING, IncidentStatus.RESOLVED): {UserRole.FOREST_OFFICER, UserRole.ADMIN},
    (IncidentStatus.DISPATCHED, IncidentStatus.INVESTIGATING): {UserRole.FOREST_OFFICER, UserRole.ADMIN},
    (IncidentStatus.DISPATCHED, IncidentStatus.RESOLVED): {UserRole.FOREST_OFFICER, UserRole.ADMIN},
    (IncidentStatus.RESOLVED, IncidentStatus.CLOSED): {UserRole.FOREST_OFFICER, UserRole.ADMIN},
    (IncidentStatus.RESOLVED, IncidentStatus.INVESTIGATING): {UserRole.ADMIN},  # reopen
    (IncidentStatus.CLOSED, IncidentStatus.INVESTIGATING): {UserRole.ADMIN},  # admin reopen
}


def can_transition(from_status: IncidentStatus, to_status: IncidentStatus, role: UserRole) -> bool:
    """Check if a role can transition between statuses."""
    allowed = TRANSITIONS.get((from_status, to_status), set())
    return role in allowed


def validate_transition(from_status: IncidentStatus, to_status: IncidentStatus, role: UserRole) -> None:
    """Raise AppError if transition is invalid."""
    from app.core.errors import AppError, ErrorCode

    if not can_transition(from_status, to_status, role):
        raise AppError(
            ErrorCode.FORBIDDEN,
            f"Invalid transition: {from_status.value} -> {to_status.value} for role {role.value}",
        )


# For cases without role (e.g., auto-transition from SOS)
def is_valid_transition(from_status: IncidentStatus, to_status: IncidentStatus) -> bool:
    """Check if transition is valid for any role."""
    return (from_status, to_status) in TRANSITIONS