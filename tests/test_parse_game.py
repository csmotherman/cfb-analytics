"""Basic parser regression tests."""

import json
from pathlib import Path

from src.parser.parse_game import parse_game
from src.parser.validate import validate_game_tables


FIXTURE = (
    Path(__file__).parent
    / "data"
    / "michigan_2025_week1.json"
)


def test_parse_game() -> None:
    with FIXTURE.open("r", encoding="utf-8") as file:
        game_json = json.load(file)

    tables = parse_game(game_json)

    validate_game_tables(tables)

    assert len(tables["games"]) == 1
    assert not tables["drives"].empty
    assert not tables["plays"].empty
    assert tables["plays"]["play_id"].is_unique
    assert tables["play_events"]["event_id"].is_unique