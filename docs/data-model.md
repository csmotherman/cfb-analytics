# Data Model

## Principle

Every dataset has one declared grain and one responsibility. Raw data is immutable. Clean data standardizes source fields and adds only deterministic context needed by later analytics. Derived analytics never overwrite clean source columns.

## Directory layout

```text
data/
  raw/{season}/
    games.parquet
    drives.parquet
    plays.parquet
  clean/{season}/
    games.parquet
    drives.parquet
    plays.parquet
  derived/{season}/
    team_game.parquet      # future
    team_season.parquet    # future
  adjusted/{season}/       # future
```

## Games

**Grain:** one row per game.

Required canonical fields:

- `game_id`
- `season`
- `week`
- `season_type`
- `home_team`, `away_team`
- `home_conference`, `away_conference`
- `home_classification`, `away_classification`
- `home_points`, `away_points`
- `completed`
- `is_fbs_vs_fbs`

## Drives

**Grain:** one row per drive.

Required canonical fields:

- `drive_id`
- `game_id`
- `offense`, `defense`
- `drive_number`
- `start_period`, `start_yards_to_goal`
- `end_period`, `end_yards_to_goal`
- `plays`, `yards`
- `start_offense_score`, `end_offense_score`
- `drive_result`
- derived: `drive_points`, `is_scoring_drive`, `is_touchdown_drive`, `is_turnover_drive`, `is_punt_drive`, `is_three_and_out`

## Plays

**Grain:** one row per play.

Identity and joins:

- `play_id`
- `game_id`
- `drive_id`
- `drive_number`
- `play_number`

Context:

- `season`, `week`
- `offense`, `defense`
- `period`, `minutes`, `seconds`, `game_seconds_remaining`
- `down`, `distance`, `yards_to_goal`, `field_position`

Source outcome:

- `play_type`, `play_text`
- `yards_gained`, `ppa`, `scoring`

Derived deterministic flags:

- `play_family`
- `is_run`, `is_pass`, `is_sack`, `is_kneel`, `is_spike`
- `is_offensive_play`, `is_competitive_offensive_play`
- `is_turnover`, `is_penalty`, `is_special_teams`
- `is_success`, `is_explosive`, `is_negative_play`
- `is_red_zone`, `is_goal_to_go`, `is_standard_down`, `is_passing_down`

## Future grains

`team_game` will be the canonical analytics fact table: exactly one row for each team in each eligible game. Offensive values must reconcile to the opponent's defensive mirror.

`team_season` will aggregate validated `team_game` rows. Opponent adjustment and ratings occur only after season aggregation inputs are stable.
