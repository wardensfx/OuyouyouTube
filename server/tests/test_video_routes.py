from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_video_status_requires_auth():
    resp = client.get("/api/video/dQw4w9WgXcQ/status")
    assert resp.status_code == 401


def test_playlists_requires_auth():
    resp = client.get("/api/playlists")
    assert resp.status_code == 401
