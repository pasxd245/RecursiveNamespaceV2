"""Converting RNS to typed dataclasses with as_schema()."""
from __future__ import annotations

import dataclasses
from recursivenamespace import RNS


@dataclasses.dataclass
class DatabaseConfig:
    host: str
    port: int
    name: str


@dataclasses.dataclass
class AppConfig:
    debug: bool
    version: str


# Create from dynamic data (e.g., loaded from JSON/TOML)
raw = RNS({
    "host": "db.example.com",
    "port": 5432,
    "name": "mydb",
})

# Convert to a typed dataclass
db = raw.as_schema(DatabaseConfig)
print(f"DB: {db.host}:{db.port}/{db.name}")
print(f"Type: {type(db).__name__}")  # DatabaseConfig

# Works with any dataclass
app_data = RNS({"debug": True, "version": "2.0.1"})
app = app_data.as_schema(AppConfig)
print(f"\nApp v{app.version}, debug={app.debug}")
print(f"Type: {type(app).__name__}")  # AppConfig
