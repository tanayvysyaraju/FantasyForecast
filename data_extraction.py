import json
import os
import pandas as pd
import numpy as np
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

def collect_advanced_player_stats(season, weeks):
    stats_api = Stats()
    players_api = Players()
    all_players = load_all_players(players_api)
    trending_players_raw = players_api.get_trending_players("nfl", "add", 24, 200)
    trending_ids = {str(player["player_id"]) for player in trending_players_raw}

    player_data = {}

    for week in weeks:
        week_stats = stats_api.get_week_stats("regular", season, week)
        week_projections = stats_api.get_week_projections("regular", season, week)

        for player_id, stat in week_stats.items():
            player_info = all_players.get(player_id)

            if not player_info or player_id.startswith("TEAM_"):
                continue

            position = player_info.get("position")
            team = player_info.get("team")
            name = player_info.get("full_name")

            # Generate readable name for defenses
            if not name:
                if position == "DEF" and team:
                    name = f"{team} DEF"
                else:
                    name = "Unknown"

            if player_id not in player_data:
                player_data[player_id] = {
                    "name": name,
                    "position": position,
                    "team": team,
                    "bye_week": player_info.get("bye_week", None),
                    "total_points": 0,
                    "weekly_points": [],
                    "injury_weeks_missed": 0,
                    "projection_diffs": [],
                    "projection_hits": [],
                    "boom_games": 0,
                    "bust_games": 0,
                    "total_over": 0
                }

            actual = stat.get("pts_ppr")
            projected = week_projections.get(player_id, {}).get("pts_ppr")

            if actual is not None:
                pdata = player_data[player_id]
                pdata["total_points"] += actual
                if actual > 10:
                    pdata["total_over"] += 1
                pdata["weekly_points"].append(actual)
                if actual > 20:
                    pdata["boom_games"] += 1
                if actual < 5:
                    pdata["bust_games"] += 1

                if projected is not None:
                    diff = actual - projected
                    pdata["projection_diffs"].append(diff)
                    pdata["projection_hits"].append(1 if diff > 0 else 0)
            else:
                player_data[player_id]["injury_weeks_missed"] += 1

    # Output dataframes
    trade, waiver = [], []

    for pid, pdata in player_data.items():
        points = pdata["weekly_points"]
        diffs = pdata["projection_diffs"]
        hits = pdata["projection_hits"]

        avg_last_3 = sum(points[-3:]) / min(3, len(points)) if points else 0
        avg_projection_diff = sum(diffs) / len(diffs) if diffs else 0
        projection_accuracy = sum(hits) / len(hits) if hits else 0
        volatility = np.std(points) if points else 0
        ros_projection = np.mean(points) * (17 - len(points)) if points else 0
        trade_score = (
            avg_last_3 * 0.5 +
            projection_accuracy * 20 +
            avg_projection_diff * 0.3 +
            pdata["boom_games"] * 0.3 -
            pdata["bust_games"] * 0.5 -
            pdata["injury_weeks_missed"] * 1.0
        )

        trade.append({
            "name": pdata["name"],
            "position": pdata["position"],
            "team": pdata["team"],
            "total_points": pdata["total_points"],
            "projected_points": ros_projection,
            "injury_weeks_missed": pdata["injury_weeks_missed"],
            "avg_projection_diff": avg_projection_diff,
            "projection_accuracy": projection_accuracy,
            "volatility": volatility,
            "rest_of_season_projection": ros_projection,
            "trade_value_score": trade_score,
            "consistency_rating": pdata.get("total_over", 0) / len(weeks)
        })

        if pid in trending_ids and avg_last_3 > 10:
            waiver.append({
                "name": pdata["name"],
                "position": pdata["position"],
                "team": pdata["team"],
                "total_points": pdata["total_points"],
                "rest_of_season_projection": ros_projection,
                "volatility": volatility,
                "boom_games": pdata["boom_games"],
                "upside_score": pdata["boom_games"] * avg_last_3,
                "avg_pts_last_3": avg_last_3,
                "games_played": len(points)
            })

    

    trade_df = pd.DataFrame(trade)
    trade_df["position_rank"] = (
        trade_df.groupby("position")["trade_value_score"]
        .rank(ascending=False, method="dense")
        .astype(int)
    )

    return pd.DataFrame(waiver), trade_df
