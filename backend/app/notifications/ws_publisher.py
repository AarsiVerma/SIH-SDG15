"""Notification providers."""
from typing import Protocol, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification, NotificationChannel


class AlertMessage:
    def __init__(
        self,
        topic: str,
        type: str,
        payload: dict,
        incident_id: Optional[UUID] = None,
        language_key: str = "",
    ):
        self.topic = topic
        self.type = type
        self.payload = payload
        self.incident_id = incident_id
        self.language_key = language_key


class NotificationProvider(Protocol):
    async def notify(self, alert: AlertMessage, db: AsyncSession) -> None: ...


class LogNotificationProvider:
    """Logs notifications to stdout."""

    async def notify(self, alert: AlertMessage, db: AsyncSession) -> None:
        print(f"NOTIFICATION [{alert.topic}]: {alert.payload}")


class WsNotificationProvider:
    """Sends notifications via WebSocket hub."""

    async def notify(self, alert: AlertMessage, db: AsyncSession) -> None:
        from app.ws.hub import hub
        await hub.broadcast(alert.topic, {
            "type": alert.type,
            "incident_id": str(alert.incident_id) if alert.incident_id else None,
            "language_key": alert.language_key,
            **alert.payload,
        })

        # Also persist to DB
        notif = Notification(
            incident_id=alert.incident_id,
            channel=NotificationChannel.WS,
            title=alert.payload.get("title", "Update"),
            body=alert.payload.get("body", str(alert.payload)),
            language_key=alert.language_key,
        )
        db.add(notif)
        await db.commit()


class CompositeNotificationProvider:
    """Combines multiple providers."""

    def __init__(self, *providers: NotificationProvider):
        self.providers = providers

    async def notify(self, alert: AlertMessage, db: AsyncSession) -> None:
        for p in self.providers:
            await p.notify(alert, db)