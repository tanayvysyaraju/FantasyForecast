import requests, os, json
import pandas as pd
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

SWID = os.getenv("SWID")
ESPN_S2 = os.getenv("ESPN_S2")
SEASON = os.getenv("LEAGUE_YEAR")

def get_top_player_ids(limit=25):
    url = f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/2024/players?view=players_wl"
    headers = {
        "X-Fantasy-Filter": json.dumps({
            "players": {
                "limit": limit,
                "sortPercOwned": {
                    "sortAsc": False,
                    "sortPriority": 1
                }
            }
        }),
        "User-Agent": "Mozilla/5.0"
    }
    cookies = {"espn_s2": ESPN_S2, "SWID": SWID}
    response = requests.get(url, headers=headers, cookies=cookies)
    try:
        return [p["id"] for p in response.json()]
    except Exception as e:
        print("❌ JSON parsing failed:", e)
        print("💡 This probably means your cookies are missing, expired, or wrong.")
        return []

def get_kona_player_info():
    # Get PPR_ID from your league or try 0/1/2 (usually 0 works)
    url = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/2024/segments/0/leaguedefaults/0?view=kona_player_info"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    return response.json()

def extract_stats(player_data, top_ids):
    top_players = [p for p in player_data['players'] if p['id'] in top_ids]
    stat_categories = player_data['categories']

    readable_stats = []
    for p in top_players:
        stats = {}
        stats['name'] = p['player']['fullName']
        stats['position'] = p['player']['defaultPositionId']
        stats['team'] = p['player'].get('proTeamId')
        for s in p.get('stats', []):
            if s.get('id') == 0:  # id=0 is season total stats
                stats['fantasy_points'] = s.get('appliedTotal')
                break
        readable_stats.append(stats)

    return readable_stats

def print_readable_stats(readable_stats):
    for player in readable_stats:
        print(f"{player['name']} - Pos: {player['position']}, Team ID: {player['team']}, Fantasy Points: {player.get('fantasy_points', 'N/A')}")

def extract_stats(kona_data, top_ids):
    players = kona_data['players']
    stat_list = []

    for p in players:
        if p['id'] in top_ids:
            stats = {
                'name': p['player']['fullName'],
                'position': p['player'].get('defaultPositionId'),
                'team': p['player'].get('proTeamId'),
                'fantasy_points': None
            }
            for s in p.get('stats', []):
                if s.get('id') == 0:  # season total stats
                    stats['fantasy_points'] = s.get('appliedTotal')
                    break
            stat_list.append(stats)

    return pd.DataFrame(stat_list)

def print_stats_table(df, top_n=25):
    df = df.sort_values(by='fantasy_points', ascending=False)
    table = df[['name', 'position', 'team', 'fantasy_points']].head(top_n)
    print(tabulate(table, headers='keys', tablefmt='pretty'))



