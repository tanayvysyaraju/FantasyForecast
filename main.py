# main.py
from data_extraction import collect_advanced_player_stats
from tabulate import tabulate

def main():
    season = 2024
    weeks = list(range(1,12))  # Weeks 1 through 10

    waiverDf, tradeDf = collect_advanced_player_stats(season=season, weeks=weeks)

    print("\nTop 200 Players by Avg Points:\n")
    topwa_df = waiverDf.sort_values(by="total_points", ascending=False).head(200)
    print(tabulate(topwa_df, headers='keys', tablefmt='pretty'))

    print("\nTop 200 players by trade value\n")
    toptd_df = tradeDf.sort_values(by="trade_value_score", ascending=False).head(200)
    print(tabulate(toptd_df, headers='keys', tablefmt='pretty'))

if __name__ == "__main__":
    main()
