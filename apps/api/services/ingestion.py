import requests
from bs4 import BeautifulSoup
import pdfplumber
import pandas as pd
import io
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List

from apps.api.db import models
from apps.api.core.text_utils import clean_text, chunk_text

async def process_source(source_id: str, db: AsyncSession):
    source = await db.get(models.Source, source_id)
    if not source:
        return

    try:
        source.status = "processing"
        await db.commit()

        if source.type == "url":
            await _process_url(source, db)
        elif source.type == "note":
            await _process_note(source, db)
        elif source.type == "pdf":
            await _process_pdf(source, db)
        elif source.type == "csv":
            await _process_csv(source, db)
        
        source.status = "completed"
        await db.commit()

    except Exception as e:
        await db.rollback()
        source.status = "failed"
        source.error_message = str(e)
        await db.commit()

from apps.api.services.embeddings import get_embedding

async def _create_chunks(document: models.Document, raw_text: str, db: AsyncSession):
    cleaned = clean_text(raw_text)
    text_chunks = chunk_text(cleaned)
    
    for i, text in enumerate(text_chunks):
        embedding = get_embedding(text)
        chunk = models.Chunk(
            document_id=document.id,
            chunk_index=i,
            text=text,
            embedding=embedding
        )
        db.add(chunk)

async def _process_url(source: models.Source, db: AsyncSession):
    response = requests.get(source.url, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()
    
    text = soup.get_text()
    
    doc = models.Document(
        source_id=source.id,
        doc_type="page",
        metadata_={"url": source.url, "title": soup.title.string if soup.title else source.title}
    )
    db.add(doc)
    await db.flush() # get doc.id
    
    await _create_chunks(doc, text, db)

async def _process_note(source: models.Source, db: AsyncSession):
    doc = models.Document(
        source_id=source.id,
        doc_type="note",
        metadata_={"title": source.title}
    )
    db.add(doc)
    await db.flush()
    
    await _create_chunks(doc, source.raw_text, db)

async def _process_pdf(source: models.Source, db: AsyncSession):
    # Depending on how raw_text is stored for file uploads (path vs content)
    # In routers/sources.py we stored "loc:/path/to/file"
    file_path = source.raw_text.replace("loc:", "")
    
    text_content = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text_content += page.extract_text() or ""
            
    doc = models.Document(
        source_id=source.id,
        doc_type="report",
        metadata_={"filename": source.filename}
    )
    db.add(doc)
    await db.flush()
    
    await _create_chunks(doc, text_content, db)

async def _process_csv(source: models.Source, db: AsyncSession):
    file_path = source.raw_text.replace("loc:", "")
    df = pd.read_csv(file_path)
    
    # Flexible column handling: look for 'review' or 'text' or assume all columns
    # We will treat each row as a document
    
    for _, row in df.iterrows():
        # Convert row to dict for metadata
        row_data = row.to_dict()
        
        # Try to find main text content
        content = ""
        possible_text_cols = ['review', 'text', 'content', 'body', 'review_text']
        for col in possible_text_cols:
            if col in row_data and isinstance(row_data[col], str):
                content = row_data[col]
                break
        
        if not content:
            # Fallback: join all values
            content = " ".join([str(v) for v in row_data.values()])
            
        doc = models.Document(
            source_id=source.id,
            doc_type="review",
            metadata_=row_data
        )
        db.add(doc)
        await db.flush()
        
        await _create_chunks(doc, content, db)
