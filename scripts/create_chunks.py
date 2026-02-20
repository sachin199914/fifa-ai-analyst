import pandas as pd
import json

matches = pd.read_csv('data/matches_clean.csv')
cups = pd.read_csv('data/cups_clean.csv')

chunks = []

# --- Chunk Type 1: Individual match summaries ---
for _, row in matches.iterrows():
    text = f"""
FIFA World Cup {row['Year']} - Stage: {row['Stage']}
Match: {row['Home Team Name']} vs {row['Away Team Name']}
Score: {row['Home Team Goals']} - {row['Away Team Goals']}
Result: {row['Result']}
Venue: {row['Stadium']}, {row['City']}
Attendance: {row['Attendance']}
""".strip()

    chunks.append({
        "id": f"match_{row['MatchID']}",
        "text": text,
        "metadata": {
            "type": "match",
            "year": str(row['Year']),
            "home_team": row['Home Team Name'],
            "away_team": row['Away Team Name'],
            "stage": row['Stage']
        }
    })

# --- Chunk Type 2: Tournament summaries ---
for _, row in cups.iterrows():
    text = f"""
FIFA World Cup {row['Year']} was held in {row['Country']}.
Winner: {row['Winner']}
Runner-up: {row['Runners-Up']}
Third place: {row['Third']}
Total goals scored: {row['GoalsScored']}
Total matches played: {row['MatchesPlayed']}
Total attendance: {row['Attendance']}
""".strip()

    chunks.append({
        "id": f"tournament_{row['Year']}",
        "text": text,
        "metadata": {
            "type": "tournament",
            "year": str(row['Year']),
            "winner": row['Winner'],
            "host": row['Country']
        }
    })

# --- Chunk Type 3: Team history summaries (with titles) ---

# Count titles per team
titles = {}
for _, row in cups.iterrows():
    winner = row['Winner']
    if winner not in titles:
        titles[winner] = []
    titles[winner].append(str(row['Year']))

# Build team stats from matches
team_stats = {}

for _, row in matches.iterrows():
    for team, is_home in [(row['Home Team Name'], True), (row['Away Team Name'], False)]:
        if team not in team_stats:
            team_stats[team] = {
                "years": set(),
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_scored": 0
            }

        team_stats[team]["years"].add(row['Year'])

        goals_for = row['Home Team Goals'] if is_home else row['Away Team Goals']
        goals_against = row['Away Team Goals'] if is_home else row['Home Team Goals']

        team_stats[team]["goals_scored"] += goals_for

        if goals_for > goals_against:
            team_stats[team]["wins"] += 1
        elif goals_for == goals_against:
            team_stats[team]["draws"] += 1
        else:
            team_stats[team]["losses"] += 1

# Create one chunk per team
for team, stats in team_stats.items():
    total = stats["wins"] + stats["draws"] + stats["losses"]
    win_rate = round((stats["wins"] / total) * 100, 1) if total > 0 else 0

    team_titles = titles.get(team, [])
    title_text = (
        f"Won {len(team_titles)} World Cup(s) in {', '.join(team_titles)}"
        if team_titles
        else "Has not won a World Cup"
    )

    text = f"""
{team} FIFA World Cup History:
{title_text}
Participated in {len(stats['years'])} World Cups: {sorted(stats['years'])}
Overall record: {stats['wins']} wins, {stats['draws']} draws, {stats['losses']} losses
Win rate: {win_rate}%
Total goals scored: {stats['goals_scored']}
""".strip()

    chunks.append({
        "id": f"team_{team.replace(' ', '_').replace('/', '_')}",
        "text": text,
        "metadata": {
            "type": "team_history",
            "team": team
        }
    })

# --- Save all chunks ---
with open('data/chunks.json', 'w') as f:
    json.dump(chunks, f, indent=2)

print(f"✅ Total chunks created: {len(chunks)}")
print(f"   Match chunks:      {sum(1 for c in chunks if c['metadata']['type'] == 'match')}")
print(f"   Tournament chunks: {sum(1 for c in chunks if c['metadata']['type'] == 'tournament')}")
print(f"   Team chunks:       {sum(1 for c in chunks if c['metadata']['type'] == 'team_history')}")

# Preview a few team chunks to verify titles
print("\n--- Preview: Teams with World Cup titles ---")
for team, year_list in titles.items():
    print(f"  {team}: {', '.join(year_list)}")