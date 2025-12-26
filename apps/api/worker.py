from celery import Celery
from apps.api.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.task_routes = {
    "apps.api.worker.test_celery": "main-queue",
    "apps.api.worker.process_workspace_sources": "main-queue"
}

@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"

@celery_app.task(acks_late=True)
def process_workspace_sources(workspace_id: str):
    import asyncio
    from sqlalchemy import select
    from apps.api.db.session import AsyncSessionLocal
    from apps.api.db import models
    from apps.api.services import ingestion

    async def _run():
        async with AsyncSessionLocal() as db:
            # Find pending sources
            result = await db.execute(
                select(models.Source)
                .where(models.Source.workspace_id == workspace_id)
                .where(models.Source.status == "pending")
            )
            sources = result.scalars().all()
            
            results = []
            for source in sources:
                await ingestion.process_source(source.id, db)
                results.append(source.id)
            return f"Processed {len(results)} sources"

    return asyncio.run(_run())

@celery_app.task(acks_late=True)
def run_analytics(workspace_id: str):
    import asyncio
    from apps.api.db.session import AsyncSessionLocal
    from apps.api.services import analytics

    async def _run():
        async with AsyncSessionLocal() as db:
            await analytics.run_workspace_analytics(workspace_id, db)
            return "Analytics completed"

    return asyncio.run(_run())
