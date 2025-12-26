from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel
from typing import List, Optional

from apps.api.db.session import get_db
from apps.api.db import models
from apps.api.services.embeddings import get_embedding

router = APIRouter(
    prefix="/workspaces",
    tags=["search"]
)

class SearchResult(BaseModel):
    chunk_text: str
    source_title: str
    source_url: Optional[str] = None
    document_type: str
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]

@router.post("/{workspace_id}/search", response_model=SearchResponse)
async def search_workspace(
    workspace_id: str, 
    query: str, 
    limit: int = 5, 
    filters: Optional[dict] = None, 
    db: AsyncSession = Depends(get_db)
):
    # Verify workspace
    workspace = await db.get(models.Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Generate query embedding
    query_embedding = get_embedding(query)

    # Base query
    stmt = (
        select(models.Chunk, models.Document, models.Source, models.Chunk.embedding.cosine_distance(query_embedding).label("distance"))
        .join(models.Document, models.Chunk.document_id == models.Document.id)
        .join(models.Source, models.Document.source_id == models.Source.id)
        .where(models.Source.workspace_id == workspace_id)
    )

    # Apply Metadata Filters
    # filters example: {"brand": "BrandA", "source_type": "url"}
    # Note: Document metadata is JSONB, so we can filter inside it for brands etc.
    if filters:
        for key, value in filters.items():
            if key == "brand":
                # JSONB containment or specific key check
                stmt = stmt.where(models.Document.metadata_['brand'].astext == value)
            # Add other filters as needed

    stmt = stmt.order_by(models.Chunk.embedding.cosine_distance(query_embedding)).limit(limit)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    search_results = []
    for chunk, doc, source, distance in rows:
        # Distance is cosine distance (0 to 2), similarity is 1 - distance
        score = 1 - distance
        
        search_results.append(SearchResult(
            chunk_text=chunk.text,
            source_title=source.title,
            source_url=source.url,
            document_type=doc.doc_type,
            score=score
        ))

    return SearchResponse(results=search_results)
