"""Chain-key access with dot notation and array indexing."""

from recursivenamespace import RNS

ns = RNS({})

# Dot-separated chain keys create nested namespaces automatically
ns.val_set("server.host", "localhost")
ns.val_set("server.port", 8080)
print("server.host:", ns.val_get("server.host"))  # localhost
print("server.port:", ns.val_get("server.port"))  # 8080

# Array operations with []
ns.val_set("users[].#", "Alice")  # append
ns.val_set("users[].#", "Bob")  # append
ns.val_set("users[].#", "Charlie")  # append
print("users:", ns.val_get("users[].0"))  # Alice
print("last:", ns.val_get("users[].#"))  # Charlie (# = last)

# Set by index
ns.val_set("users[].1", "Robert")
print("updated:", ns.val_get("users[].1"))  # Robert

# Deep chain with arrays
ns.val_set("teams[].#.name", "Backend")
ns.val_set("teams[].#.name", "Frontend")
print("team 0:", ns.val_get("teams[].0.name"))  # Backend
print("team 1:", ns.val_get("teams[].1.name"))  # Frontend

# Safe access with fallback
print("missing:", ns.get_or_else("no.such.key", "N/A"))  # N/A

print("\nFinal structure:")
print(ns)
