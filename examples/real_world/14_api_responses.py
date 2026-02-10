"""Handling API responses with RNS."""
import json
from recursivenamespace import RNS

# Simulated API response (as if from requests.get().json())
api_response = json.loads("""
{
    "status": "success",
    "data": {
        "user": {
            "id": 42,
            "name": "Alice",
            "email": "alice@example.com",
            "preferences": {
                "theme": "dark",
                "language": "en",
                "notifications": true
            }
        },
        "permissions": ["read", "write", "admin"]
    },
    "meta": {"request_id": "abc-123", "timestamp": 1700000000}
}
""")

# Convert to RNS for clean attribute access
resp = RNS(api_response)

# Clean, readable access instead of resp["data"]["user"]["name"]
print(f"User: {resp.data.user.name} (#{resp.data.user.id})")
print(f"Email: {resp.data.user.email}")
print(f"Theme: {resp.data.user.preferences.theme}")
print(f"Permissions: {resp.data.permissions}")
print(f"Request ID: {resp.meta.request_id}")

# Safe access for optional fields
bio = resp.get_or_else("data.user.bio", "No bio set")
print(f"Bio: {bio}")

# Extract just what you need
user_dict = resp.data.user.to_dict()
print(f"\nUser dict keys: {list(user_dict.keys())}")
