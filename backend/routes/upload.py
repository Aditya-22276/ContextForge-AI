from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    UploadFile,
    File,
    Form
)

from sqlalchemy.orm import Session

from db.database import get_db
from models.document import Document

from services.embeddings import (
    generate_embedding,
    embedding_to_json
)

from services.dependencies import (
    get_current_user
)

import fitz

router = APIRouter()


# -----------------------------------
# TEXT CHUNKER
# -----------------------------------
def chunk_text(
    text,
    chunk_size=500
):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start = end

    return chunks


# -----------------------------------
# TEXT UPLOAD
# -----------------------------------
@router.post("/upload")
async def upload_text(

    content: str = Form(...),

    db: Session = Depends(get_db),

    user_id: int = Depends(
        get_current_user
    )
):

    # EMPTY CHECK
    if not content.strip():

        raise HTTPException(
            status_code=400,
            detail="Content cannot be empty"
        )

    # SPLIT INTO CHUNKS
    chunks = chunk_text(content)

    stored_docs = []

    # STORE CHUNKS
    for chunk in chunks:

        if not chunk.strip():
            continue

        embedding = generate_embedding(
            chunk
        )

        embedding_json = embedding_to_json(
            embedding
        )

        document = Document(
            content=chunk,

            embedding=embedding_json,

            # ✅ NEW
            filename="Pasted Text",

            user_id=user_id
        )

        db.add(document)

        stored_docs.append(document)

    db.commit()

    return {
        "message":
        f"Stored {len(stored_docs)} chunks successfully"
    }


# -----------------------------------
# PDF / TXT FILE UPLOAD
# -----------------------------------
@router.post("/upload-file")
async def upload_file(

    file: UploadFile = File(...),

    db: Session = Depends(get_db),

    user_id: int = Depends(
        get_current_user
    )
):

    extracted_text = ""

    # TXT FILE
    if file.filename.endswith(".txt"):

        extracted_text = (
            await file.read()
        ).decode("utf-8")

    # PDF FILE
    elif file.filename.endswith(".pdf"):

        pdf_bytes = await file.read()

        pdf = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        for page in pdf:

            extracted_text += (
                page.get_text()
            )

    else:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only TXT and PDF "
                "files supported"
            )
        )

    # EMPTY CHECK
    if not extracted_text.strip():

        raise HTTPException(
            status_code=400,
            detail="No text found in file"
        )

    # SPLIT INTO CHUNKS
    chunks = chunk_text(extracted_text)

    stored_docs = []

    # STORE CHUNKS
    for chunk in chunks:

        if not chunk.strip():
            continue

        embedding = generate_embedding(
            chunk
        )

        embedding_json = embedding_to_json(
            embedding
        )

        document = Document(

            content=chunk,

            embedding=embedding_json,

            # ✅ STORE FILENAME
            filename=file.filename,

            user_id=user_id
        )

        db.add(document)

        stored_docs.append(document)

    db.commit()

    return {
        "message":
        f"Stored {len(stored_docs)} chunks successfully",

        "filename": file.filename,

        "chunks": len(stored_docs)
    }