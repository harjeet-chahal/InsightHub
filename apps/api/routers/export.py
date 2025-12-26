from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os

from apps.api.db.session import get_db
from apps.api.db import models
from apps.api.services import export

router = APIRouter(
    prefix="/workspaces",
    tags=["export"]
)

@router.get("/{workspace_id}/export/csv")
async def export_csv(workspace_id: str, db: AsyncSession = Depends(get_db)):
    workspace = await db.get(models.Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    zip_buffer = await export.generate_csv_export(workspace_id, db)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=workspace_{workspace_id}_export.zip"}
    )

@router.get("/{workspace_id}/export/pptx")
async def export_pptx(workspace_id: str, db: AsyncSession = Depends(get_db)):
    workspace = await db.get(models.Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    pptx_path = await export.generate_pptx_export(workspace_id, db)
    
    return FileResponse(
        pptx_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"insight_hub_report_{workspace_id}.pptx",
        background=asyncio.create_task(cleanup_file(pptx_path)) # Cleanup might need custom handling in FastAPI
    )

import asyncio
async def cleanup_file(path: str):
    # Small delay to ensure file is sent
    await asyncio.sleep(10)
    try:
        os.remove(path)
    except:
        pass
