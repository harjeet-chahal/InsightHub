from typing import List, Optional, Any, Dict
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
import uuid

# Base Schemas
class WorkspaceBase(BaseModel):
    name: str

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceResponse(WorkspaceBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SourceBase(BaseModel):
    title: str
    type: str # url, pdf, csv, note

class SourceCreateURL(SourceBase):
    type: str = "url"
    url: HttpUrl

class SourceCreateNote(SourceBase):
    type: str = "note"
    raw_text: str

# Used for multipart uploads - just metadata, file handled separately
class SourceResponse(SourceBase):
    id: str
    workspace_id: str
    url: Optional[str] = None
    filename: Optional[str] = None
    raw_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class IngestResponse(BaseModel):
    message: str
    task_id: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None

class ScorecardCreate(BaseModel):
    name: str
    config: Dict[str, Any] 
    # Config example: 
    # {
    #   "factors": [
    #      {"name": "Taste", "keywords": ["delicious", "yummy"], "weight": 0.4},
    #      {"name": "Price", "keywords": ["cheap", "expensive", "value"], "weight": 0.6}
    #   ]
    # }

class ScorecardResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    config: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ScorecardResultResponse(BaseModel):
    id: str
    scorecard_id: str
    brand: str
    results: Dict[str, Any] # {"overall": 85, "factors": {"Taste": 90, "Price": 80}}
    created_at: datetime

    class Config:
        from_attributes = True
