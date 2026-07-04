from app.progress import _is_watched


def test_not_watched_without_duration():
    assert _is_watched(position=100, duration=0) is False


def test_short_video_needs_close_to_full_ratio():
    # 40s video: tail = min(40 * 0.1, 60) = 4s -> threshold at 36s
    assert _is_watched(position=35, duration=40) is False
    assert _is_watched(position=36, duration=40) is True


def test_long_video_uses_capped_tail_seconds():
    # 3h video: tail = min(10800 * 0.1, 60) = 60s -> threshold at 10740s
    assert _is_watched(position=10739, duration=10800) is False
    assert _is_watched(position=10740, duration=10800) is True


def test_ratio_and_cap_crossover_at_ten_minutes():
    # At duration=600s, ratio-based tail (60s) equals the cap (60s)
    assert _is_watched(position=539, duration=600) is False
    assert _is_watched(position=540, duration=600) is True
