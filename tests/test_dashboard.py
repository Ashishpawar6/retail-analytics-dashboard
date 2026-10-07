from pathlib import Path

from streamlit.testing.v1 import AppTest

from analytics.pipeline import run
from tests.conftest import make_raw

APP = Path(__file__).resolve().parent.parent / "app" / "dashboard.py"


def test_dashboard_renders_without_errors(tmp_path, monkeypatch):
    db = tmp_path / "retail.db"
    run(make_raw(), db)
    monkeypatch.setenv("RETAIL_DB", str(db))

    app = AppTest.from_file(str(APP), default_timeout=60).run()

    assert not app.exception
    assert [m.label for m in app.metric][:5] == ["Gross revenue", "Returns", "Orders", "Customers (with ID)", "Avg order value"]
    assert app.metric[0].value == "£95"
    assert len(app.tabs) == 5


def test_dashboard_shows_a_helpful_error_when_the_database_is_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("RETAIL_DB", str(tmp_path / "missing.db"))
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    assert "analytics.pipeline" in app.error[0].value
