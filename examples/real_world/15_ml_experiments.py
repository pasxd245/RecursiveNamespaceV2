"""ML experiment tracking with RNS."""
from recursivenamespace import RNS

# Define experiment configuration
experiment = RNS({
    "name": "bert-finetune-v3",
    "model": {
        "architecture": "bert-base-uncased",
        "hidden_size": 768,
        "num_layers": 12,
    },
    "training": {
        "learning_rate": 3e-5,
        "batch_size": 32,
        "epochs": 5,
        "optimizer": "adamw",
        "warmup_steps": 500,
    },
    "data": {
        "dataset": "squad_v2",
        "train_split": 0.9,
        "max_length": 512,
    },
})

# Log parameters as flat dict (for MLflow, W&B, etc.)
flat_params = experiment.to_dict(flatten_sep="/")
print("Flat params for logger:")
for k, v in flat_params.items():
    print(f"  {k}: {v}")

# Simulate training results
experiment["results"] = RNS({
    "best_f1": 0.891,
    "best_em": 0.823,
    "train_loss": 0.142,
    "eval_loss": 0.287,
})

# Save experiment as JSON
experiment.save_json("/tmp/rns_experiment.json")
print(f"\nSaved experiment: {experiment.name}")

# Load and compare later
loaded = RNS.load_json("/tmp/rns_experiment.json")
print(f"Loaded: {loaded.name}")
print(f"  Best F1: {loaded.results.best_f1}")
print(f"  LR: {loaded.training.learning_rate}")

# Quick hyperparameter sweep with overlay
print("\nHyperparameter sweep:")
for lr in [1e-5, 3e-5, 5e-5]:
    with experiment.overlay({"training": RNS({"learning_rate": lr})}):
        print(f"  LR={experiment.training.learning_rate}")
