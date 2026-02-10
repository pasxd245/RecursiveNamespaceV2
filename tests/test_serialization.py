"""
Tests for JSON and TOML serialization functionality.
"""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from recursivenamespace import (
    RNS,
    SerializationError,
)

# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_JSON = FIXTURES_DIR / "sample_config.json"
SAMPLE_TOML = FIXTURES_DIR / "sample_config.toml"


# JSON Serialization Tests


def test_to_json_basic():
    """Test basic JSON serialization."""
    rns = RNS({"name": "John", "age": 30, "active": True})
    json_str = rns.to_json()
    assert isinstance(json_str, str)
    # Verify it's valid JSON
    data = json.loads(json_str)
    assert data["name"] == "John"
    assert data["age"] == 30
    assert data["active"] is True


def test_to_json_nested():
    """Test JSON serialization with nested structures."""
    rns = RNS(
        {
            "user": {
                "name": "Alice",
                "contact": {
                    "email": "alice@example.com",
                    "phone": "123-456-7890",
                },
            }
        }
    )
    json_str = rns.to_json()
    data = json.loads(json_str)
    assert data["user"]["name"] == "Alice"
    assert data["user"]["contact"]["email"] == "alice@example.com"


def test_to_json_with_lists():
    """Test JSON serialization with lists."""
    rns = RNS(
        {
            "numbers": [1, 2, 3],
            "tags": ["python", "json", "test"],
            "mixed": [1, "two", 3.0, True],
        }
    )
    json_str = rns.to_json()
    data = json.loads(json_str)
    assert data["numbers"] == [1, 2, 3]
    assert data["tags"] == ["python", "json", "test"]
    assert data["mixed"] == [1, "two", 3.0, True]


def test_to_json_indent_none():
    """Test JSON serialization without indentation (compact)."""
    rns = RNS({"a": 1, "b": 2})
    json_str = rns.to_json(indent=None)
    assert "\n" not in json_str
    assert json_str == '{"a": 1, "b": 2}' or json_str == '{"b": 2, "a": 1}'


def test_to_json_sort_keys():
    """Test JSON serialization with sorted keys."""
    rns = RNS({"z": 1, "a": 2, "m": 3})
    json_str = rns.to_json(indent=None, sort_keys=True)
    assert json_str == '{"a": 2, "m": 3, "z": 1}'


def test_to_json_unicode():
    """Test JSON serialization with Unicode characters."""
    rns = RNS({"name": "José", "city": "São Paulo", "emoji": "🚀"})
    json_str = rns.to_json(ensure_ascii=False)
    data = json.loads(json_str)
    assert data["name"] == "José"
    assert data["city"] == "São Paulo"
    assert data["emoji"] == "🚀"


def test_to_json_empty():
    """Test JSON serialization of empty namespace."""
    rns = RNS({})
    json_str = rns.to_json()
    data = json.loads(json_str)
    assert data == {}


def test_from_json_basic():
    """Test basic JSON deserialization."""
    json_str = '{"name": "John", "age": 30, "active": true}'
    rns = RNS.from_json(json_str)
    assert rns.name == "John"
    assert rns.age == 30
    assert rns.active is True


def test_from_json_nested():
    """Test JSON deserialization with nested structures."""
    json_str = """{
        "user": {
            "name": "Bob",
            "settings": {
                "theme": "dark",
                "notifications": true
            }
        }
    }"""
    rns = RNS.from_json(json_str)
    assert rns.user.name == "Bob"
    assert rns.user.settings.theme == "dark"
    assert rns.user.settings.notifications is True


def test_from_json_with_lists():
    """Test JSON deserialization with arrays."""
    json_str = '{"numbers": [1, 2, 3], "names": ["Alice", "Bob"]}'
    rns = RNS.from_json(json_str)
    assert rns.numbers == [1, 2, 3]
    assert rns.names == ["Alice", "Bob"]


def test_from_json_invalid():
    """Test JSON deserialization with invalid JSON."""
    with pytest.raises(SerializationError, match="Invalid JSON"):
        RNS.from_json("{invalid json")


