import os
import tempfile
import pytest
from fastapi.testclient import TestClient

# Use a temp sqlite file so schema persists across connections.
tmp = tempfile.NamedTemporaryFile(prefix="airdrop_test_", suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{tmp.name}"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"  # not used by unit tests
os.environ["DEBUG"] = "true"

from app.main import create_app  # noqa: E402
from app.db.session import init_db  # noqa: E402

@pytest.fixture()
def client():
    app = create_app()
    # ensure a fresh engine for each test
    init_db.close()
    init_db.configure(os.environ["DATABASE_URL"])
    init_db.ensure_bootstrap()
    with TestClient(app) as c:
        yield c
