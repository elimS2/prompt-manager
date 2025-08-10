import os
import sys
import argparse
from pathlib import Path
from sqlalchemy import text


# Ensure project root on sys.path for `import app`
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app  # noqa: E402
from app.models import db  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Introspect active application database")
    parser.add_argument("--table", dest="table", help="Table name to verify existence", default=None)
    args = parser.parse_args()

    app = create_app('development')
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    print(f"DB URI: {db_uri}")
    if isinstance(db_uri, str) and db_uri.startswith('sqlite:///'):
        # derive file path after sqlite:///
        path = db_uri.replace('sqlite:///', '', 1)
        print(f"SQLite file absolute path: {os.path.abspath(path)}")

    with app.app_context():
        conn = db.engine.connect()
        tables = [row[0] for row in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))]
        print(f"Tables: {tables}")
        # Show alembic version
        if 'alembic_version' in tables:
            version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
            print(f"Alembic version: {version}")

        if args.table:
            exists = args.table in tables
            print(f"Has table '{args.table}': {exists}")
            if exists:
                try:
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {args.table}")).scalar()
                    print(f"{args.table} row count: {count}")
                except Exception as exc:
                    print(f"Could not count rows for '{args.table}': {exc}")


if __name__ == '__main__':
    main()