def test_from_json_non_dict():
    """Test JSON deserialization with non-dict JSON."""
    with pytest.raises(SerializationError, match="must represent a dict"):
        RNS.from_json("[1, 2, 3]")


def test_json_round_trip():
    """Test JSON round-trip (dict -> RNS -> JSON -> RNS -> dict)."""
    original = {
        "config": {"debug": True, "port": 8000, "features": ["auth", "logging"]}
    }
    rns1 = RNS(original)
    json_str = rns1.to_json()
    rns2 = RNS.from_json(json_str)
    result = rns2.to_dict()
    assert result == original


def test_save_json(tmp_path):
    """Test saving JSON to file."""
    rns = RNS({"test": "data", "number": 42})
    filepath = tmp_path / "test.json"
    rns.save_json(filepath)

    assert filepath.exists()
    with open(filepath) as f:
        data = json.load(f)
    assert data["test"] == "data"
    assert data["number"] == 42


def test_save_json_creates_dirs(tmp_path):
    """Test save_json creates parent directories."""
    rns = RNS({"key": "value"})
    filepath = tmp_path / "nested" / "dirs" / "test.json"
    rns.save_json(filepath)
    assert filepath.exists()


def test_load_json():
    """Test loading JSON from file."""
    rns = RNS.load_json(SAMPLE_JSON)
    assert rns.app.name == "MyApp"
    assert rns.app.version == "1.0.0"
    assert rns.database.port == 5432
    assert rns.database.credentials.username == "admin"


def test_load_json_file_not_found():
    """Test load_json with non-existent file."""
    with pytest.raises(FileNotFoundError):
        RNS.load_json("nonexistent.json")


def test_json_file_round_trip(tmp_path):
    """Test JSON file round-trip."""
    original = {"data": {"nested": [1, 2, 3]}}
    rns1 = RNS(original)

    filepath = tmp_path / "round_trip.json"
    rns1.save_json(filepath)
    rns2 = RNS.load_json(filepath)

    assert rns2.to_dict() == original


# TOML Serialization Tests


def test_to_toml_basic():
    """Test basic TOML serialization."""
    rns = RNS({"name": "MyApp", "version": "1.0.0", "debug": False})
    toml_str = rns.to_toml()
    assert isinstance(toml_str, str)
    assert 'name = "MyApp"' in toml_str
    assert 'version = "1.0.0"' in toml_str
    assert "debug = false" in toml_str


def test_to_toml_nested():
    """Test TOML serialization with nested tables."""
    rns = RNS({"app": {"name": "TestApp", "port": 8000}})
    toml_str = rns.to_toml()
    assert "[app]" in toml_str
    assert 'name = "TestApp"' in toml_str
    assert "port = 8000" in toml_str


def test_to_toml_with_arrays():
    """Test TOML serialization with arrays."""
    rns = RNS({"tags": ["python", "toml", "test"], "ports": [8000, 8001, 8002]})
    toml_str = rns.to_toml()
    assert 'tags = ["python", "toml", "test"]' in toml_str
    assert "ports = [8000, 8001, 8002]" in toml_str


def test_to_toml_boolean():
    """Test TOML serialization with boolean values."""
    rns = RNS({"enabled": True, "disabled": False})
    toml_str = rns.to_toml()
    assert "enabled = true" in toml_str
    assert "disabled = false" in toml_str


def test_to_toml_numbers():
    """Test TOML serialization with different number types."""
    rns = RNS({"integer": 42, "float_val": 3.14})
    toml_str = rns.to_toml()
    assert "integer = 42" in toml_str
    assert "float_val = 3.14" in toml_str


def test_from_toml_basic():
    """Test basic TOML deserialization."""
    toml_str = """
name = "MyApp"
version = "1.0.0"
debug = false
"""
    rns = RNS.from_toml(toml_str)
    assert rns.name == "MyApp"
    assert rns.version == "1.0.0"
    assert rns.debug is False


