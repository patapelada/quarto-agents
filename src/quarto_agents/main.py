import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from quarto_lib import ChooseInitialPieceResponse, CompleteTurnResponse, GameState

from quarto_agents.agent_loader import get_agent

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()
allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
agent = get_agent()


@app.get(
    "/",
    tags=["health"],
)
def health_check():
    return {
        "status": "ok",
        "agent": agent.identifier,
    }


@app.post(
    "/choose-initial-piece",
    response_model=ChooseInitialPieceResponse,
)
def choose_initial_piece():
    return agent.choose_initial_piece()


@app.post(
    "/complete-turn",
    response_model=CompleteTurnResponse,
)
def complete_turn(game: GameState):
    return agent.complete_turn(game)
