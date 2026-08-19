from cfb_analytics.pipelines.publish_michigan_player_images import build


def test_build_matches_exact_and_known_short_name():
    page = '''<a href="/sports/football/roster/jonah/1" aria-label="Jonah Lea&#39;ea jersey number 1 full bio"><source srcset="x?url=https%3A%2F%2Fcdn.example%2Fjonah.jpg&amp;width=100"><a href="/sports/football/roster/cam/2" aria-label="Cam Brandt jersey number 2 full bio"><source srcset="x?url=https%3A%2F%2Fcdn.example%2Fcam.jpg&amp;width=100">'''
    roster = [{"id": 1, "firstName": "Jonah", "lastName": "Lea'ea"}, {"id": 2, "firstName": "Cameron", "lastName": "Brandt"}]
    result = build(page, roster, "2026-08-19")
    assert [row["playerId"] for row in result] == ["1", "2"]
    assert result[0]["imageUrl"] == "https://cdn.example/jonah.jpg"


def test_build_omits_players_without_official_image():
    assert build("", [{"id": 1, "firstName": "No", "lastName": "Photo"}], "2026-08-19") == []
