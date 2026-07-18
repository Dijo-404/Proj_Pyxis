"""SQLite-only engine configuration tests."""

from pathlib import Path

from sqlalchemy import text

from backend.app.core.database import build_sqlite_url, create_sqlite_engine


def test_builds_file_backed_sqlite_url(tmp_path: Path) -> None:
    database_path = tmp_path / "nested" / "pyxis.db"

    url = build_sqlite_url(database_path)

    assert url.startswith("sqlite:///")
    assert url.endswith("/nested/pyxis.db")


def test_enables_sqlite_safety_pragmas(tmp_path: Path) -> None:
    database_path = tmp_path / "pyxis.db"
    engine = create_sqlite_engine(database_path)
    try:
        with engine.connect() as connection:
            assert connection.scalar(text("PRAGMA foreign_keys")) == 1
            assert connection.scalar(text("PRAGMA busy_timeout")) == 5000
            assert connection.scalar(text("PRAGMA journal_mode")) == "wal"
            assert connection.scalar(text("PRAGMA synchronous")) == 1
    finally:
        engine.dispose()

    assert database_path.is_file()
