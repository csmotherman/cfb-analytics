"""Versioned, conservative normalization of CFBD playText.

V1 targets dominant rushing/passing formats and common penalty/result grammar.
It never mutates the source record and deliberately returns AMBIGUOUS when
multiple yardage or destination phrases make extraction unsafe.
"""
from __future__ import annotations

import re
from typing import Any

from cfb_analytics.canonical.play_text_forensics import (
    _yardage_profile,
    _destination_profile,
    _penalty_profile,
    _semantic_text_label,
)

TEXT_PARSE_VERSION = "v1"

FIRST_DOWN_RE = re.compile(r"\b(?:1st|first) down\b", re.I)
TOUCHDOWN_RE = re.compile(r"\b(?:touchdown|for a td|for td)\b", re.I)
NO_PLAY_RE = re.compile(r"\bno play\b|\bnullified\b", re.I)
PENALTY_YARDS_RE = re.compile(r"\bpenalty\b.*?(?P<yards>\d+)\s+(?:yd|yds|yard|yards)\b", re.I)
PENALTY_TYPE_RE = re.compile(
    r"\b(?:penalty[, ]+)?(?P<type>offensive holding|defensive holding|holding|offside|offsides|false start|"
    r"pass interference|defensive pass interference|offensive pass interference|roughing the passer|"
    r"roughing passer|personal foul|unsportsmanlike conduct|facemask|face mask|delay of game|encroachment|"
    r"illegal formation|illegal motion|illegal shift|illegal block|illegal substitution|targeting)\b",
    re.I,
)


def _clean(text: Any) -> str:
    return " ".join(str(text or "").split())


def _penalty_status(profile: dict[str, Any]) -> str | None:
    if not profile["has_penalty"]:
        return None
    statuses=set(profile["statuses"])
    # More consequential statuses take precedence over generic enforcement words.
    for status in ("NO_PLAY","OFFSETTING","DECLINED","ACCEPTED","HALF_DISTANCE"):
        if status in statuses:
            return status
    return "UNSPECIFIED"


def _safe_yards(text: str) -> tuple[int | None, bool, int]:
    profile=_yardage_profile(text)
    values=profile["values"]
    if len(values)==1:
        return values[0], False, 1
    if not values:
        return None, False, 0
    # Repeated identical textual yardage is still semantically ambiguous: it may
    # describe both play result and enforcement, so don't silently choose it.
    return None, True, len(values)


def _safe_destination(text: str) -> tuple[str | None, int | None, bool, int]:
    dests=_destination_profile(text)
    if len(dests)==1:
        return dests[0]["team"],dests[0]["yard"],False,1
    if not dests:
        return None,None,False,0
    return None,None,True,len(dests)


def _penalty_details(text: str, profile: dict[str, Any]) -> dict[str, Any]:
    if not profile["has_penalty"]:
        return {"textPenalty":False,"textPenaltyStatus":None,"textPenaltyType":None,"textPenaltyYards":None}
    type_match=PENALTY_TYPE_RE.search(text)
    yard_match=PENALTY_YARDS_RE.search(text)
    return {
        "textPenalty":True,
        "textPenaltyStatus":_penalty_status(profile),
        "textPenaltyType":type_match.group("type").upper().replace(" ","_") if type_match else None,
        "textPenaltyYards":int(yard_match.group("yards")) if yard_match else None,
    }


def _normalized_tokens(result: dict[str, Any]) -> list[str]:
    tokens=[]
    if result["textPlayType"]: tokens.append(result["textPlayType"])
    if result["textYardsGained"] is not None:
        y=result["textYardsGained"]
        tokens.append("NO_GAIN" if y==0 else f"GAIN {y}" if y>0 else f"LOSS {abs(y)}")
    if result["textDestinationTeam"] is not None:
        tokens.append(f"TO {result['textDestinationTeam']} {result['textDestinationYardLine']}")
    if result["textFirstDown"]: tokens.append("FIRST_DOWN")
    if result["textTouchdown"]: tokens.append("TOUCHDOWN")
    if result["textPenalty"]:
        tokens.append("PENALTY")
        if result["textPenaltyType"]: tokens.append(result["textPenaltyType"])
        if result["textPenaltyYards"] is not None: tokens.append(f"PENALTY_YARDS {result['textPenaltyYards']}")
        if result["textPenaltyStatus"]: tokens.append(result["textPenaltyStatus"])
    if result["textNoPlay"] and result.get("textPenaltyStatus")!="NO_PLAY": tokens.append("NO_PLAY")
    return tokens


def normalize_play_text(play: dict[str, Any]) -> dict[str, Any]:
    text=_clean(play.get("playText"))
    semantic=_semantic_text_label(text)
    yards,yards_ambiguous,yards_count=_safe_yards(text)
    team,yardline,dest_ambiguous,dest_count=_safe_destination(text)
    pp=_penalty_profile(text)
    penalty=_penalty_details(text,pp)
    ambiguous_reasons=[]
    if yards_ambiguous: ambiguous_reasons.append("MULTIPLE_YARDAGE_PHRASES")
    if dest_ambiguous: ambiguous_reasons.append("MULTIPLE_DESTINATIONS")
    if pp["penalty_count"]>1: ambiguous_reasons.append("MULTIPLE_PENALTY_TOKENS")
    if not text: ambiguous_reasons.append("MISSING_PLAY_TEXT")

    result={
        "textParseVersion":TEXT_PARSE_VERSION,
        "sourcePlayText":play.get("playText"),
        "textPlayType":semantic,
        "textYardsGained":yards,
        "textDestinationTeam":team,
        "textDestinationYardLine":yardline,
        "textFirstDown":bool(FIRST_DOWN_RE.search(text)),
        "textTouchdown":bool(TOUCHDOWN_RE.search(text)),
        "textNoPlay":bool(NO_PLAY_RE.search(text)),
        "textYardagePhraseCount":yards_count,
        "textDestinationCount":dest_count,
        "textPenaltyTokenCount":pp["penalty_count"],
        **penalty,
        "textAmbiguous":bool(ambiguous_reasons),
        "textAmbiguityReasons":ambiguous_reasons,
    }
    if not text:
        confidence="NONE"
    elif ambiguous_reasons:
        confidence="LOW"
    elif semantic and (yards_count==1 or dest_count==1 or result["textTouchdown"] or result["textFirstDown"]):
        confidence="HIGH"
    elif semantic:
        confidence="MEDIUM"
    else:
        confidence="LOW"
    result["textParseConfidence"]=confidence
    result["normalizedPlayText"]=" | ".join(_normalized_tokens(result)) or "UNPARSED"
    return result
