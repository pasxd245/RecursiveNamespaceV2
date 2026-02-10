"""Application configuration management with overlay()."""
from recursivenamespace import RNS

# Base configuration
config = RNS({
    "debug": False,
    "log_level": "INFO",
    "database": {"host": "db.prod.internal", "port": 5432},
    "cache_ttl": 300,
})

print("Production config:")
print(f"  debug={config.debug}, db={config.database.host}")

# Temporarily switch to development settings
with config.overlay({"debug": True, "log_level": "DEBUG"}):
    print("\nDev overlay active:")
    print(f"  debug={config.debug}, log_level={config.log_level}")
    print(f"  db still={config.database.host}")  # unchanged

print("\nBack to production:")
print(f"  debug={config.debug}, log_level={config.log_level}")

# Nested overlays for testing
with config.overlay({"cache_ttl": 0}):
    print(f"\nNo-cache overlay: ttl={config.cache_ttl}")
    with config.overlay({"debug": True}):
        print(f"  + debug overlay: debug={config.debug}, "
              f"ttl={config.cache_ttl}")
    print(f"  After inner exit: debug={config.debug}")

print(f"\nFinal: debug={config.debug}, ttl={config.cache_ttl}")
