"""
Correctness TC (정확성 검증 테스트).
각 테스트는 TC_correctness.md의 동일 TC ID에 대응한다.
"""

import json
from datetime import datetime

import pytest

from json_example import (
    parse_json_string,
    dump_to_string,
    save_to_file,
    load_from_file,
    dump_with_custom_encoder,
    handle_invalid_json,
)
from json_field_store import JsonFieldStore
from crud_app import (
    create_record,
    list_records,
    read_record,
    update_record,
    delete_record,
    main,
)


def feed_inputs(monkeypatch, values):
    iterator = iter(values)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(iterator))


# ---------------------------------------------------------------------------
# json_example.py
# ---------------------------------------------------------------------------

def test_JX_01_parse_json_string_matches_expected_types_and_values():
    data = parse_json_string()
    assert data == {
        "name": "홍길동",
        "age": 30,
        "is_admin": False,
        "tags": ["python", "json"],
    }
    assert isinstance(data["age"], int)
    assert isinstance(data["is_admin"], bool)
    assert isinstance(data["tags"], list)


def test_JX_02_dump_to_string_is_valid_json_and_keeps_korean_readable():
    data = {"name": "홍길동"}
    json_str = dump_to_string(data)
    assert json.loads(json_str) == data
    assert "홍길동" in json_str
    assert "\\u" not in json_str


def test_JX_03_save_and_load_roundtrip_is_exact(tmp_path):
    data = {"name": "Alice", "age": 30}
    path = tmp_path / "sample.json"

    save_to_file(data, path)
    loaded = load_from_file(path)

    assert loaded == data


def test_JX_04_custom_encoder_serializes_datetime_as_iso8601(capsys):
    dump_with_custom_encoder()
    out = capsys.readouterr().out
    assert "created_at" in out
    assert "T" in out  # datetime.isoformat() 구분자


def test_JX_05_invalid_json_is_caught_and_reported(capsys):
    handle_invalid_json()
    out = capsys.readouterr().out
    assert "[error]" in out


# ---------------------------------------------------------------------------
# json_field_store.py — JsonFieldStore
# ---------------------------------------------------------------------------

def test_JF_01_missing_file_initializes_empty(tmp_path):
    store = JsonFieldStore(tmp_path / "missing.json")
    assert store.to_dict() == {}


def test_JF_02_simple_set_get_is_exact(tmp_path):
    store = JsonFieldStore(tmp_path / "data.json")
    store.set("age", 30)
    assert store.get("age") == 30


def test_JF_03_nested_set_creates_intermediate_dicts(tmp_path):
    store = JsonFieldStore(tmp_path / "data.json")
    store.set("address.city", "Seoul")
    assert store.to_dict() == {"address": {"city": "Seoul"}}
    assert store.get("address.city") == "Seoul"


def test_JF_04_missing_field_returns_default(tmp_path):
    store = JsonFieldStore(tmp_path / "data.json")
    assert store.get("missing") is None
    assert store.get("missing", default="x") == "x"


def test_JF_05_set_overwrites_non_dict_intermediate_node(tmp_path):
    store = JsonFieldStore(tmp_path / "data.json")
    store.set("address", "not-a-dict", save=False)
    store.set("address.city", "Seoul")
    assert store.get("address") == {"city": "Seoul"}


def test_JF_06_has_reflects_presence_before_and_after_set(tmp_path):
    store = JsonFieldStore(tmp_path / "data.json")
    assert store.has("age") is False
    store.set("age", 30)
    assert store.has("age") is True


def test_JF_07_delete_removes_only_target_field(tmp_path):
    store = JsonFieldStore(tmp_path / "data.json")
    store.set("address.city", "Seoul", save=False)
    store.set("address.zipcode", "06236")

    store.delete("address.zipcode")

    assert store.has("address.zipcode") is False
    assert store.get("address.city") == "Seoul"


def test_JF_08_delete_missing_path_is_noop(tmp_path):
    store = JsonFieldStore(tmp_path / "data.json")
    store.set("name", "Alice")

    store.delete("no.such.path")

    assert store.to_dict() == {"name": "Alice"}


def test_JF_09_save_writes_exact_content_to_disk(tmp_path):
    path = tmp_path / "data.json"
    store = JsonFieldStore(path)
    store.set("name", "Alice")

    with path.open(encoding="utf-8") as f:
        assert json.load(f) == {"name": "Alice"}


def test_JF_10_reload_reflects_latest_external_write(tmp_path):
    path = tmp_path / "data.json"
    store_a = JsonFieldStore(path)
    store_a.set("name", "Alice")

    store_b = JsonFieldStore(path)
    store_b.set("name", "Bob")

    store_a.reload()
    assert store_a.get("name") == "Bob"


