# Contributing

WARDBREAKER is defensive guardrail-robustness research. Contributions that add
targets, attack families, or better oracles are welcome — as long as they keep to
the project's rules.

## Ground rules

- **Local, open-weight targets only.** No code that attacks hosted or third-party
  APIs.
- **Benign-proxy seeds only.** No turnkey dangerous payloads.
- **Keep the core zero-dependency** (standard library). Heavy dependencies such as
  `transformers` stay behind an optional extra and a lazy import.

## Development

```bash
pip install -e ".[dev]"
ruff check .
pytest -q
python -m wardbreaker --selftest
```

Add a test for any new behaviour, and run the linter and self-check before opening a
pull request. CI runs all three on every push, across Python 3.9–3.12.

## Adding an attack family

Add a pure `str -> str` function to `wardbreaker/mutators.py` and register it in the
`MUTATORS` dict. The runner and report pick it up automatically.

## Adding a target

Implement `classify(text) -> Verdict`, declare a `kind` (`"content"` or
`"injection"`), and wire it into `get_target`. Keep it local-only.
