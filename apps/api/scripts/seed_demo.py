import asyncio
import os
import sys
import csv

# Add parent directory to path to import apps modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from apps.api.db.session import async_session
from apps.api.db import models
from apps.api.services.ingestion import ingest_csv, ingest_url

async def seed():
    print("Seeding Demo Workspace...")
    async with async_session() as db:
        # 1. Create Workspace
        ws = models.Workspace(name="Toothpaste Market Research (Demo)")
        db.add(ws)
        await db.commit()
        await db.refresh(ws)
        print(f"Created Workspace: {ws.name} ({ws.id})")

        # 2. Ingest Sample CSV
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sample_reviews.csv')
        if os.path.exists(csv_path):
            with open(csv_path, 'rb') as f:
                content = f.read()
                # Create a file-like object for upload simulation
                # Our service expects bytes or file path? 
                # ingest_csv in services/ingestion.py takes (workspace_id, file, db) where file is UploadFile like or similar
                # actually ingest_csv implementation: `process_csv(source_id, file_path, db)` or similar?
                # Let's check ingestion service signature if needed. 
                # Wait, simpler: Create Source record manually and then run processing or use the simpler logic.
                # Actually, `ingestion.py` has `create_source` logic separate from processing usually?
                # Let's just manually create the Source and Documents to simulate ingestion or call the service functions if possible.
                # `ingest_csv` from service might expect FastAPI UploadFile. 
                # Let's implement robust seeding by manually reading CSV and creating Source + Documents.
                
                # Create Source
                source = models.Source(
                    workspace_id=ws.id,
                    type="csv",
                    title="sample_reviews.csv",
                    status="completed"
                )
                db.add(source)
                await db.commit()
                await db.refresh(source)
                
                # Parse CSV and Create Documents
                import io
                import pandas as pd
                
                df = pd.read_csv(io.BytesIO(content))
                documents = []
                for _, row in df.iterrows():
                    text = f"Review for {row['brand']}: {row['review_text']}"
                    doc = models.Document(
                        source_id=source.id,
                        text_content=text,
                        metadata_={
                            "brand": row['brand'],
                            "date": row['date'],
                            "rating": row['rating']
                        }
                    )
                    db.add(doc)
                    documents.append(doc)
                
                await db.commit()
                print(f"Ingested CSV: {len(documents)} reviews added.")
                
                # We need to create chunks + embeddings for these to work in search/analytics
                # We can call `_create_chunks` from ingestion service if we import it, or just rely on the celery worker?
                # Since this is a seed script, let's trigger the celery task or run chunking synchronously if imported.
                from apps.api.services.ingestion import _create_chunks
                for doc in documents:
                     await _create_chunks(doc, db)
                print("Generated embeddings for CSV documents.")

        # 3. Add Context URLs
        urls = [
            "https://en.wikipedia.org/wiki/Toothpaste",
            "https://en.wikipedia.org/wiki/Oral_hygiene"
        ]
        
        for url in urls:
            # Create Source
            source = models.Source(workspace_id=ws.id, type="url", title=url, url=url, status="pending")
            db.add(source)
            await db.commit()
            print(f"Added Source: {url}")
            # In a real scenario, the worker picks this up. 
            # We can trigger it if we want immediate results or let the user click "Ingest" in UI.
            # Let's leave it as pending to show UI functionality or trigger it.
            # Triggering via celery:
            from apps.api.worker import process_workspace_sources
            # process_workspace_sources.delay(ws.id) # If redis is running
            # OR sync process:
            # await ingest_url(...)
            # Let's just leave them for the user to "Process All" in UI to see the progress bar?
            # User requested "populate a demo workspace", implying ready to view.
            # Let's try to process one synchronously using service.
            try:
                from apps.api.services import ingestion
                await ingestion.process_source(source.id, db)
                print(f"Processed URL: {url}")
            except Exception as e:
                print(f"Skipping URL processing (network/deps): {e}")

    print("Seeding Complete!")

if __name__ == "__main__":
    asyncio.run(seed())
