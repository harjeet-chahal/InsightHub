from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from apps.api.db.session import get_db
from apps.api.db import models
from apps.api import schemas
from apps.api.worker import celery_app

router = APIRouter(
    prefix="/workspaces",
    tags=["workspaces"]
)

@router.post("/", response_model=schemas.WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(workspace: schemas.WorkspaceCreate, db: AsyncSession = Depends(get_db)):
    new_workspace = models.Workspace(name=workspace.name)
    db.add(new_workspace)
    await db.commit()
    await db.refresh(new_workspace)
    return new_workspace

@router.get("/", response_model=List[schemas.WorkspaceResponse])
async def get_workspaces(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Workspace))
    workspaces = result.scalars().all()
    return workspaces

@router.get("/{workspace_id}/sources", response_model=List[schemas.SourceResponse])
async def get_workspace_sources(workspace_id: str, db: AsyncSession = Depends(get_db)):
    # Verify workspace exists
    workspace = await db.get(models.Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    result = await db.execute(select(models.Source).where(models.Source.workspace_id == workspace_id))
    sources = result.scalars().all()
    return sources

@router.post("/{workspace_id}/ingest", response_model=schemas.IngestResponse)
async def ingest_workspace(workspace_id: str, db: AsyncSession = Depends(get_db)):
    workspace = await db.get(models.Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Trigger background task
    task = celery_app.send_task("apps.api.worker.process_workspace_sources", args=[workspace_id])
    return {"message": "Ingestion started", "task_id": task.id}

@router.post("/{workspace_id}/analytics", response_model=schemas.IngestResponse)
async def trigger_analytics(workspace_id: str, db: AsyncSession = Depends(get_db)):
    workspace = await db.get(models.Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    task = celery_app.send_task("apps.api.worker.run_analytics", args=[workspace_id])
    return {"message": "Analytics job started", "task_id": task.id}

@router.get("/{workspace_id}/dashboard")
async def get_dashboard(workspace_id: str, db: AsyncSession = Depends(get_db)):
    workspace = await db.get(models.Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    result = await db.execute(
        select(models.Insight)
        .where(models.Insight.workspace_id == workspace_id)
        .order_by(models.Insight.created_at.desc())
    )
    insights = result.scalars().all()
    
    dashboard_data = {
        "stats": None,
        "claims": None,
        "trends": None,
        "other": []
    }
    
    # Only take the latest of each kind if multiple exist (though we wipe clean in service)
    for insight in insights:
        if insight.kind == 'stats' and not dashboard_data['stats']:
            dashboard_data['stats'] = insight.metrics
        elif insight.kind == 'claims' and not dashboard_data['claims']:
            dashboard_data['claims'] = insight.metrics
        elif insight.kind == 'trends' and not dashboard_data['trends']:
            dashboard_data['trends'] = insight.metrics
        else:
            dashboard_data['other'].append({
                "title": insight.title,
                "summary": insight.summary,
                "metrics": insight.metrics
            })
@router.get("/{workspace_id}/themes")
async def get_themes(workspace_id: str, db: AsyncSession = Depends(get_db)):
    workspace = await db.get(models.Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    result = await db.execute(
        select(models.Insight)
        .where(models.Insight.workspace_id == workspace_id)
        .where(models.Insight.kind == 'theme')
        .order_by(models.Insight.metrics['count'].desc())
    )
    themes = result.scalars().all()
    return themes
