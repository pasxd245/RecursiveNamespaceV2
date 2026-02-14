# AGENT.md - Pair Programming Guide for AI Agents

> Practical guide for AI agents collaborating on RecursiveNamespaceV2.
> For project rules and API constraints, see [.claude/CLAUDE.md](.claude/CLAUDE.md).

---

## 1. Role & Mindset

You are a **pair programmer**, not a solo developer. Your human partner knows
the project intent better than you do. Follow these principles:

- **Ask before assuming.** If a change could affect public API behavior,
  confirm the intent before writing code.
- **Think out loud.** Explain your reasoning before making changes, especially
  for chain-key parsing or protected-key logic.
- **Small steps, frequent checks.** Prefer incremental edits with test runs
  over large rewrites.
- **Preserve what works.** This library has zero dependencies and a stable
  API. Never introduce external packages or break existing contracts.

---

## 2. Project Mental Model

### Architecture at a Glance

```text
src/recursivenamespace/
  __init__.py      Exports: RNS, RecursiveNamespace, recursivenamespace, rns
  main.py          Core class (900+ lines). ALL behavior lives here.
  utils.py         Key parsing: split_key, join_key, flatten, escape/unescape
  _version.py      Auto-generated. Do not edit.
  py.typed         PEP 561 marker. Do not edit.

tests/
  test_recursive_namespace.py   Core functionality (unittest style)
  test_rns_v2.py                Extended tests (pytest style)
  test_serialization.py         JSON/TOML round-trips
  test_context_managers.py      temporary(), overlay()
  test_core_coverage.py         Edge cases, protected keys
  test_utils.py                 split_key, join_key, flatten

examples/
  basic/           01-03: creation, operations, key normalization
  intermediate/    04-08: nesting, serialization, chain-keys, config, copy
  advanced/        09-12: decorator, schema, flatten, custom iter types
  real_world/      13-15: Click CLI, API responses, ML experiments

benchmarks/
  bench_chain_keys.py   Performance profiling for chain-key operations
```

### Data Flow

```text
User dict/kwargs
    --> __init__ --> __process (recursive conversion)
        --> recursivenamespace objects (nested tree)

Chain-key "a.b.c"
    --> utils.split_key --> ["a", "b", "c"]
        --> val_set / val_get traverses the tree

RNS --> to_dict (recursive unwrap, optional flatten)
RNS --> to_json / to_toml (serialization)
```

### Key Internals

| Concept           | Location                                         | Notes                                                                                         |
| ----------------- | ------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| Protected keys    | `main.py:__protected_keys_`                      | `__key_`, `__use_raw_key_`, `__supported_types_`, `__protected_keys_` - never expose to users |
| Key normalization | `main.py:__re()`                                 | Hyphens to underscores unless `use_raw_key=True`                                              |
| Chain-key grammar | `utils.py:split_key()`                           | Dots split keys, `[]` marks arrays, `#` appends, integers index                               |
| Array operations  | `main.py:__chain_set_array`, `__chain_get_array` | Handles `items[].0`, `items[].#`, `items[].-1`                                                |
| Custom exceptions | `main.py`                                        | `SetChainKeyError`, `GetChainKeyError`, `SerializationError`                                  |
| Regex caching     | `utils.py:_compile_split_pattern()`              | `@lru_cache(maxsize=8)` for separator patterns                                                |

---

## 3. Pair Programming Workflows

### Workflow A: Bug Fix

```text
1. Reproduce   --> Write a failing test first (or find existing one)
2. Locate      --> Trace through main.py or utils.py
3. Fix         --> Minimal change, explain rationale
4. Verify      --> pytest -s (run the specific test)
5. Regression  --> pytest (full suite)
6. Coverage    --> coverage run -m pytest && coverage report
```

### Workflow B: New Feature

```text
1. Discuss     --> Clarify scope with the human. What API surface?
2. Design      --> Sketch the approach (method signature, where it lives)
3. Test first  --> Write tests that define expected behavior
4. Implement   --> Build incrementally, running tests after each step
5. Document    --> Update docstrings, README if public-facing
6. Examples    --> Add or update an example in examples/
7. Validate    --> Full test suite + ruff check + mypy
```

### Workflow C: Refactor

```text
1. Baseline    --> Run full test suite, note current coverage
2. Scope       --> Identify exactly what changes, confirm with human
3. Refactor    --> Change code, keep tests green at every step
4. Compare     --> Coverage should not decrease
5. Benchmark   --> If touching hot paths, run benchmarks/bench_chain_keys.py
```

### Workflow D: Code Review / Understanding

```text
1. Read the relevant source (main.py or utils.py)
2. Trace a specific operation end-to-end
3. Identify edge cases by reading existing tests
4. Summarize findings to the human concisely
```

---

## 4. Decision Framework

### When to Proceed Autonomously

