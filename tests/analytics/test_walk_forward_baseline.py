from cfb_analytics.analytics.walk_forward_baseline import FEATURES, evaluate


def row(i, margin):
    r={k:float(i+j)/10 for j,k in enumerate(FEATURES)}
    r.update({"target_margin":float(margin),"target_homeWin":1 if margin>0 else 0,"homeHistoryAvailable":True,"awayHistoryAvailable":True})
    return r


def test_baseline_fits_and_scores_without_external_dependencies():
    train=[row(i, i-8) for i in range(1,17)]
    test=[row(17,9),row(18,10),row(19,11)]
    result=evaluate(train,test)
    assert result["train_games"]==16
    assert result["test_games"]==3
    assert result["margin_mae"]>=0
    assert result["margin_rmse"]>=0
    assert 0<=result["winner_accuracy"]<=1
