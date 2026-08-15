"""Fan-facing team profile research layer.

Raw metrics remain authoritative; this package converts them into comparable
season-relative grades, historical fingerprints, and explainable archetypes.
"""

from .archetypes import classify_archetypes
from .archetype_catalog import CATALOG, CATALOG_VERSION
from .contract import PROFILE_METRICS, PROFILE_VERSION
from .grades import grade_percentile, percentile_rank
from .match_archetypes import match_snapshot
from .similarity import historical_comparables

__all__ = [
    "CATALOG",
    "CATALOG_VERSION",
    "PROFILE_METRICS",
    "PROFILE_VERSION",
    "classify_archetypes",
    "grade_percentile",
    "historical_comparables",
    "match_snapshot",
    "percentile_rank",
]
