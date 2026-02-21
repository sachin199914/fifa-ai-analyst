import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

# ── Load Data ──
print("Loading data...")
matches = pd.read_csv('data/matches_clean.csv')
results = pd.read_csv('data/results.csv')

# ── Build Team Stats from full historical results ──
# This gives us a much richer dataset than just World Cup matches
print("Building team stats...")

def build_team_stats(df, before_date=None):
    """Build win rate, goals scored/conceded per team"""
    if before_date:
        df = df[df['date'] < before_date]
    
    stats = {}
    
    for _, row in df.iterrows():
        home = row['home_team']
        away = row['away_team']
        hg = row['home_score']
        ag = row['away_score']
        
        for team in [home, away]:
            if team not in stats:
                stats[team] = {
                    'played': 0, 'wins': 0, 'draws': 0,
                    'losses': 0, 'goals_scored': 0, 'goals_conceded': 0
                }
        
        # Home team
        stats[home]['played'] += 1
        stats[home]['goals_scored'] += hg
        stats[home]['goals_conceded'] += ag
        if hg > ag:
            stats[home]['wins'] += 1
        elif hg == ag:
            stats[home]['draws'] += 1
        else:
            stats[home]['losses'] += 1
        
        # Away team
        stats[away]['played'] += 1
        stats[away]['goals_scored'] += ag
        stats[away]['goals_conceded'] += hg
        if ag > hg:
            stats[away]['wins'] += 1
        elif ag == hg:
            stats[away]['draws'] += 1
        else:
            stats[away]['losses'] += 1
    
    # Convert to rates
    for team in stats:
        p = stats[team]['played']
        if p > 0:
            stats[team]['win_rate'] = stats[team]['wins'] / p
            stats[team]['draw_rate'] = stats[team]['draws'] / p
            stats[team]['loss_rate'] = stats[team]['losses'] / p
            stats[team]['avg_goals_scored'] = stats[team]['goals_scored'] / p
            stats[team]['avg_goals_conceded'] = stats[team]['goals_conceded'] / p
        else:
            stats[team]['win_rate'] = 0
            stats[team]['draw_rate'] = 0
            stats[team]['loss_rate'] = 0
            stats[team]['avg_goals_scored'] = 0
            stats[team]['avg_goals_conceded'] = 0
    
    return stats

# ── Prepare Training Data from World Cup Matches ──
print("Preparing features...")

# Build overall team stats first
all_stats = build_team_stats(results)

def get_team_features(team, stats):
    """Get feature vector for a team"""
    if team in stats:
        s = stats[team]
        return [
            s['win_rate'],
            s['draw_rate'],
            s['loss_rate'],
            s['avg_goals_scored'],
            s['avg_goals_conceded'],
            s['played']
        ]
    else:
        # Unknown team — use neutral values
        return [0.33, 0.33, 0.33, 1.0, 1.0, 0]

def get_head_to_head(team1, team2, df):
    """Get head to head record between two teams"""
    h2h = df[
        ((df['home_team'] == team1) & (df['away_team'] == team2)) |
        ((df['home_team'] == team2) & (df['away_team'] == team1))
    ]
    
    if len(h2h) == 0:
        return [0, 0, 0]  # No history
    
    team1_wins = 0
    draws = 0
    team2_wins = 0
    
    for _, row in h2h.iterrows():
        if row['home_team'] == team1:
            if row['home_score'] > row['away_score']:
                team1_wins += 1
            elif row['home_score'] == row['away_score']:
                draws += 1
            else:
                team2_wins += 1
        else:
            if row['away_score'] > row['home_score']:
                team1_wins += 1
            elif row['away_score'] == row['home_score']:
                draws += 1
            else:
                team2_wins += 1
    
    total = len(h2h)
    return [team1_wins/total, draws/total, team2_wins/total]

# ── Build Feature Matrix from World Cup Matches ──
X = []
y = []

for _, row in matches.iterrows():
    home = row['Home Team Name']
    away = row['Away Team Name']
    
    home_features = get_team_features(home, all_stats)
    away_features = get_team_features(away, all_stats)
    h2h = get_head_to_head(home, away, results)
    
    features = home_features + away_features + h2h
    X.append(features)
    
    # Label: 0=home win, 1=draw, 2=away win
    if row['Home Team Goals'] > row['Away Team Goals']:
        y.append(0)
    elif row['Home Team Goals'] == row['Away Team Goals']:
        y.append(1)
    else:
        y.append(2)

X = np.array(X)
y = np.array(y)

print(f"Training samples: {len(X)}")
print(f"Label distribution: Home wins={sum(y==0)}, Draws={sum(y==1)}, Away wins={sum(y==2)}")

# ── Train Model ──
print("\nTraining model...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    min_samples_split=5,
    random_state=42
)
model.fit(X_train, y_train)

# ── Evaluate ──
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy:.2%}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Home Win', 'Draw', 'Away Win']))

# ── Save Model + Stats ──
os.makedirs('data/model', exist_ok=True)

with open('data/model/match_predictor.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('data/model/team_stats.pkl', 'wb') as f:
    pickle.dump(all_stats, f)

# Save team list for frontend dropdown
import json
teams = sorted(all_stats.keys())
with open('data/model/teams_list.json', 'w') as f:
    json.dump(teams, f)

print(f"\n✅ Model saved to data/model/match_predictor.pkl")
print(f"✅ Team stats saved to data/model/team_stats.pkl")
print(f"✅ {len(teams)} teams saved to data/model/teams_list.json")