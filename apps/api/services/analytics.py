import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import defaultdict, Counter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime
import json

from apps.api.db import models

# Ensure NLTK data is downloaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

# Configurable claims
CLAIMS = [
    "whitening", "sensitivity", "enamel", "fresh breath", 
    "fluoride-free", "natural", "cavity protection", 
    "gum health", "plaque", "charcoal"
]

async def run_workspace_analytics(workspace_id: str, db: AsyncSession):
    # 1. Fetch all documents & sources
    # Join Source to filter by workspace
    stmt = (
        select(models.Document)
        .join(models.Source)
        .where(models.Source.workspace_id == workspace_id)
    )
    result = await db.execute(stmt)
    documents = result.scalars().all()

    if not documents:
        return

    # 2. Initialize Analyzers
    sia = SentimentIntensityAnalyzer()
    
    # Aggregators
    total_docs = 0
    sentiment_counts = Counter() # pos, neu, neg
    sentiment_scores = []
    claim_counts = Counter()
    rating_trends = defaultdict(lambda: defaultdict(list)) # brand -> date -> [ratings]

    # Brand-level Aggregators
    brand_stats = defaultdict(lambda: {"total_docs": 0, "sentiment_scores": [], "claim_counts": Counter(), "ratings": []})
    
    # 3. Process Documents
    for doc in documents:
        total_docs += 1
        
        # Metadata extraction
        meta = doc.metadata_ or {}
        brand = meta.get('brand', 'Unknown')
        date_str = meta.get('date') # assume YYYY-MM-DD
        rating = meta.get('rating')

        # Brand basic stats
        brand_stats[brand]["total_docs"] += 1

        # Chunk retrieval
        chunk_stmt = select(models.Chunk).where(models.Chunk.document_id == doc.id)
        chunk_result = await db.execute(chunk_stmt)
        chunks = chunk_result.scalars().all()
        
        full_text = " ".join([c.text for c in chunks])
        if not full_text:
            continue

        # Sentiment
        scores = sia.polarity_scores(full_text)
        compound = scores['compound']
        sentiment_scores.append(compound)
        brand_stats[brand]["sentiment_scores"].append(compound)
        
        if compound >= 0.05:
            sentiment_counts['positive'] += 1
        elif compound <= -0.05:
            sentiment_counts['negative'] += 1
        else:
            sentiment_counts['neutral'] += 1
            
        # Claims
        text_lower = full_text.lower()
        for claim in CLAIMS:
            if claim in text_lower:
                claim_counts[claim] += 1
                brand_stats[brand]["claim_counts"][claim] += 1
                
        # Ratings / Trends
        if date_str and rating:
            try:
                r = float(rating)
                month = date_str[:7] # YYYY-MM
                rating_trends[brand][month].append(r)
                brand_stats[brand]["ratings"].append(r)
            except:
                pass


    # 4. Prepare Insights Data
    
    # Insight: Stats & Sentiment
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    
    # Calculate brand specific summaries for dashboard table
    brands_summary = {}
    for brand, data in brand_stats.items():
        b_avg_sent = sum(data["sentiment_scores"]) / len(data["sentiment_scores"]) if data["sentiment_scores"] else 0
        b_avg_rating = sum(data["ratings"]) / len(data["ratings"]) if data["ratings"] else 0
        b_top_claim = data["claim_counts"].most_common(1)[0][0] if data["claim_counts"] else "None"
        
        brands_summary[brand] = {
            "total_docs": data["total_docs"],
            "avg_sentiment": round(b_avg_sent, 3),
            "avg_rating": round(b_avg_rating, 2),
            "top_claim": b_top_claim,
            "claims_breakdown": dict(data["claim_counts"])
        }

    stats_metrics = {
        "total_documents": total_docs,
        "sentiment_distribution": dict(sentiment_counts),
        "average_sentiment": round(avg_sentiment, 3),
        "brands_summary": brands_summary
    }
    
    # Insight: Claims
    claims_metrics = dict(claim_counts)
    
    # Insight: Trends (avg rating per month per brand)
    trends_metrics = {}
    for brand, months in rating_trends.items():
        trends_metrics[brand] = {}
        for month, ratings in months.items():
            trends_metrics[brand][month] = round(sum(ratings) / len(ratings), 2)


    # 5. Store Insights (Upsert strategy: delete old for this kind/workspace and create new)
    # Clear existing insights to avoid duplicates for this run
    await db.execute(
        delete(models.Insight)
        .where(models.Insight.workspace_id == workspace_id)
        .where(models.Insight.kind.in_(['stats', 'claims', 'trends']))
    )
    
    insights = [
        models.Insight(
            workspace_id=workspace_id,
            kind='stats',
            title='General Statistics',
            summary=f"Processed {total_docs} documents. Sentiment mostly {max(sentiment_counts, key=sentiment_counts.get) if sentiment_counts else 'unknown'}.",
            metrics=stats_metrics
        ),
        models.Insight(
            workspace_id=workspace_id,
            kind='claims',
            title='Claims Frequency',
            summary=f"Found mentions of {len(claim_counts)} distinct claims.",
            metrics=claims_metrics
        ),
        models.Insight(
            workspace_id=workspace_id,
            kind='trends',
            title='Ratings Trends',
            summary="Average ratings over time by brand.",
            metrics=trends_metrics
        )
    ]
    
from apps.api.services import themes

    # ... (existing analytics code) ...
    
    db.add_all(insights)
    
    # Run Theme Extraction
    await themes.extract_themes(workspace_id, db)
    
    await db.commit()
