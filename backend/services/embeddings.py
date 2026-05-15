import os
import json
import numpy as np

from dotenv import load_dotenv
from google import genai

# -------------------------
# LOAD ENV VARIABLES
# -------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:

    raise ValueError(
        "GEMINI_API_KEY not found in .env file"
    )

# -------------------------
# GEMINI CLIENT
# -------------------------

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# -------------------------
# GENERATE EMBEDDING
# -------------------------

def generate_embedding(text: str) -> list:

    try:

        response = client.models.embed_content(

            model="gemini-embedding-001",

            contents=text
        )

        return response.embeddings[0].values

    except Exception as e:

        print(
            "Embedding Error:",
            e
        )

        return []

# -------------------------
# JSON CONVERSION
# -------------------------

def embedding_to_json(
    embedding: list
) -> str:

    return json.dumps(
        embedding
    )


def json_to_embedding(
    json_str: str
) -> np.ndarray:

    return np.array(
        json.loads(json_str)
    )

# -------------------------
# COSINE SIMILARITY
# -------------------------

def cosine_similarity(
    vec1: np.ndarray,
    vec2: np.ndarray
) -> float:

    dot_product = np.dot(
        vec1,
        vec2
    )

    norm1 = np.linalg.norm(vec1)

    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:

        return 0.0

    return float(
        dot_product / (norm1 * norm2)
    )