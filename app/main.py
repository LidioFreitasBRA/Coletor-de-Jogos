from fastapi import FastAPI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Football Stats API",
    description="API de estatísticas de futebol",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Football Stats API está funcionando!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/teams")
async def get_teams():
    return {"teams": ["Flamengo", "Palmeiras", "São Paulo"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
