from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import shutil
import os

from apps.api.db.session import get_db
from apps.api.db import models
from apps.api import schemas

router = APIRouter(
    prefix="/sources",
    tags=["sources"]
)

@router.post("/url", response_model=schemas.SourceResponse, status_code=status.HTTP_201_CREATED)
async def add_url_source(source: schemas.SourceCreateURL, workspace_id: str, db: AsyncSession = Depends(get_db)):
    # Basic check for workspace
    workspace = await db.get(models.Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    new_source = models.Source(
        workspace_id=workspace_id,
        type="url",
        title=source.title,
        url=str(source.url)
    )
    db.add(new_source)
    await db.commit()
    await db.refresh(new_source)
    return new_source

@router.post("/note", response_model=schemas.SourceResponse, status_code=status.HTTP_201_CREATED)
async def add_note_source(source: schemas.SourceCreateNote, workspace_id: str, db: AsyncSession = Depends(get_db)):
    workspace = await db.get(models.Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    new_source = models.Source(
        workspace_id=workspace_id,
        type="note",
        title=source.title,
        raw_text=source.raw_text
    )
    db.add(new_source)
    await db.commit()
    await db.refresh(new_source)
    return new_source

@router.post("/upload", response_model=schemas.SourceResponse, status_code=status.HTTP_201_CREATED)
async def upload_file_source(
    workspace_id: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    workspace = await db.get(models.Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Save file locally (in production, use S3/Blob storage)
    upload_dir = "/app/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{workspace_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    source_type = "pdf" if file.filename.endswith(".pdf") else "csv" if file.filename.endswith(".csv") else "file"

    new_source = models.Source(
        workspace_id=workspace_id,
        type=source_type,
        title=title,
        filename=file.filename,
        # In a real app we'd store the path or S3 key
        raw_text=f"loc:{file_path}" 
    )
    db.add(new_source)
    await db.commit()
    await db.refresh(new_source)
    return new_source
