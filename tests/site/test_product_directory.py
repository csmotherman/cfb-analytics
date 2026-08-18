from cfb_analytics.site.product_directory import PRODUCT_MANIFEST, SITE_TREE, print_tree


def test_primary_fan_routes_are_present():
    routes = {item["route"] for item in PRODUCT_MANIFEST["navigation"]}
    assert routes == {"/football/2026", "/football/[season]", "/schedule", "/rankings", "/compare", "/metrics"}


def test_landing_page_is_answer_first():
    landing = PRODUCT_MANIFEST["landingPage"]
    assert landing["hero"]["headline"] == "Know exactly where Michigan stands."
    assert landing["modules"][0]["id"] == "fan_questions"
    assert landing["modules"][1]["id"] == "power_snapshot"
    assert landing["modules"][2]["id"] == "featured_simulation"
    assert landing["modules"][-1]["id"] == "methodology_tease"


def test_metric_language_preserves_plain_and_technical_names():
    metrics = PRODUCT_MANIFEST["fanMetricLanguage"]
    for spec in metrics.values():
        assert spec["surfaceLabel"]
        assert spec["fanQuestion"].endswith("?")
        assert spec["technicalLabel"]


def test_team_page_answers_fan_questions_above_fold():
    team = PRODUCT_MANIFEST["pageContracts"]["teamSeason"]
    assert "How good was this team?" in team["fanQuestions"]
    assert "primary strength" in team["aboveFold"]
    assert "primary weakness" in team["aboveFold"]
    assert team["sections"][0] == "The 30-second answer"
    assert team["sections"][-1] == "Advanced breakdown"


def test_frontend_tree_has_core_michigan_pages_and_data_adapter():
    required = {
        "app/page.tsx",
        "app/michigan/page.tsx",
        "app/football/[season]/page.tsx",
        "app/schedule/page.tsx",
        "app/teams/[team]/[season]/page.tsx",
        "app/compare/page.tsx",
        "components/MichiganHome.tsx",
        "lib/michigan.ts",
    }
    assert required.issubset(set(SITE_TREE))
    rendered = print_tree()
    assert rendered.startswith("website/\n")
    assert "app/michigan/page.tsx" in rendered
