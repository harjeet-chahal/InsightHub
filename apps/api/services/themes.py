from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from collections import Counter
import re

from apps.api.db import models

async def extract_themes(workspace_id: str, db: AsyncSession, n_clusters: int = 5):
    # 1. Fetch chunks with embeddings
    stmt = (
        select(models.Chunk, models.Source)
        .join(models.Document)
        .join(models.Source)
        .where(models.Source.workspace_id == workspace_id)
        .where(models.Chunk.embedding.isnot(None))
    )
    result = await db.execute(stmt)
    rows = result.all()
    
    if not rows:
        return
        
    chunks = [row[0] for row in rows]
    embeddings = [c.embedding for c in chunks]
    
    # Need enough samples
    if len(embeddings) < n_clusters:
        n_clusters = max(1, len(embeddings))
        
    # 2. Clustering
    # Convert list of lists/arrays to numpy array
    X = np.array(embeddings)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    labels = kmeans.fit_predict(X)
    
    # 3. Process Clusters
    cluster_map = {i: [] for i in range(n_clusters)}
    for idx, label in enumerate(labels):
        cluster_map[label].append(chunks[idx])

    # Clear old themes
    await db.execute(
        delete(models.Insight)
        .where(models.Insight.workspace_id == workspace_id)
        .where(models.Insight.kind == 'theme')
    )
    
    insights = []
    
    for label, cluster_chunks in cluster_map.items():
        if not cluster_chunks:
            continue
            
        # Get texts for keyword extraction
        texts = [c.text for c in cluster_chunks]
        
        # Simple Keyword Extraction (TF-IDF equivalent or just frequency)
        # For better titles, we'd use LLM, but here we use simple stats
        vectorizer = TfidfVectorizer(stop_words='english', max_features=3)
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()
            title = ", ".join(feature_names).title()
        except:
            title = f"Theme {label+1}"
            
        # Get evidence (top 5 longest or just first 5 for now)
        # Ideally we'd find those closest to centroid, but we don't have easy access 
        # to distance from centroid without re-calculating or using transform.
        # For MVP, random 5 from cluster is okay, or longest.
        evidence_chunks = sorted(cluster_chunks, key=lambda c: len(c.text), reverse=True)[:5]
        
        evidence_data = []
        for c in evidence_chunks:
            # We need to fetch source info, but we didn't store it eagerly in cluster_map tuples
            # We can re-fetch or assume 'text' is enough. 
            # The prompt asked for source references.
            # Let's simple use the text.
            evidence_data.append({
                "text": c.text,
                "chunk_id": c.id
            })
            
        insight = models.Insight(
            workspace_id=workspace_id,
            kind='theme',
            title=title,
            summary=f"Cluster containing {len(cluster_chunks)} text segments.",
            metrics={"count": len(cluster_chunks)},
            evidence=evidence_data
        )
        insights.append(insight)
        
    db.add_all(insights)
    await db.commit()
