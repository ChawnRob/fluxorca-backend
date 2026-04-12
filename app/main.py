from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

app = FastAPI()

feedbacks = []
memory_store: Dict[str, List[dict]] = {}

class FeedbackInput(BaseModel):
    slug: str
    sentiment: str
    message: Optional[str] = None

class MemoryInput(BaseModel):
    user_id: str
    content: str
    memory_type: str = "short_term"
    emotion: Optional[str] = None
    importance: int = 1

@app.get("/")
def root():
    return {"message": "Fluxorca API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/qr/{slug}")
def get_qr(slug: str):
    return {
        "slug": slug,
        "status": "ok",
        "links": {
            "google": "https://g.page/r/test/review",
            "apple": "https://maps.apple.com/?q=test",
            "trustpilot": "https://trustpilot.com/review/test"
        },
        "message": f"QR config loaded for {slug}"
    }

@app.post("/feedback")
def create_feedback(payload: FeedbackInput):
    item = {
        "slug": payload.slug,
        "sentiment": payload.sentiment,
        "message": payload.message,
        "created_at": datetime.utcnow().isoformat()
    }
    feedbacks.append(item)
    return {"status": "received", "data": item}

@app.get("/feedback/{slug}")
def list_feedback(slug: str):
    results = [f for f in feedbacks if f["slug"] == slug]
    return {
        "slug": slug,
        "count": len(results),
        "items": results
    }

@app.post("/memory")
def create_memory(payload: MemoryInput):
    item = {
        "content": payload.content,
        "memory_type": payload.memory_type,
        "emotion": payload.emotion,
        "importance": payload.importance,
        "created_at": datetime.utcnow().isoformat()
    }

    if payload.user_id not in memory_store:
        memory_store[payload.user_id] = []

    memory_store[payload.user_id].append(item)

    return {
        "status": "stored",
        "user_id": payload.user_id,
        "memory": item
    }

@app.get("/memory/{user_id}")
def get_memory(user_id: str):
    items = memory_store.get(user_id, [])
    return {
        "user_id": user_id,
        "count": len(items),
        "items": items
    }

@app.get("/memory/{user_id}/latest")
def get_latest_memory(user_id: str):
    items = memory_store.get(user_id, [])
    if not items:
        return {
            "user_id": user_id,
            "status": "empty",
            "memory": None
        }

    return {
        "user_id": user_id,
        "status": "ok",
        "memory": items[-1]
    }

@app.get("/memory/{user_id}/long-term")
def get_long_term_memory(user_id: str):
    items = memory_store.get(user_id, [])
    results = [m for m in items if m["memory_type"] == "long_term"]
    return {
        "user_id": user_id,
        "count": len(results),
        "items": results
    }