def test_from_toml_nested():
    """Test TOML deserialization with nested tables."""
    toml_str = """
[app]
name = "TestApp"
port = 8000

[app.database]
host = "localhost"
port = 5432
"""
    rns = RNS.from_toml(toml_str)
    assert rns.app.name == "TestApp"
    assert rns.app.port == 8000
    assert rns.app.database.host == "localhost"
    assert rns.app.database.port == 5432


def test_from_toml_arrays():
    """Test TOML deserialization with arrays."""
    toml_str = """
tags = ["python", "toml"]
ports = [8000, 8001, 8002]
"""
    rns = RNS.from_toml(toml_str)
    assert rns.tags == ["python", "toml"]
    assert rns.ports == [8000, 8001, 8002]


def test_save_toml(tmp_path):
    """Test saving TOML to file."""
    rns = RNS({"app": {"name": "TestApp", "version": "1.0"}})
    filepath = tmp_path / "test.toml"
    rns.save_toml(filepath)

    assert filepath.exists()
    content = filepath.read_text()
    assert "[app]" in content
    assert 'name = "TestApp"' in content


def test_load_toml():
    """Test loading TOML from file."""
    rns = RNS.load_toml(SAMPLE_TOML)
    assert rns.app.name == "MyApp"
    assert rns.app.debug is False
    assert rns.database.host == "localhost"
    assert rns.database.credentials.username == "admin"


def test_load_toml_file_not_found():
    """Test load_toml with non-existent file."""
    with pytest.raises(FileNotFoundError):
        RNS.load_toml("nonexistent.toml")


def test_toml_file_round_trip(tmp_path):
    """Test TOML file round-trip (basic structures only)."""
    original = {
        "app": {"name": "Test", "port": 8000},
        "features": ["auth", "api"],
    }
    rns1 = RNS(original)

    filepath = tmp_path / "round_trip.toml"
    rns1.save_toml(filepath)
    rns2 = RNS.load_toml(filepath)

    assert rns2.app.name == "Test"
    assert rns2.app.port == 8000
    assert rns2.features == ["auth", "api"]


# Edge Cases and Error Handling


def test_json_with_special_characters():
    """Test JSON with special characters in strings."""
    rns = RNS(
        {
            "quote": 'He said "Hello"',
            "newline": "Line1\nLine2",
            "backslash": "path\\to\\file",
        }
    )
    json_str = rns.to_json()
    rns2 = RNS.from_json(json_str)
    assert rns2.quote == 'He said "Hello"'
    assert rns2.newline == "Line1\nLine2"
    assert rns2.backslash == "path\\to\\file"


def test_toml_with_special_characters():
    """Test TOML with special characters in strings."""
    rns = RNS({"quote": 'He said "Hello"', "backslash": "path\\to\\file"})
    toml_str = rns.to_toml()
    assert 'He said \\"Hello\\"' in toml_str or 'He said "Hello"' in toml_str


def test_empty_namespace_serialization():
    """Test serialization of empty namespace."""
    rns = RNS({})

    json_str = rns.to_json()
    assert json_str == "{}" or json_str == "{\n}"

    toml_str = rns.to_toml()
    assert toml_str.strip() == ""


def test_use_raw_key_with_serialization():
    """Test serialization with use_raw_key=True."""
    rns = RNS({"some-key": "value", "another.key": "value2"}, use_raw_key=True)

    json_str = rns.to_json()
    rns2 = RNS.from_json(json_str, use_raw_key=True)

    assert rns2["some-key"] == "value"
    assert rns2["another.key"] == "value2"


def test_deeply_nested_serialization():
    """Test serialization with deeply nested structures."""
    rns = RNS(
        {
            "level1": {
                "level2": {"level3": {"level4": {"level5": {"value": "deep"}}}}
            }
        }
    )

    json_str = rns.to_json()
    rns2 = RNS.from_json(json_str)
    assert rns2.level1.level2.level3.level4.level5.value == "deep"


def test_large_structure_serialization():
    """Test serialization with large structure (100 keys)."""
    data = {f"key{i}": f"value{i}" for i in range(100)}
    rns = RNS(data)

    json_str = rns.to_json()
    rns2 = RNS.from_json(json_str)

    for i in range(100):
        assert getattr(rns2, f"key{i}") == f"value{i}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
