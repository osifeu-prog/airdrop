from fastapi import FastAPI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Airdrop API",
    description="Airdrop Distribution System",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Airdrop API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/docs")
async def get_docs():
    return {"docs": "available at /docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)