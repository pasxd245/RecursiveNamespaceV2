# Claude Skills for RecursiveNamespaceV2

## Purpose

RecursiveNamespaceV2 is a pure-Python library that extends Python's SimpleNamespace to support recursive/nested data access with both attribute and dict styles. Your work should preserve its core promise: intuitive access to deeply nested structures, robust chain-key operations, and predictable conversion between namespaces and dictionaries.

## Key Concepts to Preserve

- Recursive conversion of nested dicts into namespaces.
- Dual access: attribute-style and dict-style are equivalent.
- Chain-key access with dot notation (e.g., "a.b.c").
- Array indexing syntax in chain keys (e.g., "items[].0", "items[].#").
- Optional key normalization (hyphens to underscores) unless use_raw_key is enabled.
- Safe conversion to dicts, including optional flattening.
- Protected keys: internal attributes must not be user-accessible.

## Core API Surface (Do Not Break)

- RNS / RecursiveNamespace / recursivenamespace alias exports.
- Methods: val_set, val_get, get_or_else, to_dict, update, as_schema, items, keys, values, copy, deepcopy.
- Decorator support via rns.rns() with optional chain-key support.
- Pickle compatibility for serialization.

## Project Layout

- Core implementation: src/recursivenamespace/main.py
- Utilities: src/recursivenamespace/utils.py
- Exports: src/recursivenamespace/__init__.py
- Tests: tests/
- Examples: examples/

## Coding Standards

- Pure Python, no external dependencies.
- Keep API behavior backward compatible.
- Ruff formatting with 80 char line length.
- Target Python 3.8+ (tooling may target 3.10).

## Testing Guidance

- Use pytest. Common runs:
  - pytest -s
  - coverage run -m pytest
- Add tests for chain-key parsing, array indexing, and protected key behavior.
- Validate dict/namespace parity and conversion round trips.

## Common Pitfalls

- Breaking chain-key parsing rules in utils.split_key/join_key.
- Forgetting key normalization behavior when use_raw_key is True.
- Modifying protected keys or allowing user access to them.
- Failing to convert nested structures recursively on updates.

## Suggested Workflow for Changes

1. Identify whether the change touches core semantics (main.py) or key parsing (utils.py).
2. Update or add focused tests in tests/.
3. Verify examples still reflect expected usage.
4. Keep public API stable; add new features in a backward-compatible way.

## When Adding Features

- Prefer extending the existing chain-key grammar rather than introducing new APIs.
- Update README and docs/Summary.md if behavior changes.
- Keep error handling consistent (SetChainKeyError, GetChainKeyError, KeyError).

## Notes for Claude

- Be explicit about chain-key behavior with arrays and nested objects.
- Preserve performance characteristics (lazy processing, lightweight operations).
- Avoid adding dependencies unless explicitly requested.
