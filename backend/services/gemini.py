import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

# -----------------------------
# LOAD ENV
# -----------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:

    raise ValueError(
        "GEMINI_API_KEY not found in .env file"
    )

# -----------------------------
# GEMINI CLIENT
# -----------------------------

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# -----------------------------
# SAFE RESPONSE EXTRACTOR
# -----------------------------

def extract_response_text(response):

    try:

        if hasattr(response, "text") and response.text:

            return response.text.strip()

        return "No response generated."

    except Exception as e:

        print(
            "Response Parse Error:",
            e
        )

        return "Error parsing AI response."

# -----------------------------
# SUMMARIZER
# -----------------------------

def summarize_text(text: str) -> str:

    prompt = f"""
You are an expert AI summarizer.

Your task:
- Summarize the text clearly
- Use concise bullet points
- Keep summary under 150 words
- Preserve important information
- Avoid repetition

TEXT:
{text}

SUMMARY:
"""

    try:

        response = client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt,

            config=types.GenerateContentConfig(
                temperature=0.3,
                top_p=0.9,
                top_k=40,
                max_output_tokens=400,
            )
        )

        return extract_response_text(
            response
        )

    except Exception as e:

        print(
            "Gemini Summary Error:",
            e
        )

        return "Error generating summary."

# -----------------------------
# NORMAL CHAT RESPONSE
# -----------------------------

def generate_response(prompt: str) -> str:

    system_prompt = f"""
You are ContextForge AI.

Rules:
- Answer ONLY from provided context
- Be accurate and concise
- Do not hallucinate
- If answer is not found in context, say:
  "I couldn't find that information in the uploaded documents."

USER QUERY + CONTEXT:
{prompt}

ANSWER:
"""

    try:

        response = client.models.generate_content(

            model="gemini-2.5-flash",

            contents=system_prompt,

            config=types.GenerateContentConfig(
                temperature=0.4,
                top_p=0.95,
                top_k=50,
                max_output_tokens=700,
            )
        )

        return extract_response_text(
            response
        )

    except Exception as e:

        print(
            "Gemini Chat Error:",
            e
        )

        return "Error generating AI response."

# -----------------------------
# CHAT TITLE GENERATOR
# -----------------------------

def generate_chat_title(query: str) -> str:

    prompt = f"""
Generate a very short chat title
for this user query.

Rules:
- Maximum 5 words
- No quotes
- No special characters
- Keep it concise

QUERY:
{query}

TITLE:
"""

    try:

        response = client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt,

            config=types.GenerateContentConfig(
                temperature=0.4,
                top_p=0.95,
                top_k=50,
                max_output_tokens=30,
            )
        )

        title = extract_response_text(
            response
        )

        cleaned_title = title.strip()

        if (
            cleaned_title == "No response generated."
            or cleaned_title == ""
        ):

            return query[:40]

        return cleaned_title

    except Exception as e:

        print(
            "Title Generation Error:",
            e
        )

        return query[:40]