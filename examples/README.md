# Examples

## Basic

| File                                                       | Description                                       |
| ---------------------------------------------------------- | ------------------------------------------------- |
| [01_basic_usage.py](basic/01_basic_usage.py)               | Attribute/dict access, flattening, dynamic fields |
| [02_basic_operations.py](basic/02_basic_operations.py)     | Dict conversion, nested access, len/keys/items    |
| [03_keys_vs_attributes.py](basic/03_keys_vs_attributes.py) | Key normalization (hyphens to underscores)        |

## Intermediate

| File                                                            | Description                                      |
| --------------------------------------------------------------- | ------------------------------------------------ |
| [04_nested_namespace.py](intermediate/04_nested_namespace.py)   | Deeply nested employee data access               |
| [05_json_toml.py](intermediate/05_json_toml.py)                 | JSON/TOML serialization round-trips and file I/O |
| [06_chain_keys.py](intermediate/06_chain_keys.py)               | Chain-key dot notation and array indexing        |
| [07_config_management.py](intermediate/07_config_management.py) | Config overlays for dev/prod switching           |
| [08_copy_and_modify.py](intermediate/08_copy_and_modify.py)     | copy, deepcopy, temporary(), pop, delete         |

## Advanced

| File                                                            | Description                                         |
| --------------------------------------------------------------- | --------------------------------------------------- |
| [09_decorator_usage.py](advanced/09_decorator_usage.py)         | @rns.rns() decorator with chain-keys and KV_Pair    |
| [10_schema_conversion.py](advanced/10_schema_conversion.py)     | Converting RNS to typed dataclasses                 |
| [11_flatten_reconstruct.py](advanced/11_flatten_reconstruct.py) | Flatten nested data and reconstruct from flat dicts |
| [12_custom_iter_types.py](advanced/12_custom_iter_types.py)     | Preserving tuples/sets, raw_key mode                |

## Real World

| File                                                          | Description                                      |
| ------------------------------------------------------------- | ------------------------------------------------ |
| [13_click_integration.py](real_world/13_click_integration.py) | CLI tool with Click library integration          |
| [14_api_responses.py](real_world/14_api_responses.py)         | Handling nested API/JSON responses               |
| [15_ml_experiments.py](real_world/15_ml_experiments.py)       | ML experiment tracking and hyperparameter sweeps |
