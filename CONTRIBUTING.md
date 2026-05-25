# Contributing

Thanks for your interest! Here's how to contribute:

## Reporting Issues

- Check existing issues first
- Include the full error message and steps to reproduce
- Mention your Python version and OS

## Pull Requests

1. Fork the repo and create a feature branch
2. Write or update tests in `tests/`
3. Run `python -m pytest tests/ -v` to verify
4. Run `flake8 . --count --select=E9,F63,F7,F82 --show-source`
5. Open a PR with a clear title and description

## Code Style

- Keep functions small and focused (single responsibility)
- Docstrings for all public methods (Google style)
- Type hints everywhere
- Turkish/English/Dutch support strings go in the agent's `_build_system_prompt()`

## Adding a New Language

1. Add detection logic to `_detect_language()` in `agent.py`
2. Add a system prompt in `_build_system_prompt()`
3. Add template fallbacks in `_fallback_reply()`
4. Add keyword mappings in `categorizer.py`
5. Add KB documents in `knowledge_base.py`

## Running Tests

```bash
pip install pytest flake8
python -m pytest tests/ -v
flake8 . --count --select=E9,F63,F7,F82 --show-source
```
