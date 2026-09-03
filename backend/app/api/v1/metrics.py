"""Prometheus-style metrics endpoint (MVP)."""
import time
from functools import wraps
from typing import Dict

from fastapi import APIRouter, Depends, Response
from app.api.deps import RequireAdmin
from app.models import User

router = APIRouter(prefix="/metrics", tags=["metrics"])

# Simple in-memory counters
_counters: Dict[str, float] = {}
_histograms: Dict[str, list] = {}


def inc_counter(name: str, value: float = 1.0):
    _counters[name] = _counters.get(name, 0) + value


def observe_histogram(name: str, value: float):
    if name not in _histograms:
        _histograms[name] = []
    _histograms[name].append(value)
    # Keep last 1000
    if len(_histograms[name]) > 1000:
        _histograms[name] = _histograms[name][-1000:]


def metrics_timer(name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                observe_histogram(f"{name}_duration_seconds", time.perf_counter() - start)
        return wrapper
    return decorator


@router.get("")
async def metrics(
    current_user: User = Depends(RequireAdmin),
) -> Response:
    """Prometheus text format."""
    lines = []

    # Counters
    for name, value in _counters.items():
        lines.append(f'# TYPE {name} counter')
        lines.append(f'{name} {value}')

    # Histograms (simple summary)
    for name, values in _histograms.items():
        if not values:
            continue
        lines.append(f'# TYPE {name} summary')
        count = len(values)
        total = sum(values)
        lines.append(f'{name}_count {count}')
        lines.append(f'{name}_sum {total:.6f}')
        # Quantiles (approx)
        sorted_vals = sorted(values)
        for q in [0.5, 0.9, 0.99]:
            idx = int(len(sorted_vals) * q)
            lines.append(f'{name}{{quantile="{q}"}} {sorted_vals[idx]:.6f}')

    return Response(content="\n".join(lines) + "\n", media_type="text/plain")


# Public helpers for other modules
__all__ = ["inc_counter", "observe_histogram", "metrics_timer"]