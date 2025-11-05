from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import chatkit
from .routers import documents
from .services.config import config
from .services.log_service import setup_logging  # noqa


if not config.validate():
    raise RuntimeError("Invalid configuration. Please check your .env file and ensure all required variables are set.")


logger = logging.getLogger(__name__)
logger.info("Logging system initialized successfully")

logger.info("Starting Exam Assistant API")
app = FastAPI(title="Exam Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Configuring API routes")
app.include_router(chatkit.router, prefix="/exam-assistant", tags=["ChatKit"])
app.include_router(documents.router, prefix="/exam-assistant", tags=["Documents"])
logger.info("API initialization complete")
