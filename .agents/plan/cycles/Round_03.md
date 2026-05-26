# PDCA Cycle 3: Release Readiness & Code Hygiene

**Date Started**: 2026-02-14
**Status**: **IN PROGRESS** — code hygiene done, release prep remaining
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

| #   | Objective                         | Status |
| --- | --------------------------------- | ------ |
| 1   | Extract exceptions to `errors.py` | ✅     |
| 2   | Export all public exceptions      | ✅     |
| 3   | Clean up error handling           | ✅     |
| 4   | Sync documentation with reality   | ✅     |
| 5   | Harden CI (enforce mypy strict)   | ✅     |
| 6   | Flag high-complexity functions    | ✅     |
| 7   | Tag a stable release              | ⏳     |

---

## Completed Work

### 1. Created `errors.py` Module ✅

**File**: `src/recursivenamespace/errors.py`

Extracted three exception classes from `main.py` into a dedicated module
with proper type annotations:

- `SetChainKeyError(KeyError)` — chain-key set on incompatible type
- `GetChainKeyError(KeyError)` — chain-key get on incompatible type
- `SerializationError(Exception)` — serialization/deserialization failure

Updated `main.py` to import from `.errors`:

```python
from .errors import GetChainKeyError, SerializationError, SetChainKeyError
```

---

### 2. Exported All Public Exceptions ✅

**File**: `src/recursivenamespace/__init__.py`

Added `SetChainKeyError` and `GetChainKeyError` to imports and `__all__`:

```python
from .errors import GetChainKeyError, SerializationError, SetChainKeyError

__all__ = [
    "recursivenamespace",
    "RecursiveNamespace",
    "RNS",
    "rns",
    "GetChainKeyError",
    "SerializationError",
    "SetChainKeyError",
    "__version__",
]
```

**Verified**: `python -c "from recursivenamespace import SetChainKeyError, GetChainKeyError, SerializationError"` passes.

---

### 3. Error Handling Cleanup ✅

**File**: `src/recursivenamespace/main.py`

| Location            | Before                                | After                                    |
| ------------------- | ------------------------------------- | ---------------------------------------- |
| `update()`          | `raise Exception(...)` (bare)         | `raise TypeError(...) from e` (chained)  |
| `__process()`       | `print(..., out=sys.stderr)` (bug)    | `print(..., file=sys.stderr)` (fixed)    |
| `get_or_else()`     | `exc_info=1` (int, wrong type)        | `exc_info=True` (bool, correct)          |
| `to_dict()`         | `flatten_sep` passed as `bool \| str` | Type-narrowed with `isinstance` guard    |

**Note**: `get_or_else()` keeps `except Exception` intentionally — it is
designed to be a safe fallback that never throws. The `except` clause is
documented in context.

---

### 4. Documentation Sync ✅

`docs/plan/Summary.md` was already updated in Cycle 2 — verified that:

- JSON/TOML serialization and context managers listed as **completed features**
- Project structure includes new files (test_serialization.py, benchmarks/, etc.)
- No stale "future enhancements" references

---

### 5. CI Hardening ✅

#### 5a. Type-check workflow

**File**: `.github/workflows/type-check.yml`

Removed the fallback that swallowed mypy failures:

```yaml
# Before:
mypy src/recursivenamespace --config-file=pyproject.toml || echo "Type checking will be enforced..."

# After:
mypy src/recursivenamespace --config-file=pyproject.toml
```

#### 5b. Fixed 14 pre-existing mypy errors

These were hidden by the fallback. All fixed:

| Error | Fix |
| --- | --- |
| `python_version = "3.8"` unsupported | Bumped to `"3.9"` in `pyproject.toml` (runtime still 3.8+) |
| `tomllib` / `tomli` import-not-found | Added `type: ignore[import-not-found]` for conditional imports |
| `__protected_keys_` typed as `tuple[()]` | Annotated as `set[str]` |
| `flatten_sep` type mismatch | Added `isinstance` guard before passing to `flatten_as_dict` |
| `val_set` missing return type | Added `-> None` |
| `val_get` missing return type | Added `-> Any` |
| `exc_info=1` wrong type | Changed to `exc_info=True` |
| `dataclasses.asdict` arg type | Added `type: ignore[arg-type]` |
| Decorator `data` variable type narrowing | Annotated as `data: Any` |

**Result**: `mypy src/recursivenamespace --strict` passes with 0 errors.

---

### 6. Cognitive Complexity Audit ✅

Identified and flagged 9 functions with estimated cognitive complexity >= 15.
Each marked with `# TODO(refactor):` for future cleanup:

| File | Function | Complexity | Primary Issue |
| --- | --- | --- | --- |
| `main.py` | `__init__` | ~16 | Nested type checks in loop |
| `main.py` | `__process` | ~17 | isinstance branches + try/except |
| `main.py` | `to_dict` | ~15 | Nested isinstance branches |
| `main.py` | `__chain_set_array` | ~18 | 4-level nesting with index branching |
| `main.py` | `__chain_get_array` | ~16 | Validation + index branching |
| `main.py` | `_dict_to_toml` | ~19 | 5-level nested type checks for TOML |
| `main.py` | `rns` | ~17 | Multi-branch data type handling |
| `utils.py` | `flatten_as_dict` | ~15 | Recursive nested type checks |
| `utils.py` | `flatten_as_list` | ~20 | Deeply nested recursive + enum branching |

These are deferred to a future refactoring cycle to avoid behavioral changes
during release prep.

---

## Remaining Work

### 7. Release Preparation ⏳

- [x] Run full quality gate (ruff, mypy, pytest — all pass)
- [x] Verify `pyproject.toml` metadata (author, description, classifiers)
- [x] Confirm all `__all__` exports match public API
- [ ] Finalize CHANGELOG.md (rename `[Unreleased]` to version)
- [ ] Tag release version
- [ ] Publish to PyPI

---

## Acceptance Criteria

| Criterion                                     | Status |
| --------------------------------------------- | ------ |
| Exceptions live in `errors.py`                | ✅     |
| All 3 exceptions importable from package root | ✅     |
| No generic `raise Exception` in main.py       | ✅     |
| `Summary.md` reflects actual features         | ✅     |
| mypy strict enforced in CI (no fallback)      | ✅     |
| mypy strict passes (0 errors)                 | ✅     |
| All tests pass (104)                          | ✅     |
| Coverage >= 85%                               | ✅     |
| High-complexity functions flagged             | ✅     |
| Stable release tagged                         | ⏳     |

---

## Files Modified

| File | Change |
| --- | --- |
| `src/recursivenamespace/errors.py` | **NEW** — extracted exception classes |
| `src/recursivenamespace/main.py` | Import from errors, bug fixes, type fixes, TODOs |
| `src/recursivenamespace/__init__.py` | Added exception imports and exports |
| `src/recursivenamespace/utils.py` | Added complexity TODO flags |
| `.github/workflows/type-check.yml` | Removed mypy fallback |
| `pyproject.toml` | Bumped mypy python_version 3.8 -> 3.9 |

---

*This document is part of the PDCA Continuous Improvement framework for
RecursiveNamespaceV2. See [PDCA.md](./PDCA.md) for the overall plan.*
