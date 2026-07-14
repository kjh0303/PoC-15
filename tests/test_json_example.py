import json

import pytest

from json_example import (
    parse_json_string,
    dump_to_string,
    save_to_file,
    load_from_file,
    dump_with_custom_encoder,
    handle_invalid_json,
)


def test_parse_json_string_returns_expected_dict():
    data = parse_json_string()
    assert data == {
        "name": "홍길동",
        "age": 30,
        "is_admin": False,
        "tags": ["python", "json"],
    }


def test_dump_to_string_roundtrips_and_keeps_korean_readable():
    data = {"name": "홍길동"}
    json_str = dump_to_string(data)
    assert json.loads(json_str) == data
    assert "홍길동" in json_str  # ensure_ascii=False


def test_save_and_load_roundtrip(tmp_path):
    data = {"name": "Alice", "age": 30}
    path = tmp_path / "sample.json"

    save_to_file(data, path)
    loaded = load_from_file(path)

    assert loaded == data


def test_dump_with_custom_encoder_serializes_datetime(capsys):
    dump_with_custom_encoder()
    out = capsys.readouterr().out
    # ISO 8601 날짜 문자열 형태로 직렬화되어 출력에 포함되어야 함
    assert "created_at" in out
    assert "T" in out  # datetime.isoformat() 구분자


def test_handle_invalid_json_reports_error_without_raising(capsys):
    handle_invalid_json()  # 내부에서 JSONDecodeError를 잡아야 하며 예외가 밖으로 나오면 안 됨
    assert "[error]" in capsys.readouterr().out
