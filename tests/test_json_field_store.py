import json

import pytest

from json_field_store import JsonFieldStore


@pytest.fixture
def store(tmp_path):
    return JsonFieldStore(tmp_path / "data.json")


def test_missing_file_starts_empty(tmp_path):
    store = JsonFieldStore(tmp_path / "does_not_exist.json")
    assert store.to_dict() == {}


def test_set_and_get_simple_field(store):
    store.set("name", "Alice")
    assert store.get("name") == "Alice"


def test_get_missing_field_returns_default(store):
    assert store.get("missing") is None
    assert store.get("missing", default="fallback") == "fallback"


def test_set_creates_intermediate_dicts_for_nested_path(store):
    store.set("address.city", "Seoul")
    assert store.to_dict() == {"address": {"city": "Seoul"}}
    assert store.get("address.city") == "Seoul"


def test_set_overwrites_non_dict_intermediate_node(store):
    store.set("address", "not-a-dict", save=False)
    store.set("address.city", "Seoul")
    assert store.get("address") == {"city": "Seoul"}


def test_has(store):
    store.set("age", 30)
    assert store.has("age") is True
    assert store.has("email") is False


def test_delete_existing_field(store):
    store.set("age", 30)
    store.delete("age")
    assert store.has("age") is False


def test_delete_nested_field(store):
    store.set("address.city", "Seoul", save=False)
    store.set("address.zipcode", "06236")
    store.delete("address.zipcode")
    assert store.get("address") == {"city": "Seoul"}


def test_delete_missing_field_is_noop(store):
    store.delete("missing")  # should not raise
    assert store.to_dict() == {}


def test_delete_missing_intermediate_path_is_noop(store):
    store.delete("no.such.path")  # should not raise
    assert store.to_dict() == {}


def test_save_persists_to_disk(tmp_path):
    path = tmp_path / "data.json"
    store = JsonFieldStore(path)
    store.set("name", "Alice")

    with path.open(encoding="utf-8") as f:
        assert json.load(f) == {"name": "Alice"}


def test_set_without_save_defers_write(tmp_path):
    path = tmp_path / "data.json"
    store = JsonFieldStore(path)
    store.set("name", "Alice", save=False)

    assert not path.exists()
    store.save()
    assert path.exists()


def test_reload_picks_up_external_changes(tmp_path):
    path = tmp_path / "data.json"
    store_a = JsonFieldStore(path)
    store_a.set("name", "Alice")

    store_b = JsonFieldStore(path)
    store_b.set("name", "Bob")  # writes over store_a's file

    store_a.reload()
    assert store_a.get("name") == "Bob"


def test_second_instance_loads_previously_saved_data(tmp_path):
    path = tmp_path / "data.json"
    JsonFieldStore(path).set("name", "Alice")

    reloaded = JsonFieldStore(path)
    assert reloaded.get("name") == "Alice"
