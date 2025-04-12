from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.core.logging import get_logger, setup_logging
from api.src.users.routes import router as auth_router
from api.src.songs.routes import router as song_router
from api.src.artists.routes import router as artist_router
from api.src.playlists.routes import router as playlist_router
from api.utils.migrations import run_migrations

# Set up logging configuration
setup_logging()

# Optional: Run migrations on startup
run_migrations()

# Set up logger for this module
logger = get_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(auth_router)
app.include_router(song_router)
app.include_router(artist_router)
app.include_router(playlist_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint."""
    logger.debug("Root endpoint called")
    return {"message": "Welcome to Neotune API!"}
