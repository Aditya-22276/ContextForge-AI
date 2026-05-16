from services.embeddings import (
    generate_embedding,
    json_to_embedding,
    cosine_similarity
)

from services.gemini import generate_response

from models.document import Document

from sqlalchemy import or_

import numpy as np

# Retrive relevant documents
# Hybrid search

def retrieve_relevant_docs(
    query,
    db,
    user_id,
    top_k=5
):

    # Geneartes hybrid embeddings
    query_embedding = generate_embedding(query)

    # Get user documents
    docs = db.query(Document).filter(
        Document.user_id == user_id
    ).all()

    scored_docs = []

    # Query words
    query_words = query.lower().split()

    # Hybrid search
    for doc in docs:

        try:

            # vector search
            doc_embedding = json_to_embedding(
                doc.embedding
            )

            vector_score = cosine_similarity(
                query_embedding,
                doc_embedding
            )

          # Keyword score
            content_lower = doc.content.lower()

            keyword_matches = sum(
                1
                for word in query_words
                if word in content_lower
            )

            keyword_score = (
                keyword_matches /
                max(len(query_words), 1)
            )

           # Final hybrid score
            final_score = (
                (0.7 * vector_score) +
                (0.3 * keyword_score)
            )

            scored_docs.append(
                (doc, final_score)
            )

        except Exception as e:

            print(
                f"Hybrid Search Error for doc {doc.id}:",
                e
            )

    # Sorts descending
    scored_docs.sort(
        key=lambda x: x[1],
        reverse=True
    )

  # Gives TOP results
    top_results = []

    for doc, score in scored_docs[:top_k]:

        if score > 0.15:

            top_results.append(
                (doc, score)
            )

    return top_results


# Build context
def build_context(top_docs):

    context = ""

    sources = []

    scores = []

    seen_content = set()

    seen_files = set()

    for i, (doc, score) in enumerate(top_docs):

        content = doc.content.strip()

        # Avoid duplicate chunks
        if content in seen_content:
            continue

        seen_content.add(content)

        # Preview window
        preview = content[:1200]

        context += f"""
DOCUMENT {i + 1}:
{preview}

"""

        # Aviod duplicate file names
        if doc.filename not in seen_files:

            sources.append({
                "id": doc.id,
                "filename": doc.filename
            })

            seen_files.add(doc.filename)

        scores.append(score)

    confidence = round(
        sum(scores) / len(scores),
        2
    ) if scores else 0

    return context.strip(), sources, confidence


# Generate chat response
def generate_chat_response(
    query: str,
    context: str,
    history=None
):

    history_text = ""

    if history:

        for msg in history[-6:]:

            role = msg.get("role", "user")

            content = msg.get("content", "")

            history_text += (
                f"{role.upper()}: {content}\n"
            )

    prompt = f"""
You are ContextForge AI.

You are an intelligent conversational AI assistant.

Your job:
- Use previous conversation memory
- Understand follow-up questions
- Analyze uploaded documents
- Combine information intelligently
- Keep responses natural and conversational

PREVIOUS CONVERSATION:
{history_text}

DOCUMENT CONTEXT:
{context}

CURRENT USER QUESTION:
{query}

RULES:
- Answer naturally
- Understand references like:
  "it", "they", "that", "those"
- Do not hallucinate
- If answer not found say:
  "I could not find that information in the uploaded documents."
"""

    return generate_response(prompt)