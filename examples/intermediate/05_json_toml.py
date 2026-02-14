"""JSON and TOML serialization round-trips."""

from recursivenamespace import RNS

# Build a configuration namespace
config = RNS(
    {
        "app": {"name": "MyApp", "version": "1.0.0"},
        "database": {"host": "localhost", "port": 5432},
        "features": ["auth", "api", "logging"],
    }
)

# ── JSON ────────────────────────────────────────────────────────
json_str = config.to_json(indent=2, sort_keys=True)
print("JSON output:")
print(json_str)

# Round-trip: JSON string -> RNS
loaded = RNS.from_json(json_str)
assert loaded.app.name == "MyApp"
assert loaded.database.port == 5432

# File I/O
config.save_json("/tmp/rns_example_config.json")
from_file = RNS.load_json("/tmp/rns_example_config.json")
assert from_file == config

# ── TOML ────────────────────────────────────────────────────────
toml_str = config.to_toml()
print("\nTOML output:")
print(toml_str)

# Round-trip: TOML string -> RNS
loaded_toml = RNS.from_toml(toml_str)
assert loaded_toml.app.name == "MyApp"

# File I/O
config.save_toml("/tmp/rns_example_config.toml")
from_toml_file = RNS.load_toml("/tmp/rns_example_config.toml")
assert from_toml_file.app.name == "MyApp"

print("\nAll serialization round-trips passed!")
