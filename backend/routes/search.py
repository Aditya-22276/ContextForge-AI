from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.database import get_db
from models.document import Document
from services.embeddings import generate_embedding, json_to_embedding, cosine_similarity
import numpy as np

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 3


class SearchResult(BaseModel):
    id: int
    content: str
    similarity_score: float


class SearchResponse(BaseModel):
    results: list[SearchResult]


@router.post("/search", response_model=SearchResponse)
def search_documents(request: SearchRequest, db: Session = Depends(get_db)):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Convert query to embedding
    query_embedding = generate_embedding(request.query)
    query_vector = np.array(query_embedding)

    # Get documents
    documents = db.query(Document).filter(Document.embedding != None).all()

    if not documents:
        raise HTTPException(status_code=404, detail="No documents found")

    # Compare similarity
    scored = []
    for doc in documents:
        doc_vector = json_to_embedding(doc.embedding)
        score = cosine_similarity(query_vector, doc_vector)
        scored.append((doc, score))

    # Sort results
    scored.sort(key=lambda x: x[1], reverse=True)

    # Return top results
    top_results = scored[:request.top_k]

    return SearchResponse(
        results=[
            SearchResult(
                id=doc.id,
                content=doc.content,
                similarity_score=round(score, 4)
            )
            for doc, score in top_results
        ]
    )