# ---------------------------------------------------------------------------
# crud_app.py
# ---------------------------------------------------------------------------

@pytest.fixture
def store(tmp_path):
    return JsonFieldStore(tmp_path / "db.json")


def test_CA_01_create_assigns_id_1_and_stores_exact_values(store, monkeypatch):
    feed_inputs(monkeypatch, ["Alice", "30", "a@a.com"])
    create_record(store)

    assert store.get("records.1") == {"name": "Alice", "age": "30", "email": "a@a.com"}
    assert store.get("next_id") == 2


def test_CA_02_sequential_creates_get_sequential_ids_without_mixing_values(store, monkeypatch):
    feed_inputs(monkeypatch, ["Alice", "30", "a@a.com"])
    create_record(store)
    feed_inputs(monkeypatch, ["Bob", "25", "b@b.com"])
    create_record(store)

    assert store.get("records.1.name") == "Alice"
    assert store.get("records.2.name") == "Bob"


def test_CA_03_list_records_on_empty_store_shows_notice(store, capsys):
    list_records(store)
    assert "없습니다" in capsys.readouterr().out


def test_CA_04_list_records_prints_stored_record_accurately(store, capsys):
    store.set("records.1", {"name": "Alice", "age": "30", "email": "a@a.com"})
    list_records(store)
    out = capsys.readouterr().out
    assert "id=1" in out
    assert "Alice" in out


def test_CA_05_read_existing_id_returns_exact_record(store, monkeypatch, capsys):
    store.set("records.1", {"name": "Alice", "age": "30", "email": "a@a.com"})
    feed_inputs(monkeypatch, ["1"])
    read_record(store)
    assert "Alice" in capsys.readouterr().out


def test_CA_06_read_nonexistent_id_reports_error(store, monkeypatch, capsys):
    feed_inputs(monkeypatch, ["999"])
    read_record(store)
    assert "[오류]" in capsys.readouterr().out


def test_CA_07_update_blank_inputs_keep_values_unchanged(store, monkeypatch):
    original = {"name": "Alice", "age": "30", "email": "a@a.com"}
    store.set("records.1", dict(original))

    feed_inputs(monkeypatch, ["1", "", "", ""])
    update_record(store)

    assert store.get("records.1") == original


def test_CA_08_update_changes_only_targeted_field(store, monkeypatch):
    store.set("records.1", {"name": "Alice", "age": "30", "email": "a@a.com"})

    feed_inputs(monkeypatch, ["1", "", "31", ""])
    update_record(store)

    assert store.get("records.1") == {"name": "Alice", "age": "31", "email": "a@a.com"}


def test_CA_09_update_nonexistent_id_reports_error_and_no_change(store, monkeypatch):
    feed_inputs(monkeypatch, ["999"])
    update_record(store)
    assert store.to_dict() == {}


def test_CA_10_delete_removes_only_target_record(store, monkeypatch):
    store.set("records.1", {"name": "Alice", "age": "30", "email": "a@a.com"}, save=False)
    store.set("records.2", {"name": "Bob", "age": "25", "email": "b@b.com"})

    feed_inputs(monkeypatch, ["1"])
    delete_record(store)

    assert store.has("records.1") is False
    assert store.get("records.2.name") == "Bob"


def test_CA_11_delete_nonexistent_id_reports_error_and_no_change(store, monkeypatch):
    store.set("records.1", {"name": "Alice", "age": "30", "email": "a@a.com"})

    feed_inputs(monkeypatch, ["999"])
    delete_record(store)

    assert store.get("records.1") == {"name": "Alice", "age": "30", "email": "a@a.com"}


def test_CA_12_end_to_end_scenario_produces_exact_final_state(tmp_path, monkeypatch):
    db_path = tmp_path / "db.json"
    monkeypatch.setattr("crud_app.DB_FILE", str(db_path))

    session = [
        "1", "Alice", "30", "a@a.com",   # create id=1
        "1", "Bob", "25", "b@b.com",     # create id=2
        "4", "2", "", "26", "",          # update id=2's age only
        "5", "1",                        # delete id=1
        "2",                              # list
        "0",                              # exit
    ]
    feed_inputs(monkeypatch, session)
    main()

    final = JsonFieldStore(db_path)
    assert final.has("records.1") is False
    assert final.get("records.2") == {"name": "Bob", "age": "26", "email": "b@b.com"}
    assert final.get("next_id") == 3
