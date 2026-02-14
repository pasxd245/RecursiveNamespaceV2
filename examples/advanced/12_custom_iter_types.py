"""Using accepted_iter_types to preserve custom iterables."""

from recursivenamespace import RNS

# By default, tuples and sets are recursively processed
default = RNS({"coords": (1, 2, 3), "tags": {"a", "b"}})
print(f"Default tuple type: {type(default.coords)}")
print(f"Default set type:   {type(default.tags)}")

# Preserve tuples by passing accepted_iter_types
preserved = RNS(
    {"coords": (1, 2, 3), "tags": {"a", "b"}},
    accepted_iter_types=[tuple, set],
)
print(f"\nPreserved tuple: {preserved.coords}")
print(f"Preserved set:   {preserved.tags}")
assert isinstance(preserved.coords, tuple)
assert isinstance(preserved.tags, set)

# Nested structures also respect the setting
nested = RNS(
    {"data": {"points": (10, 20), "labels": {"x", "y"}}},
    accepted_iter_types=[tuple, set],
)
print(f"\nNested tuple: {nested.data.points}")
print(f"Nested set:   {nested.data.labels}")

# raw_key mode disables key normalization
raw = RNS({"my-key": 1, "other.key": 2}, use_raw_key=True)
print(f"\nRaw keys: {raw.keys()}")
# Access with original key names (no normalization)
print(f"my-key: {getattr(raw, 'my-key')}")
print(f"other.key: {getattr(raw, 'other.key')}")
