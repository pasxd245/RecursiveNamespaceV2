"""Using the @rns.rns() decorator to wrap function returns."""
from recursivenamespace import rns
from recursivenamespace.utils import KV_Pair


# Basic decorator: dict return -> RNS
@rns.rns()
def get_user():
    return {"name": "Alice", "role": "admin", "active": True}


user = get_user()
print(f"User: {user.name} ({user.role})")


# Non-dict return is wrapped in a "props" key
@rns.rns()
def get_version():
    return "2.1.0"


ver = get_version()
print(f"Version: {ver.props}")


# Chain-key decorator with KV_Pair
@rns.rns(use_chain_key=True)
def build_config():
    return [
        KV_Pair("app.name", "MyApp"),
        KV_Pair("app.version", "1.0"),
        KV_Pair("db.host", "localhost"),
        KV_Pair("db.port", 5432),
    ]


config = build_config()
print(f"\nConfig: {config.app.name} v{config.app.version}")
print(f"DB: {config.db.host}:{config.db.port}")


# Decorator with accepted_iter_types
@rns.rns(accepted_iter_types=[tuple])
def get_data():
    return {"coords": (1.5, 2.5), "tags": ["a", "b"]}


data = get_data()
print(f"\nCoords (tuple preserved): {data.coords}")
print(f"Tags: {data.tags}")
