import json
import os
import pandas as pd
from sleeper_wrapper import Stats, Players

def load_all_players(players_api, cache_file="players_cache.json"):
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            all_players = json.load(f)
        print("✅ Loaded player data from cache.")
    else:
        all_players = players_api.get_all_players()
        with open(cache_file, "w") as f:
            json.dump(all_players, f)
        print("📦 Cached player data to file.")
    return all_players

def collect_advanced_player_stats(season, weeks, position_filter=None):
    stats_api = Stats()
    players_api = Players()
    all_players = load_all_players(players_api)

    player_data = {}

    for week in weeks:
        week_stats = stats_api.get_week_stats("regular", season, week)
        week_projections = stats_api.get_week_projections("regular", season, week)

        for player_id, stat in week_stats.items():
            player_info = all_players.get(player_id)

            if (
                not player_info or
                not player_info.get("full_name") or
                player_info.get("position") == "DEF" or
                player_id.startswith("TEAM_")
            ):
                continue

            if position_filter and player_info.get("position") not in position_filter:
                continue

            if player_id not in player_data:
                player_data[player_id] = {
                    "name": player_info.get("full_name", "Unknown"),
                    "position": player_info.get("position"),
                    "team": player_info.get("team"),
                    "total_points": 0,
                    "weekly_points": [],
                    "injury_weeks_missed": 0,
                    "projection_diffs": [],
                    "projection_hits": []
                }

            actual = stat.get("pts_ppr")
            projected = week_projections.get(player_id, {}).get("pts_ppr")

            if actual is not None:
                pdata = player_data[player_id]
                pdata["total_points"] += actual
                pdata["weekly_points"].append(actual)

                if projected is not None:
                    diff = actual - projected
                    pdata["projection_diffs"].append(diff)
                    pdata["projection_hits"].append(1 if diff > 0 else 0)
            else:
                player_data[player_id]["injury_weeks_missed"] += 1

    # Normal stats
    normal = [
        {
            "name": pdata["name"],
            "position": pdata["position"],
            "team": pdata["team"],
            "total_points": pdata["total_points"]
        }
        for pdata in player_data.values()
    ]

    # Engineered features
    enriched = []
    for pdata in player_data.values():
        points = pdata["weekly_points"]
        boom = sum(p > 20 for p in points)
        bust = sum(p < 5 for p in points)
        diffs = pdata["projection_diffs"]
        hits = pdata["projection_hits"]

        enriched.append({
            "name": pdata["name"],
            "position": pdata["position"],
            "team": pdata["team"],
            "avg_pts_last_3": sum(points[-3:]) / min(3, len(points)) if points else 0,
            "boom_games": boom,
            "bust_games": bust,
            "injury_weeks_missed": pdata["injury_weeks_missed"],
            "avg_projection_diff": sum(diffs) / len(diffs) if diffs else 0,
            "projection_accuracy": sum(hits) / len(hits) if hits else 0
        })

    return pd.DataFrame(normal), pd.DataFrame(enriched)
