"""Copy, deepcopy, and temporary() context manager."""

from recursivenamespace import RNS

original = RNS(
    {
        "name": "experiment_1",
        "params": {"lr": 0.001, "epochs": 10},
        "results": {"accuracy": 0.95},
    }
)

# ── Shallow copy ────────────────────────────────────────────────
shallow = original.copy()
print("Shallow copy:", shallow.name)

# ── Deep copy ───────────────────────────────────────────────────
deep = original.deepcopy()
deep.params.lr = 0.01
deep.name = "experiment_2"
print(f"Deep copy lr: {deep.params.lr}")  # 0.01
print(f"Original lr:  {original.params.lr}")  # 0.001

# ── temporary() context manager ─────────────────────────────────
print("\nUsing temporary():")
with original.temporary() as tmp:
    tmp.params.lr = 0.1
    tmp.params.epochs = 100
    tmp.results.accuracy = 0.99
    print(f"  Inside: lr={tmp.params.lr}, acc={tmp.results.accuracy}")

print(f"  After:  lr={original.params.lr}, acc={original.results.accuracy}")

# ── pop and delete ──────────────────────────────────────────────
ns = RNS({"a": 1, "b": 2, "c": 3})
val = ns.pop("b")
print(f"\nPopped b={val}, remaining keys: {ns.keys()}")

del ns["c"]
print(f"After del c: {ns.keys()}")
