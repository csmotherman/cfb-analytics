from cfb_analytics.analytics.roster_continuity import build_summary, classify_current_roster


def _player(pid: str, first: str, last: str, *, year: int = 2, position: str = "WR"):
    return {
        "id": pid,
        "firstName": first,
        "lastName": last,
        "team": "Western Michigan",
        "year": year,
        "position": position,
    }


def test_classifies_returning_transfer_and_new_player():
    previous = [_player("1", "Return", "Guy", year=1), _player("2", "Name", "Match", year=2)]
    current = [
        _player("1", "Return", "Guy", year=2),
        _player("99", "Name", "Match", year=3),
        _player("3", "Portal", "Guy", year=3, position="DL"),
        _player("4", "Fresh", "Guy", year=1, position="QB"),
    ]
    portal = [
        {
            "firstName": "Portal",
            "lastName": "Guy",
            "position": "DL",
            "origin": "Another State",
            "destination": "Western Michigan",
            "stars": 3,
            "rating": 0.84,
        }
    ]

    rows = classify_current_roster(current, previous, portal, "Western Michigan")
    by_name = {row["name"]: row for row in rows}

    assert by_name["Return Guy"]["status"] == "returning"
    assert by_name["Name Match"]["status"] == "returning"
    assert by_name["Portal Guy"]["status"] == "transfer_in"
    assert by_name["Portal Guy"]["transfer_origin"] == "Another State"
    assert by_name["Fresh Guy"]["status"] == "new_other"


def test_returning_match_takes_priority_over_portal_entry():
    previous = [_player("1", "Came", "Back")]
    current = [_player("1", "Came", "Back")]
    portal = [
        {
            "firstName": "Came",
            "lastName": "Back",
            "origin": "Western Michigan",
            "destination": "Western Michigan",
        }
    ]

    rows = classify_current_roster(current, previous, portal, "Western Michigan")
    assert rows[0]["status"] == "returning"


def test_summary_reports_roster_share_and_portal_context():
    previous = [_player("1", "Return", "Guy")]
    current = [
        _player("1", "Return", "Guy", year=3, position="LB"),
        _player("2", "Transfer", "Guy", year=4, position="DB"),
    ]
    portal = [
        {
            "firstName": "Transfer",
            "lastName": "Guy",
            "position": "DB",
            "origin": "Old School",
            "destination": "Western Michigan",
        },
        {
            "firstName": "Gone",
            "lastName": "Guy",
            "position": "WR",
            "origin": "Western Michigan",
            "destination": "New School",
        },
    ]

    summary = build_summary(current, previous, portal, "Western Michigan", 2026)

    assert summary["currentRosterCount"] == 2
    assert summary["returningPlayers"] == 1
    assert summary["returningRosterShare"] == 0.5
    assert summary["transferInsOnCurrentRoster"] == 1
    assert summary["portalEntriesIntoTeam"] == 1
    assert summary["portalEntriesOutOfTeam"] == 1
    assert summary["positionGroupDistribution"] == {"DB": 1, "LB": 1}
    assert summary["rosterYearDistribution"] == {"Roster year 3": 1, "Roster year 4": 1}
