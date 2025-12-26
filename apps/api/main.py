from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from apps.api.core.config import settings
from apps.api.worker import celery_app
from apps.api.routers import workspaces, sources, search, scorecards, export

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(workspaces.router, prefix=settings.API_V1_STR)
app.include_router(sources.router, prefix=settings.API_V1_STR)
app.include_router(search.router, prefix=settings.API_V1_STR)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": f"An unexpected error occurred: {str(exc)}"},
    )

@app.get("/")
def root():
    return {"message": "Welcome to InsightHub API"}

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "celery_broker": settings.CELERY_BROKER_URL is not None
    }

# Example Celery task trigger
@app.post("/test-celery")
def trigger_test_celery(word: str):
    task = celery_app.send_task("apps.api.worker.test_celery", args=[word])
    return {"task_id": task.id}
