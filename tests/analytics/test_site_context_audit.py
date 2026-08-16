import pytest

from cfb_analytics.analytics.site_context_audit import extract_neutral_site, parse_bool


def test_parse_bool_accepts_common_cfbd_boolean_shapes():
    assert parse_bool(True) is True
    assert parse_bool(False) is False
    assert parse_bool(1) is True
    assert parse_bool(0) is False
    assert parse_bool("true") is True
    assert parse_bool("false") is False
    assert parse_bool(None) is None
    assert parse_bool("unknown") is None


def test_extract_neutral_site_prefers_parseable_known_field():
    field, value = extract_neutral_site({"neutralSite": True, "venue": "Somewhere"})
    assert field == "neutralSite"
    assert value is True


def test_extract_neutral_site_returns_missing_when_schema_absent():
    assert extract_neutral_site({"id": 1, "venue": "Somewhere"}) == (None, None)


def test_extract_neutral_site_fails_on_conflicting_aliases():
    with pytest.raises(ValueError, match="Conflicting neutral-site fields"):
        extract_neutral_site({"neutralSite": True, "neutral": False})
