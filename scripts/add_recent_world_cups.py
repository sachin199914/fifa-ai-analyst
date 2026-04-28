import pandas as pd
import uuid

print("Loading data...")
# 1. Update cups_clean.csv
cups = pd.read_csv('data/cups_clean.csv')

new_cups = [
    {
        'Year': 2018, 'Country': 'Russia', 'Winner': 'France', 'Runners-Up': 'Croatia',
        'Third': 'Belgium', 'Fourth': 'England', 'GoalsScored': 169,
        'QualifiedTeams': 32, 'MatchesPlayed': 64, 'Attendance': '3.031.768'
    },
    {
        'Year': 2022, 'Country': 'Qatar', 'Winner': 'Argentina', 'Runners-Up': 'France',
        'Third': 'Croatia', 'Fourth': 'Morocco', 'GoalsScored': 172,
        'QualifiedTeams': 32, 'MatchesPlayed': 64, 'Attendance': '3.404.252'
    }
]

cups = pd.concat([cups, pd.DataFrame(new_cups)], ignore_index=True)
cups.drop_duplicates(subset=['Year'], keep='last', inplace=True)
cups.to_csv('data/cups_clean.csv', index=False)
print("Updated cups_clean.csv with 2018 and 2022 data.")

# 2. Update matches_clean.csv
matches = pd.read_csv('data/matches_clean.csv')
results = pd.read_csv('data/results.csv')

# Filter 2018 and 2022 WC matches from results.csv
recent_wc_matches = results[
    (results['tournament'] == 'FIFA World Cup') &
    (results['date'].str.startswith('2018') | results['date'].str.startswith('2022'))
]

new_matches = []
for _, row in recent_wc_matches.iterrows():
    year = int(row['date'][:4])
    home = row['home_team']
    away = row['away_team']
    hg = row['home_score']
    ag = row['away_score']
    
    if hg > ag:
        res = f"{home} won"
    elif hg < ag:
        res = f"{away} won"
    else:
        res = "Draw"
        
    new_matches.append({
        'Year': year,
        'Datetime': row['date'],
        'Stage': 'FIFA World Cup',
        'Stadium': 'Unknown',
        'City': row['city'],
        'Home Team Name': home,
        'Home Team Goals': hg,
        'Away Team Goals': ag,
        'Away Team Name': away,
        'Win conditions': '',
        'Attendance': 0,
        'Half-time Home Goals': 0,
        'Half-time Away Goals': 0,
        'Referee': '',
        'Assistant 1': '',
        'Assistant 2': '',
        'RoundID': 0,
        'MatchID': str(uuid.uuid4()),
        'Home Team Initials': home[:3].upper() if isinstance(home, str) else '',
        'Away Team Initials': away[:3].upper() if isinstance(away, str) else '',
        'Result': res
    })

matches = pd.concat([matches, pd.DataFrame(new_matches)], ignore_index=True)
matches.drop_duplicates(subset=['Datetime', 'Home Team Name', 'Away Team Name'], keep='last', inplace=True)
matches.to_csv('data/matches_clean.csv', index=False)
print(f"Updated matches_clean.csv with {len(recent_wc_matches)} recent matches.")
print("Done!")