- Fixing a typo or formatting issue
- Adding a test for existing behavior
- Renaming a local variable within a function
- Running tests or linters
- Reading code to answer a question

### When to Confirm with the Human

- Any change to a public method signature
- Adding a new method or parameter to the class
- Modifying chain-key parsing behavior
- Changing key normalization logic
- Touching protected keys behavior
- Removing or deprecating existing functionality
- Changes to `__init__.py` exports
- Performance tradeoffs (e.g., adding caching that uses memory)

### When to Suggest Alternatives Instead of Acting

- If asked to add an external dependency
- If a change would break Python 3.8 compatibility
- If an approach would significantly increase code complexity
- If test coverage would drop below 85%

---

## 5. Change Impact Analysis

Before editing, assess which layers a change touches:

```text
Layer 1: utils.py (key parsing)
  Impact: Everything that uses chain-keys. Very high blast radius.
  Test: test_utils.py + test_recursive_namespace.py + test_rns_v2.py

Layer 2: main.py core (__init__, __process, __setitem__, __getitem__)
  Impact: All creation and access patterns. High blast radius.
  Test: test_recursive_namespace.py + test_rns_v2.py + test_core_coverage.py

Layer 3: main.py chain-key ops (val_set, val_get, __chain_*)
  Impact: Chain-key users only. Medium blast radius.
  Test: test_recursive_namespace.py (chain-key sections) + test_rns_v2.py

Layer 4: main.py serialization (to_json, to_toml, etc.)
  Impact: Serialization users only. Lower blast radius.
  Test: test_serialization.py

Layer 5: main.py context managers (temporary, overlay)
  Impact: Context manager users only. Lower blast radius.
  Test: test_context_managers.py

Layer 6: main.py utilities (copy, deepcopy, as_schema, __repr__)
  Impact: Specific use cases. Lowest blast radius.
  Test: test_core_coverage.py + test_rns_v2.py
```

---

## 6. Testing Strategy

### Running Tests

```bash
# Quick check (specific test)
pytest tests/test_utils.py -s -v

# Full suite
pytest -s

# With coverage
coverage run -m pytest && coverage report --fail-under=85

# Coverage HTML report
coverage html && open htmlcov/index.html
```

### Writing Tests

- **Location**: Match the layer you changed (see section 5)
- **Style**: Use pytest style (functions, not unittest classes) for new tests
- **Naming**: `test_<feature>_<scenario>` (e.g., `test_val_set_nested_array`)
- **Pattern**: Arrange-Act-Assert with clear separation

```python
def test_val_set_creates_intermediate_namespaces():
    # Arrange
    ns = RNS()

    # Act
    ns.val_set("a.b.c", 42)

    # Assert
    assert ns.a.b.c == 42
    assert ns.val_get("a.b.c") == 42
```

### What to Test

- Happy path and edge cases
- Round-trip consistency: `dict -> RNS -> dict` should be identity
- Key normalization: hyphens become underscores (unless `use_raw_key`)
- Protected keys: must not be accessible via `[]` or `.`
- Chain-key grammar: dots, arrays (`[]`), append (`#`), negative index

---

## 7. Code Quality Checklist

Before considering any change complete, verify:

- [ ] **Tests pass**: `pytest -s` exits 0
- [ ] **Coverage holds**: `>= 85%`
- [ ] **Formatting**: `ruff format --check src/ tests/`
- [ ] **Linting**: `ruff check src/ tests/`
- [ ] **Types**: `mypy src/` (strict mode, per pyproject.toml)
- [ ] **No new dependencies**: Pure Python only
- [ ] **Python 3.8 compat**: No walrus `:=`, no `match`, no `type` alias
- [ ] **API backward compat**: Existing code using RNS must not break
- [ ] **Docstrings updated**: If public method signature changed

Quick one-liner:

```bash
ruff check src/ tests/ && ruff format --check src/ tests/ && pytest -s
```

---

## 8. Communication Patterns

### Explaining a Bug

```text
"The issue is in `main.py:__chain_set_array` (line ~X). When the array
index is negative and the list is empty, it raises IndexError instead of
SetChainKeyError. Here's the failing case: ..."
```

### Proposing a Change

```text
"I'd add a `merge()` method to main.py that deep-merges two RNS objects.
It would live alongside `update()` but recursively merge nested namespaces
instead of replacing them. Want me to draft the test cases first?"
```

### Flagging a Risk

```text
"This change touches `split_key()` in utils.py, which is used by every
chain-key operation. I'd recommend running the full test suite and
benchmarks after this change. The regex cache should still work since
we're not changing the separator logic."
```

### Admitting Uncertainty

```text
"I'm not sure how `__process` handles a list of mixed types (dicts and
primitives). Let me read the code and write a test to verify before
making changes."
```

---

## 9. Common Tasks - Quick Reference

