# PDCA Cycle 3: Release Readiness & Code Hygiene

**Date Started**: 2026-02-14
**Status**: ⏳ **PLANNED**
**Priority**: HIGH

---

## Executive Summary

Cycles 1 and 2 built a solid foundation (CI/CD, types, coverage) and added
significant functionality (serialization, context managers, 20+ examples).
Cycle 3 focuses on cleaning up the rough edges that accumulated during rapid
feature development, so the project can ship a stable, professional release.

This is a **code hygiene and release prep** cycle — no new features.

---

## Objectives

| #   | Objective                         | Why It Matters                                    |
| --- | --------------------------------- | ------------------------------------------------- |
| 1   | Extract exceptions to `errors.py` | Clean module boundaries, single responsibility    |
| 2   | Export all public exceptions      | Users can't catch errors they can't import        |
| 3   | Clean up error handling           | Generic `Exception` hides real issues             |
| 4   | Sync documentation with reality   | `Summary.md` lists done features as "future work" |
| 5   | Harden CI (enforce mypy strict)   | Type-check workflow has a "skip on failure" hack  |
| 6   | Tag a stable release              | Give users a reliable version to depend on        |

---

## Task Breakdown

### 1. Create `errors.py` Module

**File**: `src/recursivenamespace/errors.py` (new)

Move these three classes out of `main.py`:

```python
# src/recursivenamespace/errors.py

class SetChainKeyError(KeyError):
    """Raised when a chain-key set hits an incompatible type."""

class GetChainKeyError(KeyError):
    """Raised when a chain-key get hits an incompatible type."""

class SerializationError(Exception):
    """Raised when serialization or deserialization fails."""
```

Then update imports:

- `main.py`: `from .errors import SetChainKeyError, GetChainKeyError, SerializationError`
- `__init__.py`: Import all three from `.errors` and add to `__all__`

**Verification**: `python -c "from recursivenamespace import SetChainKeyError, GetChainKeyError, SerializationError"`

---

### 2. Export All Public Exceptions

**File**: `src/recursivenamespace/__init__.py`

Current `__all__` only exports `SerializationError`. Add the missing two:

```python
from .errors import SetChainKeyError, GetChainKeyError, SerializationError

__all__ = [
    "recursivenamespace",
    "RecursiveNamespace",
    "RNS",
    "rns",
    "SetChainKeyError",
    "GetChainKeyError",
    "SerializationError",
    "__version__",
]
```

---

### 3. Error Handling Cleanup

**File**: `src/recursivenamespace/main.py`

Items to audit:

| Location                          | Issue                                       | Fix                                                |
| --------------------------------- | ------------------------------------------- | -------------------------------------------------- |
| `update()` method                 | Raises generic `Exception`                  | Use `TypeError` or a custom error                  |
| `get_or_else()`                   | Bare `except Exception` swallows all errors | Narrow to `(KeyError, AttributeError, IndexError)` |
| Array validation in chain-key ops | Raises raw `KeyError`                       | Use `SetChainKeyError` / `GetChainKeyError`        |

---

### 4. Documentation Sync

#### 4a. `docs/plan/Summary.md`

- Remove "Future Enhancements" section that lists JSON/TOML and context
  managers as planned — they're implemented
- Update project structure diagram to include new files:
  - `test_serialization.py`, `test_context_managers.py`, `test_core_coverage.py`
  - `benchmarks/bench_chain_keys.py`
  - `examples/{basic,intermediate,advanced,real_world}/`
  - `CONTRIBUTING.md`, `AGENT.md`
- Add serialization and context manager sections to features list
- Update "Generated" date

#### 4b. `docs/plan/PDCA.md`

- Already updated in this cycle (Cycle 3 rewritten)

---

### 5. CI Hardening

#### 5a. `.github/workflows/type-check.yml`

Remove the fallback echo message that allows mypy failures:

```yaml
# REMOVE this pattern:
- run: mypy src/ || echo "Type checking will be enforced..."
# REPLACE with:
- run: mypy src/
```

#### 5b. `pyproject.toml`

Document that Ruff's `target-version = "py310"` is for tooling only (lint
rules and formatting). The library itself supports Python 3.8+ as declared
in `requires-python`.

---

### 6. Release Preparation

- [ ] Run full quality gate:

  ```bash
  ruff check src/ tests/ && \
  ruff format --check src/ tests/ && \
  mypy src/ && \
  pytest --cov --cov-fail-under=85
  ```

- [ ] Verify `pyproject.toml` metadata (author, description, classifiers)
- [ ] Confirm all `__all__` exports match public API
- [ ] Tag version (e.g., `v2.1.0`)
- [ ] Publish to PyPI

---

## Acceptance Criteria

| Criterion                                            | Verification                                                          |
| ---------------------------------------------------- | --------------------------------------------------------------------- |
| Exceptions live in `errors.py`                       | `grep -r "class.*Error" src/recursivenamespace/`                      |
| All 3 exceptions importable from package root        | `python -c "from recursivenamespace import ..."`                      |
| No generic `Exception` raises in main.py             | `grep "raise Exception" src/recursivenamespace/main.py` returns empty |
| `Summary.md` no longer lists done features as future | Manual review                                                         |
| mypy strict enforced in CI (no fallback)             | Check `type-check.yml` has no `\|\| echo`                             |
| All tests pass                                       | `pytest -s` exits 0                                                   |
| Coverage ≥ 85%                                       | `pytest --cov --cov-fail-under=85`                                    |

---

## Estimated Effort

| Task                   | Effort   |
| ---------------------- | -------- |
| Create `errors.py`     | 15 min   |
| Update exports         | 10 min   |
| Error handling cleanup | 30 min   |
| Documentation sync     | 30 min   |
| CI hardening           | 10 min   |
| Release verification   | 15 min   |
| **Total**              | ~2 hours |

---

## Risks

| Risk                              | Mitigation                                   |
| --------------------------------- | -------------------------------------------- |
| Moving exceptions breaks imports  | Keep re-exports in `main.py` for one release |
| Narrowing `except` reveals bugs   | Run full test suite after each change        |
| mypy strict fails on current code | Fix type issues before removing CI fallback  |

---

*This document is part of the PDCA Continuous Improvement framework for
RecursiveNamespaceV2. See [PDCA.md](./PDCA.md) for the overall plan.*
