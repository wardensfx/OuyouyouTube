from app.config import settings
from app.downloader import _output_path, _status_key


def test_output_path_uses_video_id():
    assert _output_path("dQw4w9WgXcQ") == settings.cache_dir / "dQw4w9WgXcQ.mp4"


def test_status_key_format():
    assert _status_key("dQw4w9WgXcQ") == "video_status:dQw4w9WgXcQ"
