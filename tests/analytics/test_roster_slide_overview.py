from cfb_analytics.analytics.roster_slide_overview import (
    build_slide_overview,
    classify_roster_sources,
    parse_official_roster_html,
)


def _row(name: str, position: str, cls: str, previous_school: str | None = None):
    return {
        "number": "1",
        "name": name,
        "position": position,
        "positionGroup": "QB" if position == "QB" else "DB" if position in {"CB", "S"} else "WR",
        "side": "Offense" if position in {"QB", "WR"} else "Defense",
        "classRaw": cls,
        "classLabel": {
            "Fr.": "Freshman",
            "So.": "Sophomore",
            "Jr.": "Junior",
            "Sr.": "Senior",
            "R-Sr.": "Redshirt Senior",
            "Gr.": "Graduate",
        }.get(cls, cls),
        "eligibilityBucket": "Senior / Graduate" if cls in {"Sr.", "R-Sr.", "Gr."} else "Freshman eligibility" if cls == "Fr." else "Sophomore eligibility" if cls == "So." else "Junior eligibility",
        "height": "6-1",
        "heightInches": 73.0,
        "weight": "200",
        "weightPounds": 200.0,
        "previousSchool": previous_school,
    }


def test_parse_official_roster_table_uses_previous_school_and_class():
    html = """
    <html><body>
      <table>
        <tr><th>#</th><th>Name</th><th>Pos.</th><th>Class</th><th>Ht.</th><th>Wt.</th><th>Hometown / High School</th><th>Previous School</th></tr>
        <tr><td>0</td><td>Transfer Player</td><td>QB</td><td>Gr.</td><td>6-2</td><td>215</td><td>Town / HS</td><td>Michigan</td></tr>
        <tr><td>1</td><td>Fresh Player</td><td>WR</td><td>Fr.</td><td>6-0</td><td>180</td><td>Town / HS</td><td></td></tr>
      </table>
    </body></html>
    """
    rows = parse_official_roster_html(html)
    assert len(rows) == 2
    assert rows[0]["name"] == "Transfer Player"
    assert rows[0]["previousSchool"] == "Michigan"
    assert rows[0]["classLabel"] == "Graduate"
    assert rows[1]["previousSchool"] is None
    assert rows[1]["classLabel"] == "Freshman"


def test_source_classification_precedence():
    current = [
        _row("Returner", "QB", "Jr.", "Old School"),
        _row("Rejoiner", "CB", "Sr.", "Other College"),
        _row("College New", "WR", "So.", "Power School"),
        _row("First Timer", "WR", "Fr.", None),
    ]
    previous = [_row("Returner", "QB", "So.")]
    older = [_row("Returner", "QB", "Fr."), _row("Rejoiner", "CB", "So.")]

    rows = classify_roster_sources(current, previous, older)
    by_name = {row["name"]: row["rosterSource"] for row in rows}

    assert by_name == {
        "Returner": "returning_2025",
        "Rejoiner": "rejoining_program",
        "College New": "college_newcomer",
        "First Timer": "first_time_college",
    }


def test_slide_overview_reconciles_and_uses_positive_ppa_retention():
    current = [
        _row("Returner", "QB", "Jr."),
        _row("College New", "WR", "So.", "Other School"),
        _row("First Timer", "WR", "Fr."),
        _row("Rejoiner", "CB", "Sr."),
    ]
    previous = [_row("Returner", "QB", "So.")]
    older = [_row("Rejoiner", "CB", "So.")]
    ppa_report = {
        "excludeGarbageTime": True,
        "returningPPAContributors": 1,
        "priorSeasonPPAContributors": 2,
        "overallPlayerAttributedPPA": {"returningPPA": 10.0},
        "topReturningProducers": [{"name": "Returner", "position": "QB", "totalPPA": 10.0}],
        "topLostProducers": [{"name": "Lost", "position": "QB", "totalPPA": -2.0}],
        "players": [
            {
                "name": "Returner",
                "position": "QB",
                "returning": True,
                "totalPPA": 10.0,
                "passingPPA": 8.0,
                "receivingAttributedPPA": None,
                "rushingPPA": 2.0,
            },
            {
                "name": "Lost",
                "position": "QB",
                "returning": False,
                "totalPPA": -2.0,
                "passingPPA": -3.0,
                "receivingAttributedPPA": None,
                "rushingPPA": 0.0,
            },
        ],
    }

    report = build_slide_overview(
        current,
        previous,
        older,
        ppa_report,
        team="Western Michigan",
        season=2026,
        roster_urls={"current": "a", "previous": "b", "older": "c"},
    )

    assert report["roster"]["currentPlayers"] == 4
    assert report["roster"]["sourceCounts"] == {
        "returning_2025": 1,
        "college_newcomer": 1,
        "first_time_college": 1,
        "rejoining_program": 1,
    }
    ppa = report["returningPPA"]["views"]["qbPassingPPA"]
    assert ppa["signedReturningShare"] == 8.0 / 5.0
    assert ppa["positiveReturningShare"] == 1.0
