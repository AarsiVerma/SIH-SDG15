"""Worker process stub — logs idle until pipeline is wired (VR-029+)."""
import asyncio
import logging

from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()
logger = logging.getLogger("app.worker")
settings = get_settings()


async def main() -> None:
    logger.info("Worker started (demo_mode=%s, edge_mode=%s)", settings.demo_mode, settings.edge_mode)
    while True:
        logger.info("Worker idle — waiting for ingest jobs")
        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())