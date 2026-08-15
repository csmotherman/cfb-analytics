from __future__ import annotations

from dataclasses import dataclass

PROFILE_VERSION = "team-profile-v1-research"


@dataclass(frozen=True)
class ProfileMetric:
    key: str
    section: str
    label: str
    higher_is_better: bool
    role: str
    status: str
    description: str


PROFILE_METRICS = (
    ProfileMetric("run_efficiency_off", "offense", "Run Efficiency", True, "quality", "READY", "How efficiently the offense runs relative to peers."),
    ProfileMetric("pass_efficiency_off", "offense", "Pass Efficiency", True, "quality", "READY", "How efficiently the offense passes relative to peers."),
    ProfileMetric("explosiveness_off", "offense", "Explosiveness", True, "quality", "READY", "Ability to create explosive offensive plays."),
    ProfileMetric("success_off", "offense", "Success Rate", True, "quality", "READY", "Down-and-distance efficiency."),
    ProfileMetric("drive_scoring_off", "offense", "Drive Scoring Efficiency", True, "quality", "RESEARCH", "Opponent-adjusted offensive points per drive."),
    ProfileMetric("finishing_off", "offense", "Finishing", True, "quality", "READY", "Scoring efficiency after reaching opportunity territory."),
    ProfileMetric("turnover_avoidance", "offense", "Turnover Avoidance", True, "quality", "READY", "Ability to avoid giveaways."),
    ProfileMetric("third_down_off", "offense", "Third-Down Efficiency", True, "quality", "READY", "Ability to extend drives on third down."),
    ProfileMetric("run_efficiency_def", "defense", "Run Defense", True, "quality", "READY", "Ability to suppress opposing rushing efficiency."),
    ProfileMetric("pass_efficiency_def", "defense", "Pass Defense", True, "quality", "READY", "Ability to suppress opposing passing efficiency."),
    ProfileMetric("explosive_prevention", "defense", "Explosive Prevention", True, "quality", "READY", "Ability to prevent explosive plays."),
    ProfileMetric("drive_suppression_def", "defense", "Drive Suppression", True, "quality", "RESEARCH", "Opponent-adjusted points prevented per drive."),
    ProfileMetric("havoc_def", "defense", "Havoc", True, "quality", "READY", "Negative plays, sacks, and turnover disruption."),
    ProfileMetric("turnover_creation", "defense", "Turnover Creation", True, "quality", "READY", "Ability to create takeaways."),
    ProfileMetric("third_down_def", "defense", "Third-Down Defense", True, "quality", "READY", "Ability to end drives on third down."),
    ProfileMetric("rush_rate", "style", "Run Tendency", True, "style", "READY", "How run-heavy the offense is relative to peers."),
    ProfileMetric("pass_rate", "style", "Pass Tendency", True, "style", "READY", "How pass-heavy the offense is relative to peers."),
    ProfileMetric("tempo", "style", "Tempo", True, "style", "PARTIAL", "How quickly the team creates possessions and snaps."),
    ProfileMetric("plays_per_possession", "style", "Drive Length", True, "style", "READY", "How many plays the offense sustains per possession."),
    ProfileMetric("aggressiveness", "style", "Aggressiveness", True, "style", "PLANNED", "Fourth-down and situational willingness to attack."),
    ProfileMetric("drive_consistency", "style", "Drive Consistency", True, "style", "PLANNED", "How stable drive-to-drive offensive output is."),
    ProfileMetric("drive_volatility", "style", "Drive Volatility", True, "style", "PLANNED", "How variable drive-to-drive output is."),
)

PROFILE_KEYS = tuple(metric.key for metric in PROFILE_METRICS)
PROFILE_BY_KEY = {metric.key: metric for metric in PROFILE_METRICS}
