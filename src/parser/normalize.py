"""Generic JSON normalization helpers."""

from __future__ import annotations

import copy
from typing import Any, Iterable

import pandas as pd


def normalize_object(
    obj: dict[str, Any],
    remove: Iterable[str] | None = None,
) -> dict[str, Any]:
    """
    Flatten one dictionary into scalar columns.

    Child collections listed in `remove` are excluded because they are
    extracted into separate relational tables.
    """

    if not isinstance(obj, dict):
        raise TypeError(
            f"normalize_object expected dict, received {type(obj).__name__}"
        )

    clean = copy.deepcopy(obj)

    for key in remove or ():
        clean.pop(key, None)

    if not clean:
        return {}

    normalized = pd.json_normalize(clean, sep="_")

    if normalized.empty:
        return {}

    return normalized.iloc[0].to_dict()


def dataframe_from_rows(
    rows: list[dict[str, Any]],
) -> pd.DataFrame:
    """Create a DataFrame while safely handling an empty row list."""

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


def scalar_columns_only(df: pd.DataFrame) -> list[str]:
    """Return columns containing no dictionaries or lists."""

    nested_columns: list[str] = []

    for column in df.columns:
        contains_nested = df[column].apply(
            lambda value: isinstance(value, (dict, list))
        ).any()

        if contains_nested:
            nested_columns.append(column)

    return nested_columns