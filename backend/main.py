from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.summarize import router as summarize_router
from routes.upload import router as upload_router
from routes.search import router as search_router
from routes.search import router as search_router
from routes.chat import router as chat_router
from routes.auth import router as auth_router
from routes.documents import router as documents_router
from routes.chat_history_side import router as chat_history_router
from models.chat_history import ChatHistory
from db.database import Base, engine
from models.chat_session import ChatSession
from routes.session import router as sessions_router


Base.metadata.create_all(bind=engine)



app = FastAPI(
    title="ContextForge AI",
    description="Your Second Brain — AI-powered document intelligence",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(
    documents_router,
    prefix="/api",
    tags=["Documents"]
)
app.include_router(
    sessions_router,
    prefix="/api",
    tags=["Session"]
)

app.include_router(summarize_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(chat_history_router, prefix="/api")


@app.get("/")
def root():
    return {"status": "ContextForge AI is running"}