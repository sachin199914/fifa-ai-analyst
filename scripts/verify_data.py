import pandas as pd
import os

files = {
    'WorldCupMatches.csv': 'data/WorldCupMatches.csv',
    'WorldCupPlayers.csv': 'data/WorldCupPlayers.csv',
    'WorldCups.csv':       'data/WorldCups.csv',
    'results.csv':         'data/results.csv'
}

for name, path in files.items():
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"✅ {name} — {len(df)} rows, columns: {df.columns.tolist()}")
    else:
        print(f"❌ {name} — NOT FOUND, check your data/ folder")