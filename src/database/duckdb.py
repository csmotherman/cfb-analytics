"""DuckDB storage operations with automatic schema evolution."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import duckdb
import pandas as pd

from src.database.schema import (
    TABLE_ORDER,
    TABLE_PRIMARY_KEYS,
    quoted_identifier,
)
from src.utils.config import DUCKDB_PATH


def connect(
    database_path: str | Path = DUCKDB_PATH,
    read_only: bool = False,
) -> duckdb.DuckDBPyConnection:
    """Open a DuckDB connection."""

    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    return duckdb.connect(
        str(path),
        read_only=read_only,
    )


@contextmanager
def database_connection(
    database_path: str | Path = DUCKDB_PATH,
    read_only: bool = False,
) -> Iterator[duckdb.DuckDBPyConnection]:
    """Context-managed DuckDB connection."""

    connection = connect(database_path, read_only)

    try:
        yield connection
    finally:
        connection.close()


def table_exists(
    connection: duckdb.DuckDBPyConnection,
    table_name: str,
) -> bool:
    """Return whether a table exists."""

    result = connection.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'main'
          AND table_name = ?
        """,
        [table_name],
    ).fetchone()

    return bool(result and result[0])


def get_table_columns(
    connection: duckdb.DuckDBPyConnection,
    table_name: str,
) -> dict[str, str]:
    """Return table columns mapped to DuckDB type names."""

    if not table_exists(connection, table_name):
        return {}

    rows = connection.execute(
        f"DESCRIBE {quoted_identifier(table_name)}"
    ).fetchall()

    return {
        row[0]: row[1]
        for row in rows
    }


def _duckdb_type_for_series(
    series: pd.Series,
) -> str:
    """Map a pandas Series to a practical DuckDB column type."""

    if pd.api.types.is_bool_dtype(series):
        return "BOOLEAN"

    if pd.api.types.is_integer_dtype(series):
        return "BIGINT"

    if pd.api.types.is_float_dtype(series):
        return "DOUBLE"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "TIMESTAMP"

    return "VARCHAR"


def evolve_table_schema(
    connection: duckdb.DuckDBPyConnection,
    table_name: str,
    dataframe: pd.DataFrame,
) -> None:
    """Add newly discovered DataFrame columns to an existing table."""

    existing = get_table_columns(connection, table_name)

    for column in dataframe.columns:
        if column in existing:
            continue

        column_type = _duckdb_type_for_series(
            dataframe[column]
        )

        connection.execute(
            f"""
            ALTER TABLE {quoted_identifier(table_name)}
            ADD COLUMN {quoted_identifier(column)} {column_type}
            """
        )


def create_table_from_dataframe(
    connection: duckdb.DuckDBPyConnection,
    table_name: str,
    dataframe: pd.DataFrame,
) -> None:
    """Create an empty DuckDB table based on DataFrame columns."""

    if dataframe.empty and len(dataframe.columns) == 0:
        return

    temp_name = f"_source_{table_name}"

    connection.register(temp_name, dataframe)

    try:
        connection.execute(
            f"""
            CREATE TABLE {quoted_identifier(table_name)} AS
            SELECT *
            FROM {quoted_identifier(temp_name)}
            WHERE 1 = 0
            """
        )
    finally:
        connection.unregister(temp_name)


def _align_dataframe_to_table(
    connection: duckdb.DuckDBPyConnection,
    table_name: str,
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Add missing table columns and order DataFrame columns."""

    table_columns = list(
        get_table_columns(connection, table_name)
    )

    aligned = dataframe.copy()

    for column in table_columns:
        if column not in aligned.columns:
            aligned[column] = None

    return aligned.loc[:, table_columns]


def delete_matching_rows(
    connection: duckdb.DuckDBPyConnection,
    table_name: str,
    dataframe: pd.DataFrame,
) -> None:
    """
    Delete rows matching configured key columns.

    This makes ingestion idempotent: ingesting the same game twice does
    not duplicate rows.
    """

    keys = TABLE_PRIMARY_KEYS.get(table_name, ())

    if dataframe.empty or not keys:
        return

    if not all(key in dataframe.columns for key in keys):
        return

    key_frame = (
        dataframe.loc[:, list(keys)]
        .dropna()
        .drop_duplicates()
    )

    if key_frame.empty:
        return

    temp_keys = f"_keys_{table_name}"
    connection.register(temp_keys, key_frame)

    try:
        conditions = " AND ".join(
            f"target.{quoted_identifier(key)} "
            f"= source.{quoted_identifier(key)}"
            for key in keys
        )

        connection.execute(
            f"""
            DELETE FROM {quoted_identifier(table_name)} AS target
            USING {quoted_identifier(temp_keys)} AS source
            WHERE {conditions}
            """
        )
    finally:
        connection.unregister(temp_keys)


def insert_dataframe(
    connection: duckdb.DuckDBPyConnection,
    table_name: str,
    dataframe: pd.DataFrame,
    replace_matching: bool = True,
) -> int:
    """
    Insert one DataFrame into DuckDB.

    New columns are automatically added to existing tables.
    """

    if dataframe.empty:
        return 0

    if not table_exists(connection, table_name):
        create_table_from_dataframe(
            connection,
            table_name,
            dataframe,
        )
    else:
        evolve_table_schema(
            connection,
            table_name,
            dataframe,
        )

    if replace_matching:
        delete_matching_rows(
            connection,
            table_name,
            dataframe,
        )

    aligned = _align_dataframe_to_table(
        connection,
        table_name,
        dataframe,
    )

    temp_name = f"_insert_{table_name}"
    connection.register(temp_name, aligned)

    try:
        connection.execute(
            f"""
            INSERT INTO {quoted_identifier(table_name)}
            SELECT *
            FROM {quoted_identifier(temp_name)}
            """
        )
    finally:
        connection.unregister(temp_name)

    return len(aligned)


def insert_tables(
    tables: dict[str, pd.DataFrame],
    database_path: str | Path = DUCKDB_PATH,
) -> dict[str, int]:
    """Insert all normalized tables within one transaction."""

    counts: dict[str, int] = {}

    with database_connection(database_path) as connection:
        connection.execute("BEGIN TRANSACTION")

        try:
            for table_name in TABLE_ORDER:
                dataframe = tables.get(
                    table_name,
                    pd.DataFrame(),
                )

                counts[table_name] = insert_dataframe(
                    connection,
                    table_name,
                    dataframe,
                    replace_matching=True,
                )

            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise

    return counts


def query(
    sql: str,
    parameters: list | tuple | None = None,
    database_path: str | Path = DUCKDB_PATH,
) -> pd.DataFrame:
    """Run SQL and return a pandas DataFrame."""

    with database_connection(
        database_path,
        read_only=True,
    ) as connection:
        return connection.execute(
            sql,
            parameters or [],
        ).df()


def table_counts(
    database_path: str | Path = DUCKDB_PATH,
) -> pd.DataFrame:
    """Return row counts for each existing baseline table."""

    rows: list[dict] = []

    with database_connection(
        database_path,
        read_only=True,
    ) as connection:
        for table_name in TABLE_ORDER:
            if not table_exists(connection, table_name):
                rows.append(
                    {
                        "table_name": table_name,
                        "row_count": 0,
                        "exists": False,
                    }
                )
                continue

            row_count = connection.execute(
                f"""
                SELECT COUNT(*)
                FROM {quoted_identifier(table_name)}
                """
            ).fetchone()[0]

            rows.append(
                {
                    "table_name": table_name,
                    "row_count": row_count,
                    "exists": True,
                }
            )

    return pd.DataFrame(rows)