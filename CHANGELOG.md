# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-20

Initial release.

### Added
- Fuzzing engine with a pluggable target interface and a `get_target` resolver that
  **refuses unknown/remote targets**. Adapters: `mock` (offline default), Ollama
  Llama Guard 3 (zero-dependency), HuggingFace Prompt Guard 2 (optional extra).
- 11 stdlib attack families: letter-space, zero-width, variation-selector, homoglyph,
  diacritic, bidi-override, full-width, base64, leetspeak, rot13, payload-split.
- **Killer-feature check** — a bypass counts only if the guard is fooled *and* a
  downstream model still acts on the payload (on-topic survival), filtering fake
  bypasses that flip the guard but garble the payload.
- Two seed kinds (content-policy vs injection) auto-selected per target's `kind`.
- Markdown report: per-family bypass rate, false-positive / over-blocking rate, and a
  two-sided finding that is honest about a 0% FPR.
- Offline `--selftest`, a pytest suite, ruff configuration, and GitHub Actions CI
  across Python 3.9–3.12.

[0.1.0]: https://github.com/jafeeri/wardbreaker/releases/tag/v0.1.0
