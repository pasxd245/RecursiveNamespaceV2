"""Flatten nested structures and reconstruct from flat dicts."""
from pprint import pprint
from recursivenamespace import RNS

data = RNS({
    "model": {
        "name": "bert-base",
        "layers": {"hidden": 768, "attention": 12},
    },
    "training": {
        "lr": 0.001,
        "batch_size": 32,
        "epochs": 10,
    },
})

# Flatten with dot separator
flat_dot = data.to_dict(flatten_sep=".")
print("Flat (dot):")
pprint(flat_dot)

# Flatten with underscore separator
flat_us = data.to_dict(flatten_sep="_")
print("\nFlat (underscore):")
pprint(flat_us)

# Reconstruct from flat dict using chain keys
reconstructed = RNS({})
for key, value in flat_dot.items():
    reconstructed.val_set(key, value)

print("\nReconstructed:")
print(f"  model.name = {reconstructed.model.name}")
print(f"  training.lr = {reconstructed.training.lr}")

# Verify round-trip
assert reconstructed.to_dict() == data.to_dict()
print("\nRound-trip verified!")
