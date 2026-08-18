# Drives Contract

Grain: one reconstructed possession group within a game. Stable identity is `(game_id, drive_id)`. It carries offense, defense, start/end state and scores, play count, reconstructed yardage, outcome, possession flag, validation status/issues, and schema version. Review drives remain evidence but are excluded from metrics requiring validated possessions. Overtime is retained and explicitly excluded only by metric contracts such as DDR.

