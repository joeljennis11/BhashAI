"""
BhashAI: AI-Assisted Vernacular Education & Classroom Communication
Main FastAPI Application Entrypoint
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from backend.routes.speech import router as speech_router
from backend.routes.translation import router as translation_router
from backend.routes.tts import router as tts_router
from backend.routes.documents import router as documents_router
from backend.routes.worksheets import router as worksheets_router
from backend.routes.flashcards import router as flashcards_router
from backend.routes.health import router as health_router

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("bhashai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for clean startup and resource cleanup."""
    logger.info("Initializing BhashAI Vernacular Education Backend...")
    # Ensure required directories exist
    os.makedirs("models/asr", exist_ok=True)
    os.makedirs("models/translation", exist_ok=True)
    os.makedirs("models/santali_tts", exist_ok=True)
    os.makedirs("generated/worksheets", exist_ok=True)
    os.makedirs("generated/audio", exist_ok=True)
    os.makedirs("sample_materials", exist_ok=True)
    yield
    logger.info("Shutting down BhashAI Backend...")


app = FastAPI(
    title="BhashAI",
    description="AI-Assisted Vernacular Education and Classroom Communication for Indian Tribal Languages",
    version="1.0.0-prototype",
    lifespan=lifespan
)

# Enable CORS for native Android apps and web companions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Teacher-Friendly Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "An unexpected error occurred in the classroom application. Please try again or check your offline resources.",
            "detail": str(exc)
        }
    )

# Include API Routers
app.include_router(speech_router)
app.include_router(translation_router)
app.include_router(tts_router)
app.include_router(documents_router)
app.include_router(worksheets_router)
app.include_router(flashcards_router)
app.include_router(health_router)

# Mount Static Files (Web Companion & Fonts)
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
