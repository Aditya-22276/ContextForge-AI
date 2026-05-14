from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.gemini import summarize_text

# Create router
router = APIRouter()


# Request body schema
class SummarizeRequest(BaseModel):
    text: str


# Response schema
class SummarizeResponse(BaseModel):
    summary: str


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    """
    Accepts raw text.
    Returns an AI-generated summary.
    """

    # Validate input is not empty
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # Call Gemini service
    summary = summarize_text(request.text)

    return SummarizeResponse(summary=summary)