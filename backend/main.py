from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag import query_fifa
import pickle
import json
import numpy as np
import os

app = FastAPI(title="FIFA AI Analyst API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Load Model & Stats on Startup ──
MODEL_PATH = "../data/model/match_predictor.pkl"
STATS_PATH = "../data/model/team_stats.pkl"
TEAMS_PATH = "../data/model/teams_list.json"

try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(STATS_PATH, 'rb') as f:
        team_stats = pickle.load(f)
    with open(TEAMS_PATH, 'r') as f:
        teams_list = json.load(f)
    print(f"✅ Prediction model loaded — {len(teams_list)} teams available")
except Exception as e:
    print(f"⚠️ Could not load model: {e}")
    model = None
    team_stats = {}
    teams_list = []


# ── Helper Functions ──
def get_team_features(team):
    if team in team_stats:
        s = team_stats[team]
        return [
            s['win_rate'],
            s['draw_rate'],
            s['loss_rate'],
            s['avg_goals_scored'],
            s['avg_goals_conceded'],
            s['played']
        ]
    return [0.33, 0.33, 0.33, 1.0, 1.0, 0]

def get_h2h_neutral():
    return [0.33, 0.33, 0.33]


# ── Request / Response Models ──
class QuestionRequest(BaseModel):
    question: str
    n_results: int = 5

class AnswerResponse(BaseModel):
    answer: str
    sources: list

class PredictRequest(BaseModel):
    home_team: str
    away_team: str

class PredictResponse(BaseModel):
    home_team: str
    away_team: str
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    prediction: str
    confidence: str
    home_stats: dict
    away_stats: dict


# ── Routes ──
@app.get("/health")
def health():
    return {"status": "ok", "message": "FIFA AI Analyst is running"}

@app.get("/teams")
def get_teams():
    return {"teams": teams_list, "total": len(teams_list)}

@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    result = query_fifa(request.question, request.n_results)
    return AnswerResponse(answer=result["answer"], sources=result["sources"])

@app.post("/predict", response_model=PredictResponse)
def predict_match(request: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Prediction model not loaded")

    home = request.home_team
    away = request.away_team

    if home == away:
        raise HTTPException(status_code=400, detail="Teams must be different")

    # Build features
    home_features = get_team_features(home)
    away_features = get_team_features(away)
    h2h = get_h2h_neutral()
    features = np.array([home_features + away_features + h2h])

    # Get probabilities
    probs = model.predict_proba(features)[0]

    # Map to labels (0=home win, 1=draw, 2=away win)
    classes = model.classes_
    prob_map = {c: round(float(p) * 100, 1) for c, p in zip(classes, probs)}

    home_win_prob = prob_map.get(0, 0.0)
    draw_prob     = prob_map.get(1, 0.0)
    away_win_prob = prob_map.get(2, 0.0)

    # Determine prediction
    max_prob = max(home_win_prob, draw_prob, away_win_prob)
    if max_prob == home_win_prob:
        prediction = f"{home} wins"
    elif max_prob == draw_prob:
        prediction = "Draw"
    else:
        prediction = f"{away} wins"

    # Confidence label
    if max_prob >= 60:
        confidence = "High"
    elif max_prob >= 45:
        confidence = "Medium"
    else:
        confidence = "Low"

    # Team stats for display
    def format_stats(team):
        if team in team_stats:
            s = team_stats[team]
            return {
                "played": s['played'],
                "win_rate": f"{round(s['win_rate'] * 100, 1)}%",
                "avg_goals_scored": round(s['avg_goals_scored'], 2),
                "avg_goals_conceded": round(s['avg_goals_conceded'], 2),
            }
        return {"played": 0, "win_rate": "N/A", "avg_goals_scored": 0, "avg_goals_conceded": 0}

    return PredictResponse(
        home_team=home,
        away_team=away,
        home_win_probability=home_win_prob,
        draw_probability=draw_prob,
        away_win_probability=away_win_prob,
        prediction=prediction,
        confidence=confidence,
        home_stats=format_stats(home),
        away_stats=format_stats(away)
    )