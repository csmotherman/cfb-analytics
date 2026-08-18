# Teams Contract

Grain: one team in one season. Key: `(season, team_id)`.

| Name | Type | Nullable | Source / definition |
|---|---|---:|---|
| season | integer | no | Source season |
| team_id | integer | no | CFBD stable team ID |
| team | string | no | Canonical source name |
| canonical_team_name | string | no | Canonical name |
| display_name | string | no | Consumer label |
| slug | string | no | Deterministic ASCII lowercase slug |
| conference | string | yes | Season-aware source conference |
| classification | string | yes | Source classification |
| division | string | yes | Derived subdivision label |
| source_game_observations | integer | no | Number of broad source games supporting season membership |

The broad-ingestion membership artifact is `data/canonical/season={season}/fbs_membership`. Only source-classified FBS participants appear; non-FBS opponents remain in the game fact contract.
