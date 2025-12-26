from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from apps.api.db.session import get_db
from apps.api.db import models
from apps.api import schemas
from apps.api.worker import celery_app

router = APIRouter(
    prefix="", # Routes are split between /workspaces and /scorecards
    tags=["scorecards"]
)

@router.post("/workspaces/{workspace_id}/scorecards", response_model=schemas.ScorecardResponse, status_code=status.HTTP_201_CREATED)
async def create_scorecard(workspace_id: str, scorecard: schemas.ScorecardCreate, db: AsyncSession = Depends(get_db)):
    workspace = await db.get(models.Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    new_scorecard = models.Scorecard(
        workspace_id=workspace_id,
        name=scorecard.name,
        config=scorecard.config
    )
    db.add(new_scorecard)
    await db.commit()
    await db.refresh(new_scorecard)
    return new_scorecard

@router.get("/workspaces/{workspace_id}/scorecards", response_model=List[schemas.ScorecardResponse])
async def list_scorecards(workspace_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Scorecard).where(models.Scorecard.workspace_id == workspace_id)
    )
    return result.scalars().all()

@router.get("/scorecards/{scorecard_id}", response_model=schemas.ScorecardResponse)
async def get_scorecard(scorecard_id: str, db: AsyncSession = Depends(get_db)):
    scorecard = await db.get(models.Scorecard, scorecard_id)
    if not scorecard:
        raise HTTPException(status_code=404, detail="Scorecard not found")
    return scorecard

@router.post("/scorecards/{scorecard_id}/run", response_model=schemas.IngestResponse)
async def run_scorecard(scorecard_id: str, db: AsyncSession = Depends(get_db)):
    scorecard = await db.get(models.Scorecard, scorecard_id)
    if not scorecard:
        raise HTTPException(status_code=404, detail="Scorecard not found")
        
    task = celery_app.send_task("apps.api.worker.run_scorecard", args=[scorecard_id])
    return {"message": "Scorecard calculation started", "task_id": task.id}

@router.get("/scorecards/{scorecard_id}/results", response_model=List[schemas.ScorecardResultResponse])
async def get_scorecard_results(scorecard_id: str, db: AsyncSession = Depends(get_db)):
    scorecard = await db.get(models.Scorecard, scorecard_id)
    if not scorecard:
        raise HTTPException(status_code=404, detail="Scorecard not found")
        
    result = await db.execute(
        select(models.ScorecardResult)
        .where(models.ScorecardResult.scorecard_id == scorecard_id)
    )
    return result.scalars().all()
