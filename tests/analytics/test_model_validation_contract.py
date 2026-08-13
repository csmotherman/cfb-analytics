from cfb_analytics.analytics.iterative_ratings import ITERATIVE_FEATURES
from cfb_analytics.analytics.walk_forward_baseline import FEATURES as RAW

FAMILIES={
 'Success':('home_iterativeSuccessEdge','away_iterativeSuccessEdge'),
 'Explosive':('home_iterativeExplosiveEdge','away_iterativeExplosiveEdge'),
 'YardsPerPlay':('home_iterativeYardsPerPlayEdge','away_iterativeYardsPerPlayEdge'),
 'YardsPerPossession':('home_iterativeYardsPerPossessionEdge','away_iterativeYardsPerPossessionEdge'),
 'Finishing':('home_iterativeFinishingEdge','away_iterativeFinishingEdge'),
 'FieldPosition':('home_iterativeFieldPositionEdge','away_iterativeFieldPositionEdge'),
}

def test_current_learning_feature_counts_are_locked():
 assert len(RAW)==14
 assert len(ITERATIVE_FEATURES)==12
 assert len(tuple(RAW)+tuple(ITERATIVE_FEATURES))==26

def test_iterative_family_partition_is_complete_and_unique():
 flattened=[feature for pair in FAMILIES.values() for feature in pair]
 assert len(flattened)==12
 assert len(set(flattened))==12
 assert set(flattened)==set(ITERATIVE_FEATURES)

def test_leave_one_family_out_removes_exactly_two_features():
 for pair in FAMILIES.values():
  remaining=tuple(feature for feature in ITERATIVE_FEATURES if feature not in pair)
  assert len(remaining)==10
  assert not set(pair).intersection(remaining)