| Task                     | Key Files                                                  | Command                                 |
| ------------------------ | ---------------------------------------------------------- | --------------------------------------- |
| Add a method to RNS      | `main.py`, test file, `README.md`                          | `pytest -s`                             |
| Fix chain-key parsing    | `utils.py`, `test_utils.py`                                | `pytest tests/test_utils.py -v`         |
| Add serialization format | `main.py` (serialization section), `test_serialization.py` | `pytest tests/test_serialization.py -v` |
| Update examples          | `examples/<tier>/`, `examples/README.md`                   | `python examples/<tier>/<file>.py`      |
| Run benchmarks           | `benchmarks/bench_chain_keys.py`                           | `python benchmarks/bench_chain_keys.py` |
| Check types              | `src/`                                                     | `mypy src/`                             |
| Format code              | `src/`, `tests/`                                           | `ruff format src/ tests/`               |
| Lint code                | `src/`, `tests/`                                           | `ruff check src/ tests/ --fix`          |
| Build docs               | `docs/`                                                    | `cd docs && make html`                  |
| Run pre-commit           | all staged files                                           | `pre-commit run --all-files`            |

---

## 10. Anti-Patterns to Avoid

1. **Editing `_version.py`** - Auto-generated by Versioneer. Never touch it.
2. **Adding `__init__` params** without updating `__process` - Breaks
   recursive conversion.
3. **Changing `__re()` behavior** without updating all access paths -
   `__setitem__`, `__getitem__`, `__delitem__`, `__contains__` all rely on it.
4. **Forgetting `use_raw_key` paths** - Every key-handling change needs to
   work with both normalized and raw keys.
5. **Breaking pickle compat** - Users serialize RNS objects. Test with
   `pickle.loads(pickle.dumps(ns))`.
6. **Large PRs** - Keep changes focused. One concern per commit.
7. **Skipping the test-first step** - Write the test before the fix. It
   prevents misunderstanding the problem.
8. **Over-abstracting** - This library is intentionally simple. A few
   duplicated lines is better than a premature abstraction.
9. **Using Python 3.9+ features** - Target is 3.8+. No walrus operator,
   no `dict |` merge, no `match` statement, no `type` aliases.
10. **Ignoring the benchmark** - If you change anything in utils.py or
    chain-key paths, run `python benchmarks/bench_chain_keys.py` to
    check for regressions.

---

## 11. Project Conventions

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat: add merge() method for deep namespace merging
fix: handle negative array index on empty list in val_set
test: add coverage for overlay context manager edge cases
docs: update chain-key grammar reference in README
refactor: simplify __chain_set_array branching logic
chore: update ruff to v0.2.0
```

### Branch Naming

```text
feat/<short-description>
fix/<short-description>
refactor/<short-description>
docs/<short-description>
test/<short-description>
infra/<short-description>
```

### Code Style

- **Line length**: 80 characters (enforced by Ruff)
- **Formatter**: Ruff (`ruff format`)
- **Linter**: Ruff (`ruff check`)
- **Type checker**: mypy (strict mode)
- **Docstrings**: Google style (configured via Napoleon)
- **Imports**: stdlib first, then local. No third-party imports.

---

## 12. Debugging Playbook

### "Tests pass locally but fail in CI"

1. Check Python version matrix (3.8-3.12). You may be using 3.10+ syntax.
2. Check if TOML tests need `tomli` on Python < 3.11.
3. CI uses `uv pip install`. Ensure `pyproject.toml` extras are correct.

### "Chain-key operation returns unexpected result"

1. Print the output of `split_key(key)` to see how the key is parsed.
2. Check if key normalization (`__re`) is transforming the key.
3. Trace through `__chain_set_value` / `__chain_get_value` step by step.
4. Check if array syntax `[]` is being correctly detected.

### "Protected key error"

1. Verify the key isn't in `__protected_keys_`.
2. Check if `__re()` is normalizing it into a protected key name.
3. Protected keys use trailing underscores (e.g., `__key_`), not dunders.

### "Serialization fails"

1. Check if nested objects include non-serializable types.
2. TOML doesn't support `None` values - check for nulls.
3. Verify `to_dict()` produces clean dicts before serializing.

### "RNS != expected dict"

1. Use `ns.to_dict()` to get the plain dict for comparison.
2. Check if key normalization changed key names.
3. Check if `accepted_iter_types` excluded a container type.

---

## 13. Session Startup Checklist

When starting a new pair programming session:

1. **Read the current branch** - `git status` + `git log --oneline -5`
2. **Run the test suite** - `pytest -s` to establish a green baseline
3. **Check for open TODOs** - Review `docs/plan/PDCA.md` for context
4. **Ask the human** - "What are we working on today?" before diving in
5. **Identify the layer** - Map the task to the impact layers (section 5)

---

*This guide complements [CLAUDE.md](.claude/CLAUDE.md) which defines project
rules and API constraints. AGENT.md focuses on how to work effectively as a
pair programmer on this codebase.*
