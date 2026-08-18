# Team Games Contract

Grain: exactly one team in one game. Key: `(game_id, team_id)`; a normal retained game has two symmetric rows.

Identity/source columns are `season` (integer), `week` (integer), `season_type` (string), `game_id` (string), `team_id`/`opponent_id` (integer), team/opponent names and slugs (string), season-aware conferences/classifications (nullable string), `home_away` (home/away), `neutral_site` (boolean), points for/against (nullable integer), and win/loss (nullable 0/1).

Derived columns retain the locked camelCase schemas: possession/play/yard counts; success eligible/successful/rate families by side, play family, and down; explosive counts/rates and successful-play yards; finishing-drive counts/rates; field position; turnovers; TFL/havoc; situational/down; red-zone; drive efficiency; first downs; dropbacks; basic yardage; validation status/issues; and definition-version strings. Rates are nullable when their denominator is zero. The authoritative calculation is always the documented numerator divided by denominator, never the displayed rank.

