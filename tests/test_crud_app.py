import pytest

from json_field_store import JsonFieldStore
from crud_app import (
    create_record,
    list_records,
    read_record,
    update_record,
    delete_record,
    main,
)


@pytest.fixture
def store(tmp_path):
    return JsonFieldStore(tmp_path / "db.json")


def feed_inputs(monkeypatch, values):
    """input()이 호출될 때마다 values를 순서대로 반환하도록 patch"""
    iterator = iter(values)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(iterator))


def test_create_record_assigns_id_1_on_first_record(store, monkeypatch):
    feed_inputs(monkeypatch, ["Alice", "30", "a@a.com"])
    create_record(store)

    assert store.get("records.1") == {"name": "Alice", "age": "30", "email": "a@a.com"}
    assert store.get("next_id") == 2


def test_create_record_ids_increment_sequentially(store, monkeypatch):
    feed_inputs(monkeypatch, ["Alice", "30", "a@a.com"])
    create_record(store)
    feed_inputs(monkeypatch, ["Bob", "25", "b@b.com"])
    create_record(store)

    assert store.get("records.1.name") == "Alice"
    assert store.get("records.2.name") == "Bob"
    assert store.get("next_id") == 3


def test_list_records_empty_message(store, capsys):
    list_records(store)
    assert "없습니다" in capsys.readouterr().out


def test_list_records_prints_each_record(store, capsys):
    store.set("records.1", {"name": "Alice", "age": "30", "email": "a@a.com"})
    list_records(store)
    out = capsys.readouterr().out
    assert "id=1" in out
    assert "Alice" in out


def test_read_record_found(store, monkeypatch, capsys):
    store.set("records.1", {"name": "Alice", "age": "30", "email": "a@a.com"})
    feed_inputs(monkeypatch, ["1"])
    read_record(store)
    assert "Alice" in capsys.readouterr().out


def test_read_record_not_found(store, monkeypatch, capsys):
    feed_inputs(monkeypatch, ["999"])
    read_record(store)
    assert "오류" in capsys.readouterr().out


def test_update_record_blank_input_keeps_existing_value(store, monkeypatch):
    store.set("records.1", {"name": "Alice", "age": "30", "email": "a@a.com"})
    feed_inputs(monkeypatch, ["1", "", "", ""])
    update_record(store)

    assert store.get("records.1") == {"name": "Alice", "age": "30", "email": "a@a.com"}


def test_update_record_overwrites_given_fields_only(store, monkeypatch):
    store.set("records.1", {"name": "Alice", "age": "30", "email": "a@a.com"})
    feed_inputs(monkeypatch, ["1", "", "31", ""])
    update_record(store)

    assert store.get("records.1") == {"name": "Alice", "age": "31", "email": "a@a.com"}


def test_update_record_nonexistent_id(store, monkeypatch, capsys):
    feed_inputs(monkeypatch, ["999"])
    update_record(store)
    assert "오류" in capsys.readouterr().out


def test_delete_record_removes_entry(store, monkeypatch):
    store.set("records.1", {"name": "Alice", "age": "30", "email": "a@a.com"})
    feed_inputs(monkeypatch, ["1"])
    delete_record(store)

    assert store.has("records.1") is False


def test_delete_record_nonexistent_id(store, monkeypatch, capsys):
    feed_inputs(monkeypatch, ["999"])
    delete_record(store)
    assert "오류" in capsys.readouterr().out


def test_main_end_to_end_session(tmp_path, monkeypatch, capsys):
    db_path = tmp_path / "db.json"
    monkeypatch.setattr("crud_app.DB_FILE", str(db_path))

    session = [
        "1", "Alice", "30", "a@a.com",   # create id=1
        "1", "Bob", "25", "b@b.com",     # create id=2
        "4", "2", "", "26", "",          # update id=2's age
        "5", "1",                        # delete id=1
        "2",                             # list
        "0",                             # exit
    ]
    feed_inputs(monkeypatch, session)
    main()

    final = JsonFieldStore(db_path)
    assert final.has("records.1") is False
    assert final.get("records.2") == {"name": "Bob", "age": "26", "email": "b@b.com"}
