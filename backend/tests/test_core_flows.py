from __future__ import annotations

import io
import json
import os
import shutil
import tempfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

TEST_DATA_DIR = Path(tempfile.mkdtemp(prefix="qiuzhao-tests-"))
os.environ["QIUZHAO_DATA_DIR"] = str(TEST_DATA_DIR)

from fastapi.testclient import TestClient  # noqa: E402

from app.core.errors import AppError  # noqa: E402
from app.database import engine  # noqa: E402
from app.main import app  # noqa: E402
from app.services.storage import abs_of  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client
    engine.dispose()
    shutil.rmtree(TEST_DATA_DIR, ignore_errors=True)


def _create_application(client: TestClient, company: str, status: str, days_ago: int = 0):
    response = client.post(
        "/api/applications",
        json={
            "company": company,
            "position": "后端开发工程师",
            "status": status,
            "apply_time": (datetime.now() - timedelta(days=days_ago)).isoformat(),
            "close_reason": "employer_rejected" if status == "ended" else None,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]


def test_local_origin_guard(client: TestClient):
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/health", headers={"Origin": "https://evil.example"}).status_code == 403
    assert client.get(
        "/api/health", headers={"Origin": "http://127.0.0.1:5173"}
    ).status_code == 200


def test_application_search_facets_dates_and_close_reason(client: TestClient):
    pending = _create_application(client, "星河科技", "pending")
    _create_application(client, "春风网络", "applied", days_ago=3)
    interview = _create_application(client, "远山数据", "interview", days_ago=10)
    _create_application(client, "青禾智能", "ended", days_ago=40)
    _create_application(client, "云帆系统", "offered", days_ago=2)

    searched = client.get("/api/applications", params={"keyword": "星河"}).json()["data"]
    assert [item["id"] for item in searched["items"]] == [pending["id"]]

    applied = client.get("/api/applications", params={"status_group": "applied"}).json()["data"]
    assert applied["total"] == 1
    assert applied["facets"]["all"] == 5
    assert applied["facets"]["closed"] == 1

    recent = client.get("/api/applications", params={"apply_time_range": "last_7_days"}).json()["data"]
    assert recent["total"] == 3
    older = client.get("/api/applications", params={"apply_time_range": "older"}).json()["data"]
    assert older["total"] == 1

    changed = client.put(
        f"/api/applications/{interview['id']}/status",
        json={"to_status": "ended", "close_reason": "employer_rejected", "note": "流程结束"},
    )
    assert changed.status_code == 200, changed.text
    assert changed.json()["data"]["close_reason"] == "employer_rejected"
    detail = client.get(f"/api/applications/{interview['id']}").json()["data"]
    assert detail["timeline"][0]["close_reason"] == "employer_rejected"


def test_complete_backup_round_trip(client: TestClient):
    uploaded = client.post(
        "/api/assets/upload",
        data={"category": "assets", "title": "测试图片"},
        files={"file": ("test.png", b"\x89PNG\r\n\x1a\n" + b"test-data", "image/png")},
    )
    assert uploaded.status_code == 200, uploaded.text

    exported = client.get("/api/backup/export")
    assert exported.status_code == 200, exported.text
    archive_bytes = exported.content
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        payload = json.loads(archive.read("backup.json"))
        assert payload["format"] == "qiuzhao-room-backup"
        assert len(payload["files"]) == 1
        assert archive.testzip() is None

    later = _create_application(client, "备份后新增公司", "pending")
    assert client.get(f"/api/applications/{later['id']}").status_code == 200

    restored = client.post(
        "/api/backup/import",
        files={"file": ("backup.zip", archive_bytes, "application/zip")},
    )
    assert restored.status_code == 200, restored.text
    assert restored.json()["data"]["snapshot"].startswith("auto-before-restore-")
    companies = {
        item["company"]
        for item in client.get("/api/applications", params={"page_size": 100}).json()["data"]["items"]
    }
    assert "备份后新增公司" not in companies
    assert list((TEST_DATA_DIR / "files" / "assets").glob("*.png"))


def test_storage_path_cannot_escape_files_directory():
    with pytest.raises(AppError):
        abs_of("../outside.txt")
