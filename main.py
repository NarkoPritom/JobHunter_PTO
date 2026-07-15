from __future__ import annotations

import asyncio

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config.settings import settings
from app.database.db import init_db
from app.scheduler.jobs import search_and_notify
from app.telegram_bot.bot import build_application
from app.utils.logging import configure_logging

logger = structlog.get_logger(__name__)


async def main() -> None:
    configure_logging()
    await init_db()

    app = build_application()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        search_and_notify,
        "interval",
        minutes=settings.search_interval_minutes,
        args=[app],
        next_run_time=None,  # run on first interval tick, not instantly; remove this line to run immediately
    )
    scheduler.start()

    async with app:
        await app.start()
        await app.updater.start_polling()
        logger.info("bot_started", interval_minutes=settings.search_interval_minutes)
        try:
            await asyncio.Event().wait()  # run forever
        finally:
            await app.updater.stop()
            await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
