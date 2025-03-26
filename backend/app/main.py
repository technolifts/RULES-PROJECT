from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import auth, documents, shares, audit
from app.database import Base, engine
from app.config import settings
from app.utils.audit import AuditMiddleware
import os

app = FastAPI(title="DocSecure API")

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(shares.router)
app.include_router(audit.router)

# Add audit middleware
app.middleware("http")(AuditMiddleware())

# Create uploads directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Welcome to DocSecure API"}
