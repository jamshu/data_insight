from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from api.routers import upload, analysis, sessions, export

# Create FastAPI app
app = FastAPI(
    title="Data Insights Platform API",
    description="Universal data analytics platform for CSV and Excel files",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers with correct prefixes
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(export.router, prefix="/api/export", tags=["export"])

# Add startup event
@app.on_event("startup")
async def startup_event():
    print("🚀 Data Insights Platform starting...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Data Insights Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
