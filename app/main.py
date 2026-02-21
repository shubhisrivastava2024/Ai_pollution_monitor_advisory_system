import uvicorn
from fastapi import FastAPI, HTTPException
from .api import locations, pollution, ai
from .db import init_db
from .utils.errors import global_exception_handler, http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Pollution Monitor API",
    description="REST API for monitoring pollution levels and predicting weather trends using AI.",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# Include Routers
app.include_router(locations.router)
app.include_router(pollution.router)
app.include_router(ai.router)

# Mount Static Files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/api/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    # Ensure DB is initialized before starting
    init_db.init_db()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
