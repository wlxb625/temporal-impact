# Contributing to Temporal Impact

Thank you for contributing. Keep each change scoped to one documented development goal.

## Development setup

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
mypy src
```

## Contribution rules

- Preserve the host application as the source of truth.
- Do not add automatic host-system writes.
- Add tests for new core logic and keep tests isolated.
- Do not add unapproved infrastructure or dependencies.
- Keep public interfaces typed and documented.

See [AGENTS.md](AGENTS.md) for the full project rules.

