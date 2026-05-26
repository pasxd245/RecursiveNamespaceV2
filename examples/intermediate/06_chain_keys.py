"""Chain-key access with dot notation and array indexing."""

from recursivenamespace import RNS

ns = RNS({})

# Dot-separated chain keys create nested namespaces automatically
ns._.val_set("server.host", "localhost")
ns._.val_set("server.port", 8080)
print("server.host:", ns._.val_get("server.host"))  # localhost
print("server.port:", ns._.val_get("server.port"))  # 8080

# Array operations with []
ns._.val_set("users[].#", "Alice")  # append
ns._.val_set("users[].#", "Bob")  # append
ns._.val_set("users[].#", "Charlie")  # append
print("users:", ns._.val_get("users[].0"))  # Alice
print("last:", ns._.val_get("users[].#"))  # Charlie (# = last)

# Set by index
ns._.val_set("users[].1", "Robert")
print("updated:", ns._.val_get("users[].1"))  # Robert

# Deep chain with arrays
ns._.val_set("teams[].#.name", "Backend")
ns._.val_set("teams[].#.name", "Frontend")
print("team 0:", ns._.val_get("teams[].0.name"))  # Backend
print("team 1:", ns._.val_get("teams[].1.name"))  # Frontend

# Safe access with fallback
print("missing:", ns._.get_or_else("no.such.key", "N/A"))  # N/A

print("\nFinal structure:")
print(ns)
