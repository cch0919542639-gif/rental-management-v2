from pathlib import Path
import subprocess
import sys


def test_404_page_renders_html(client):
    response = client.get("/missing-route")
    assert response.status_code == 404
    text = response.get_data(as_text=True)
    assert "404｜找不到頁面" in text
    assert "儀表板" in text


def test_500_page_renders_html(app, client):
    app.config["PROPAGATE_EXCEPTIONS"] = False

    def boom():
        raise RuntimeError("boom")

    app.add_url_rule("/_test/boom", "test_boom", boom)

    response = client.get("/_test/boom")
    assert response.status_code == 500
    text = response.get_data(as_text=True)
    assert "500｜伺服器錯誤" in text
    assert "回儀表板" in text


def test_migration_index_script_lists_available_scripts():
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, str(root / "scripts" / "migration" / "migration_index.py")],
        capture_output=True,
        text=True,
        cwd=root,
        check=True,
    )
    assert "Migration Script Index" in result.stdout
    assert "maintenance_legacy_scan.py" in result.stdout
    assert "migration_index.py" in result.stdout
