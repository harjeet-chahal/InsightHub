from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from collections import defaultdict
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

from apps.api.db import models

async def calculate_scorecard(scorecard_id: str, db: AsyncSession):
    # 1. Fetch Scorecard
    scorecard = await db.get(models.Scorecard, scorecard_id)
    if not scorecard:
        return

    # 2. Parse Config
    config = scorecard.config
    factors = config.get("factors", [])
    if not factors:
        return

    # 3. Fetch Documents for Workspace
    stmt = (
        select(models.Document)
        .join(models.Source)
        .where(models.Source.workspace_id == scorecard.workspace_id)
    )
    result = await db.execute(stmt)
    documents = result.scalars().all()
    
    # 4. Group by Brand
    docs_by_brand = defaultdict(list)
    for doc in documents:
        # Assuming brand is in metadata, normalization needed in real app
        brand = (doc.metadata_ or {}).get("brand", "Unknown")
        docs_by_brand[brand].append(doc)
        
    sia = SentimentIntensityAnalyzer()
    
    # 5. Evaluate Per Brand
    results_to_save = []
    
    # Clear old results
    await db.execute(
        delete(models.ScorecardResult)
        .where(models.ScorecardResult.scorecard_id == scorecard_id)
    )
    
    for brand, brand_docs in docs_by_brand.items():
        doc_ids = [d.id for d in brand_docs]
        
        # Fetch chunks for texts
        chunk_stmt = select(models.Chunk).where(models.Chunk.document_id.in_(doc_ids))
        chunk_result = await db.execute(chunk_stmt)
        chunks = chunk_result.scalars().all()
        
        full_text = " ".join([c.text for c in chunks]).lower()
        
        brand_scores = {}
        total_weighted_score = 0
        total_weight = 0
        
        for factor in factors:
            name = factor.get("name")
            keywords = [k.lower() for k in factor.get("keywords", [])]
            weight = factor.get("weight", 1.0)
            
            # Simple Scoring Rule: 
            # 1. Find sentences/chunks with keywords
            # 2. Calculate sentiment of those segments
            # 3. Normalize (-1 to 1) -> (0 to 100)
            
            # Since we have full_text, let's split by sentence (NLTK) or iterate chunks
            # Iterating chunks is safer for context
            
            relevant_texts = []
            for chunk in chunks:
                chunk_lower = chunk.text.lower()
                if any(k in chunk_lower for k in keywords):
                    relevant_texts.append(chunk.text)
            
            if not relevant_texts:
                # Neutral score or 0? Let's say 50 (neutral) if no mentions found
                score = 50.0
            else:
                combined_relevant = " ".join(relevant_texts)
                sentiment = sia.polarity_scores(combined_relevant)
                compound = sentiment['compound'] # -1 to 1
                
                # Normalize to 0-100
                # -1 -> 0, 0 -> 50, 1 -> 100
                score = (compound + 1) * 50
                
            brand_scores[name] = round(score, 1)
            total_weighted_score += score * weight
            total_weight += weight
            
        overall_score = 0
        if total_weight > 0:
            overall_score = total_weighted_score / total_weight
            
        result_entry = models.ScorecardResult(
            scorecard_id=scorecard.id,
            brand=brand,
            results={
                "overall": round(overall_score, 1),
                "factors": brand_scores
            }
        )
        results_to_save.append(result_entry)
        
    db.add_all(results_to_save)
    await db.commit()
