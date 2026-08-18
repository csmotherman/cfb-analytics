# Games Contract

Grain: one scheduled game. Key: `game_id` (CFBD `id`). Required fields are season, week, season type, home/away IDs and teams, classifications, conferences, points, neutral-site flag, completion state, start time, and venue where supplied. Source fields are nullable when CFBD has not populated them; IDs, season, participants, and week are non-null quality gates for publication.

