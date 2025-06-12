# main.py
from data_extraction import collect_advanced_player_stats
from tabulate import tabulate

def main():

    # After generating the dataframes from collect_advanced_player_stats()
    waiver_df, trade_df = collect_advanced_player_stats(season=2024, weeks=range(1, 17))

    # Insert into PostgreSQL
    from sqlalchemy import create_engine
    engine = create_engine("postgresql+psycopg2://tanayvysyaraju@localhost:5432/fantasy_forecast")

    trade_df.to_sql("trade_metrics", engine, if_exists="replace", index=False)
    waiver_df.to_sql("waiver_trends", engine, if_exists="replace", index=False)
    print("✅ Data inserted into PostgreSQL.")


if __name__ == "__main__":
    main()
