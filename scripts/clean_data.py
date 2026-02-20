import pandas as pd

matches = pd.read_csv('data/WorldCupMatches.csv')
cups = pd.read_csv('data/WorldCups.csv')

print(f"Before cleaning: {len(matches)} rows")

# Drop rows missing critical fields
matches = matches.dropna(subset=['Home Team Name', 'Away Team Name', 'Home Team Goals', 'Away Team Goals'])

# Remove duplicate matches (same MatchID appears twice in this dataset — known issue)
matches = matches.drop_duplicates(subset=['MatchID'])

# Convert goals to int
matches['Home Team Goals'] = matches['Home Team Goals'].astype(int)
matches['Away Team Goals'] = matches['Away Team Goals'].astype(int)
matches['Year'] = matches['Year'].astype(int)

# Add result column
def get_result(row):
    if row['Home Team Goals'] > row['Away Team Goals']:
        return f"{row['Home Team Name']} won"
    elif row['Home Team Goals'] < row['Away Team Goals']:
        return f"{row['Away Team Name']} won"
    else:
        return "Draw"

matches['Result'] = matches.apply(get_result, axis=1)

# Save
matches.to_csv('data/matches_clean.csv', index=False)
cups.to_csv('data/cups_clean.csv', index=False)

print(f"After cleaning: {len(matches)} rows")
print(f"Years covered: {sorted(matches['Year'].unique())}")
print(f"✅ Saved to data/matches_clean.csv")