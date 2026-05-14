from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from db.database import get_db

from models.document import Document

from services.dependencies import get_current_user


# ✅ ROUTER
router = APIRouter()


# -----------------------------------
# GET USER DOCUMENTS
# -----------------------------------
@router.get("/documents")
def get_documents(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):

    docs = db.query(Document).filter(
        Document.user_id == user_id
    ).all()

    unique_files = {}

    for doc in docs:

        filename = doc.filename

        if filename not in unique_files:

            unique_files[filename] = {
                "filename": filename,
                "created_at": doc.created_at
            }

    return list(unique_files.values())


# -----------------------------------
# DELETE DOCUMENT
# -----------------------------------
@router.delete("/documents/{filename}")
def delete_document(
    filename: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):

    docs = db.query(Document).filter(
        Document.user_id == user_id,
        Document.filename == filename
    ).all()

    for doc in docs:
        db.delete(doc)

    db.commit()

    return {
        "message": f"{filename} deleted successfully"
    }