# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.api.endpoints import router as api_router
from app.services.data_service import DataService

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Iniciando Football Stats API")
    
    # Inicializa serviços
    app.state.data_service = DataService()
    await app.state.data_service.initialize()
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando Football Stats API")

app = FastAPI(
    title="Football Stats API",
    description="API completa de estatísticas de futebol brasileiro e mundial",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(api_router, prefix="/api/v1")

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>Football Stats API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚽ Football Stats API</h1>
                <p>API completa de estatísticas de futebol</p>
                
                <h2>📚 Endpoints Disponíveis</h2>
                
                <div class="endpoint">
                    <strong>GET /api/v1/health</strong> - Status da API
                </div>
                
                <div class="endpoint">
                    <strong>GET /api/v1/teams</strong> - Lista de times
                </div>
                
                <div class="endpoint">
                    <strong>GET /api/v1/matches</strong> - Partidas por liga/temporada
                </div>
                
                <div class="endpoint">
                    <strong>GET /api/v1/analysis/score-probabilities</strong> - Probabilidades de placar
                </div>
                
                <div class="endpoint">
                    <strong>GET /api/v1/analysis/player-stats</strong> - Estatísticas de jogadores
                </div>
                
                <p>📖 <a href="/docs">Documentação Interativa (Swagger)</a></p>
                <p>🐙 <a href="https://github.com/seu-usuario/football-stats-app">GitHub Repository</a></p>
            </div>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "football-stats-api",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )
