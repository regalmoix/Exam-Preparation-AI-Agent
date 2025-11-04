from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import chatkit
from .routers import documents
from .routers import vector_store
from .services.config import config


# Validate configuration on startup
if not config.validate():
    raise RuntimeError("Invalid configuration. Please check your .env file and ensure all required variables are set.")

app = FastAPI(title="Exam Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatkit.router, prefix="/exam-assistant", tags=["ChatKit"])
app.include_router(documents.router, prefix="/exam-assistant", tags=["Documents"])
app.include_router(vector_store.router, prefix="/exam-assistant", tags=["Vector Store"])
