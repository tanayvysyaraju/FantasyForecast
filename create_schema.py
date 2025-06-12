from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float

# Replace with your PostgreSQL credentials
engine = create_engine("postgresql+psycopg2://tanayvysyaraju@localhost:5432/fantasy_forecast")
metadata = MetaData()

# 🟦 Trade Metrics Table (corresponds to `trade` DataFrame)
trade_metrics = Table(
    "trade_metrics", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String),
    Column("position", String),
    Column("team", String),
    Column("total_points", Float),
    Column("projected_points", Float),
    Column("injury_weeks_missed", Integer),
    Column("avg_projection_diff", Float),
    Column("projection_accuracy", Float),
    Column("volatility", Float),
    Column("rest_of_season_projection", Float),
    Column("trade_value_score", Float),
    Column("consistency_rating", Float)
)

# 🟩 Waiver Trends Table (corresponds to `waiver` DataFrame)
waiver_trends = Table(
    "waiver_trends", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String),
    Column("position", String),
    Column("team", String),
    Column("total_points", Float),
    Column("rest_of_season_projection", Float),
    Column("volatility", Float),
    Column("boom_games", Integer),
    Column("upside_score", Float),
    Column("avg_pts_last_3", Float),
    Column("games_played", Integer)
)

# Create the tables
metadata.create_all(engine)
print("✅ 'trade_metrics' and 'waiver_trends' tables created.")
