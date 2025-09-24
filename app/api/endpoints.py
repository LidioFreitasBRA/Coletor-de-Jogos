# app/api/endpoints.py
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict
import logging

from app.services.data_service import DataService, get_data_service
from app.models.schemas import (
    TeamResponse, MatchResponse, ScoreProbabilityResponse,
    PlayerStatsResponse, BettingAnalysisResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health", response_model=Dict)
async def health_check():
    return {"status": "healthy", "service": "football-stats-api"}

@router.get("/teams", response_model=List[TeamResponse])
async def get_teams(
    country: Optional[str] = Query(None, description="Filtrar por país"),
    data_service: DataService = Depends(get_data_service)
):
    """Retorna lista de times"""
    try:
        teams = await data_service.get_teams(country)
        return teams
    except Exception as e:
        logger.error(f"Erro ao buscar times: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/matches", response_model=List[MatchResponse])
async def get_matches(
    league: str = Query(..., description="Código da liga (ex: '24' para Brasileirão)"),
    season: str = Query(..., description="Temporada (ex: '2024')"),
    team: Optional[str] = Query(None, description="Filtrar por time"),
    data_service: DataService = Depends(get_data_service)
):
    """Retorna partidas de uma liga/temporada"""
    try:
        matches = await data_service.get_matches(league, season, team)
        return matches
    except Exception as e:
        logger.error(f"Erro ao buscar partidas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/analysis/score-probabilities", response_model=ScoreProbabilityResponse)
async def get_score_probabilities(
    home_team: str = Query(..., description="Time mandante"),
    away_team: str = Query(..., description="Time visitante"),
    data_service: DataService = Depends(get_data_service)
):
    """Calcula probabilidades de placar correto"""
    try:
        probabilities = await data_service.calculate_score_probabilities(home_team, away_team)
        return probabilities
    except Exception as e:
        logger.error(f"Erro ao calcular probabilidades: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/analysis/player-stats", response_model=List[PlayerStatsResponse])
async def get_player_stats(
    team: Optional[str] = Query(None, description="Filtrar por time"),
    position: Optional[str] = Query(None, description="Filtrar por posição"),
    data_service: DataService = Depends(get_data_service)
):
    """Retorna estatísticas de jogadores"""
    try:
        stats = await data_service.get_player_stats(team, position)
        return stats
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas de jogadores: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get("/analysis/betting-insights", response_model=BettingAnalysisResponse)
async def get_betting_insights(
    home_team: str = Query(..., description="Time mandante"),
    away_team: str = Query(..., description="Time visitante"),
    data_service: DataService = Depends(get_data_service)
):
    """Retorna insights para apostas"""
    try:
        insights = await data_service.get_betting_insights(home_team, away_team)
        return insights
    except Exception as e:
        logger.error(f"Erro ao gerar insights: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.post("/collect/update-data")
async def update_data(
    league: str = Query(..., description="Liga para atualizar"),
    season: str = Query(..., description="Temporada para atualizar"),
    data_service: DataService = Depends(get_data_service)
):
    """Força atualização dos dados"""
    try:
        result = await data_service.update_league_data(league, season)
        return {"status": "success", "message": f"Dados atualizados: {result}"}
    except Exception as e:
        logger.error(f"Erro ao atualizar dados: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
