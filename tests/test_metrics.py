from locuyo.analyze import compute_metrics


def w(word, start, end):
    return {"word": word, "start": start, "end": end}


def test_wpm_and_duration():
    # 6 words spoken over 3 seconds -> 120 WPM
    words = [w(f"w{i}", i * 0.5, i * 0.5 + 0.4) for i in range(6)]
    m = compute_metrics(words)
    assert m["word_count"] == 6
    assert m["duration_s"] == 2.9
    assert round(m["wpm"]) == 124


def test_fillers_single_and_multi():
    words = [
        w("So,", 0.0, 0.2),
        w("um", 0.3, 0.5),
        w("you", 0.6, 0.8),
        w("know,", 0.8, 1.0),
        w("I", 1.1, 1.2),
        w("deployed", 1.2, 1.6),
        w("it.", 1.6, 1.9),
    ]
    m = compute_metrics(words)
    # "so", "um" (single) + "you know" (multi)
    assert m["filler_count"] == 3


def test_long_pause_detected():
    words = [w("hello", 0.0, 0.4), w("world", 2.0, 2.4)]
    m = compute_metrics(words)
    assert m["long_pauses"] == 1
    assert m["longest_pause_s"] == 1.6


def test_empty_input():
    assert "error" in compute_metrics([])

