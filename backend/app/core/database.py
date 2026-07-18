"""SQLAlchemy session management for the local compliance backend."""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.config import get_settings
from backend.app.models import Base


def build_sqlite_url(database_path: str | Path) -> str:
    """Build a SQLite URL from a file path or the in-memory sentinel."""
    if str(database_path) == ":memory:":
        return "sqlite://"
    resolved_path = Path(database_path).expanduser().resolve()
    return f"sqlite:///{resolved_path.as_posix()}"


def ensure_sqlite_parent(database_path: str | Path) -> None:
    """Create the parent directory for a file-backed SQLite database."""
    if str(database_path) != ":memory:":
        Path(database_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)


def create_sqlite_engine(database_path: str | Path) -> Engine:
    """Create the only supported database engine with safe SQLite pragmas."""
    is_memory_database = str(database_path) == ":memory:"
    ensure_sqlite_parent(database_path)
    engine_options: dict[str, object] = {"connect_args": {"check_same_thread": False}}
    if is_memory_database:
        engine_options["poolclass"] = StaticPool
    database_engine = create_engine(build_sqlite_url(database_path), **engine_options)

    @event.listens_for(database_engine, "connect")
    def configure_sqlite(dbapi_connection: object, _: object) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=5000")
        if not is_memory_database:
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

    return database_engine


engine = create_sqlite_engine(get_settings().database_path)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def load_member_two_models() -> None:
    """Import model modules so SQLAlchemy registers every Member 2 table."""
    from backend.app.models import (  # noqa: F401
        audit_log,
        case,
        compliance_report,
        document,
        evidence,
        review,
        scenario,
    )


def initialize_database() -> None:
    """Create local-development tables; production should use migrations."""
    load_member_two_models()
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Provide one transactional SQLAlchemy session per request."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
