"""locuyo MVP: audio file -> transcript -> delivery metrics.

Usage:
    python -m locuyo.analyze answer.m4a --question "Tell me about your transition" 

Runs fully offline (faster-whisper on CPU). Each run appends a JSON record to
sessions/ so you can track trends over time.
"""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

# Single-word fillers are approximate ("like"/"so" are sometimes legitimate).
SINGLE_FILLERS = {"um", "uh", "uhm", "er", "erm", "hmm", "like", "basically",
                  "actually", "literally", "so"}
MULTI_FILLERS = ["you know", "i mean", "sort of", "kind of"]

# Whisper tends to delete disfluencies. A prompt containing them nudges it to keep them.
PROMPT = "Umm, let me think, like, hmm... Okay, so, you know, here's what I mean."

PAUSE_THRESHOLD_S = 0.7  # gap between words counted as a pause


def transcribe(path: str, model_size: str = "small"):
    from faster_whisper import WhisperModel  # lazy: metrics are testable without it

    model =WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(
        path, language="en", word_timestamps=True, initial_prompt=PROMPT
    )
    words = []
    for seg in segments:
        for w in seg.words or []:
            words.append({"word": w.word.strip(), "start": w.start, "end": w.end})
    return words


def compute_metrics(words):
    if not words:
        return {"error": "no speech detected"}

    text = " ".join(w["word"] for w in words)
    tokens = [re.sub(r"[^\w']", "", w["word"].lower()) for w in words]
    tokens = [t for t in tokens if t]

    duration_s = words[-1]["end"] - words[0]["start"]
    wpm = len(tokens) / (duration_s / 60) if duration_s > 0 else 0.0

    single = sum(1 for t in tokens if t in SINGLE_FILLERS)
    lowered = " ".join(tokens)
    multi = sum(lowered.count(f) for f in MULTI_FILLERS)

    pauses = [
        round(b["start"] - a["end"], 2)
        for a, b in zip(words, words[1:])
        if b["start"] - a["end"] >= PAUSE_THRESHOLD_S
    ]

    return {
        "transcript": text,
        "word_count": len(tokens),
        "duration_s": round(duration_s, 1),
        "wpm": round(wpm, 1),
        "filler_count": single + multi,
        "fillers_per_100_words": round(100 * (single + multi) / len(tokens), 1),
        "long_pauses": len(pauses),
        "longest_pause_s": max(pauses) if pauses else 0.0,
    }


def save_session(metrics: dict, audio: str, question: str, out_dir: Path):
    out_dir.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    record = {"timestamp": ts, "audio": audio, "question": question, **metrics}
    (out_dir / f"{ts}.json").write_text(json.dumps(record, indent=2))
    return out_dir / f"{ts}.json"


def main():
    p = argparse.ArgumentParser(description="Analyze a spoken interview answer.")
    p.add_argument("audio")
    p.add_argument("--question", default="")
    p.add_argument("--model", default="small", help="tiny/base/small/medium")
    p.add_argument("--sessions-dir", default="sessions")
    args = p.parse_args()

    metrics = compute_metrics(transcribe(args.audio, args.model))
    for k, v in metrics.items():
        if k != "transcript":
            print(f"{k:>24}: {v}")
    print("\nTranscript:\n" + metrics.get("transcript", ""))
    if "error" not in metrics:
        print("\nSaved:", save_session(metrics, args.audio, args.question, Path(args.sessions_dir)))


if __name__ == "__main__":
    main()

