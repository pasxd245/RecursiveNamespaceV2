"""Benchmark chain-key operations and regex caching.

Run: python benchmarks/bench_chain_keys.py
"""
from __future__ import annotations

import timeit

from recursivenamespace import RNS
from recursivenamespace.utils import _compile_split_pattern, split_key


def build_deep_structure(depth: int = 10) -> dict:
    """Build a nested dict with the given depth."""
    d: dict = {"leaf": "value"}
    for i in range(depth):
        d = {f"level_{i}": d}
    return d


def bench_split_key(n: int = 10_000) -> float:
    key = "a.b.c.d.e.f.g"
    t = timeit.timeit(lambda: split_key(key), number=n)
    return t


def bench_val_get(n: int = 10_000) -> float:
    data = build_deep_structure(5)
    ns = RNS(data)
    chain = "level_4.level_3.level_2.level_1.level_0.leaf"
    t = timeit.timeit(lambda: ns.val_get(chain), number=n)
    return t


def bench_val_set(n: int = 10_000) -> float:
    ns = RNS({})
    t = timeit.timeit(
        lambda: ns.val_set("a.b.c.d.e", "value"), number=n
    )
    return t


def bench_creation(n: int = 10_000) -> float:
    data = {
        "app": {"name": "test", "version": "1.0"},
        "db": {"host": "localhost", "port": 5432},
        "features": ["a", "b", "c"],
    }
    t = timeit.timeit(lambda: RNS(data), number=n)
    return t


def main() -> None:
    n = 50_000
    print(f"Benchmarking with {n:,} iterations each\n")

    info = _compile_split_pattern.cache_info()
    print(f"Cache before: {info}")

    results = {
        "split_key": bench_split_key(n),
        "val_get (5-deep)": bench_val_get(n),
        "val_set (5-deep)": bench_val_set(n),
        "RNS creation": bench_creation(n),
    }

    info = _compile_split_pattern.cache_info()
    print(f"Cache after:  {info}\n")

    for name, elapsed in results.items():
        ops = n / elapsed
        print(f"{name:25s}  {elapsed:.4f}s  ({ops:,.0f} ops/s)")


if __name__ == "__main__":
    main()
