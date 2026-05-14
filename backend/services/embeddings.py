import os
import json
import numpy as np
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


def generate_embedding(text: str) -> list:
    """
    Takes text as input.
    Returns embedding as a list of floats.
    """
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return response.embeddings[0].values


def embedding_to_json(embedding: list) -> str:
    """Convert embedding list to JSON string for storage."""
    return json.dumps(embedding)


def json_to_embedding(json_str: str) -> np.ndarray:
    """Convert JSON string back to numpy array."""
    return np.array(json.loads(json_str))


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    Returns a score between 0 and 1.
    1 = identical, 0 = completely different.
    """
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(dot_product / (norm1 * norm2))