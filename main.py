import pandas as pd

games = pd.read_parquet("data/raw/2025/games.parquet")

print(games.columns.tolist())
print()
print(games.head())

import pandas as pd

plays = pd.read_parquet("data/cleaned/2025/plays_clean.parquet")

offenses = (
    plays[
        plays["isOffensivePlay"]
    ]
    .groupby("gameId")["offense"]
    .nunique()
)

print(offenses.value_counts())

games = pd.read_parquet("data/raw/2025/games.parquet")

print(games[[
    "id",
    "homeTeam",
    "awayTeam"
]].head())