from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.complete_api import app as api_app

app = FastAPI(title="SLH Airdrop API", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# כלול את כל ה-endpoints מה-complete_api
app.include_router(api_app.router)

@app.get("/")
async def root():
    return {
        "message": "🚀 SLH Airdrop System",
        "status": "operational",
        "version": "1.0",
        "docs": "/docs",
        "health": "/health",
        "admin": "/admin/dashboard?admin_key=airdrop_admin_2026"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "airdrop-api"}
