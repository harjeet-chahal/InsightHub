from sentence_transformers import SentenceTransformer
import redis
import json
from typing import List
from apps.api.core.config import settings

# Global model instance
# note: in production, this should likely be handled by a separate serving container (e.g. TorchServe) 
# or initialized carefully to avoid memory overhead in every worker if concurrency is high.
# For MVP, loading global is fine.
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

# Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST, 
    port=int(settings.REDIS_PORT), 
    db=0, 
    decode_responses=True
)

def get_embedding(text: str) -> List[float]:
    # Check cache
    cache_key = f"emb:{text}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Generate
    model = get_model()
    embedding = model.encode(text).tolist()

    # Cache (expire in 24h)
    redis_client.setex(cache_key, 86400, json.dumps(embedding))
    
    return embedding
