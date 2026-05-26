# Copilot Instructions for RecursiveNamespaceV2

> For full agent workflows and planning artifacts, see
> [AGENTS.md](../AGENTS.md) and the `.agents/` directory.

## Project Overview

RecursiveNamespaceV2 is a **pure-Python** library (zero dependencies)
that extends `SimpleNamespace` to support recursive/nested data access
with both attribute and dict styles.

## Project Layout

- `src/recursivenamespace/main.py` — Core class implementation
- `src/recursivenamespace/utils.py` — Key parsing (split_key, join_key, flatten)
- `src/recursivenamespace/__init__.py` — Public exports
- `tests/` — pytest test suite
- `examples/` — Usage examples (basic, intermediate, advanced, real_world)

## Coding Standards

- **Pure Python** — never add external dependencies.
- **Python 3.8+** — no walrus `:=`, no `match`, no `dict |`, no `type` aliases.
- **Ruff** formatter and linter, 80-char line length.
- **mypy** strict mode for type checking.
- **Google-style** docstrings.

## Key Concepts

- Recursive conversion of nested dicts into namespaces.
- Attribute-style and dict-style access are equivalent.
- Chain-key dot notation: `"a.b.c"` traverses nested namespaces.
- Array indexing in chain keys: `"items[].0"`, `"items[].#"`.
- Key normalization: hyphens to underscores unless `use_raw_key=True`.
- Protected keys (`__key_`, `__use_raw_key_`, etc.) must never be
  exposed to users.

## Core API (Do Not Break)

- Exports: `RNS`, `RecursiveNamespace`, `recursivenamespace`, `rns`.
- Methods: `val_set`, `val_get`, `get_or_else`, `to_dict`, `update`,
  `as_schema`, `items`, `keys`, `values`, `copy`, `deepcopy`.
- Decorator: `rns.rns()` with optional chain-key support.
- Pickle serialization must remain compatible.

## Common Pitfalls

- Breaking chain-key parsing in `utils.split_key` / `join_key`.
- Forgetting `use_raw_key` code paths when modifying key handling.
- Allowing user access to protected keys.
- Not converting nested structures recursively on updates.

## When Suggesting Code

- Keep changes backward compatible with the existing API.
- Prefer extending chain-key grammar over introducing new APIs.
- Use consistent error types: `SetChainKeyError`, `GetChainKeyError`, `KeyError`.
- Avoid over-engineering — a few duplicated lines beats a premature abstraction.
- Always consider both normalized and raw-key paths.

## Testing

- Framework: pytest.
- Naming: `test_<feature>_<scenario>`.
- Cover: chain-key parsing, array indexing, protected keys,
  dict/namespace round trips, key normalization.
- Maintain coverage >= 85%.
