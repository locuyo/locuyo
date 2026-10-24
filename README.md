# locuyo

Practice answering interview questions out loud and get honest, measurable feedback on how you deliver them.

**Name:** *locu-* (from *locution*, Latin *loqui*, "to speak") + *yo* (Spanish for "I"). My speech, practiced.

## Status

MVP in progress. Built first as a personal tool for practicing technical interviews in English as a non-native speaker, second as a portfolio project.

## What the MVP does

Audio file in, metrics out. Runs fully offline on CPU, no cloud account needed.

- Transcribes locally with `faster-whisper`
- Words per minute
- Filler words (per 100 words)
- Long pauses (gaps of 0.7s or more) and the longest one
- Appends every session to `sessions/` as JSON so you can track trends

Not in the MVP, on purpose: facial analysis (scientifically weak, and regulated under the EU AI Act), real-time coaching, any UI.

## Usage

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m locuyo.analyze answer.m4a --question "Tell me about your transition from music to cloud security"
pytest
```

Use `--model tiny|base|small|medium` to trade speed against accuracy. Whisper tends to delete "um" and "uh", so the transcriber is prompted to keep them; filler counts are an approximation, not ground truth.

## Roadmap

1. LLM feedback on answer structure (STAR), clarity and technical accuracy
2. Question bank and session picker (`questions.md` is the seed)
3. Progress dashboard over `sessions/`
4. Infrastructure as code: Terraform, GitHub Actions with OIDC (no static AWS keys), containerized worker
5. Observability

## Infrastructure

`terraform/oidc/` sets up GitHub Actions to AWS federation:

- A plan role (read-only) assumable from pull requests and `main`
- A deploy role assumable only from the `production` GitHub environment (put required reviewers on it)
- Trust is pinned to this exact repository, never `repo:locuyo/*`

## Privacy

Recordings and transcripts are personal data. They stay local and are git-ignored. Any cloud storage added later must use encryption at rest and a retention policy.

