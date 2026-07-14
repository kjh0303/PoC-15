"""
Python 표준 라이브러리 json 모듈 사용 예시
- json.loads / json.dumps : 문자열 <-> 파이썬 객체
- json.load / json.dump   : 파일 <-> 파이썬 객체
"""

import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("sample.json")


def parse_json_string():
    """JSON 문자열을 파이썬 객체로 파싱 (json.loads)"""
    json_str = '{"name": "홍길동", "age": 30, "is_admin": false, "tags": ["python", "json"]}'
    data = json.loads(json_str)
    print("[loads] 파싱 결과:", data)
    print("[loads] 타입:", type(data))
    return data


def dump_to_string(data):
    """파이썬 객체를 JSON 문자열로 변환 (json.dumps)"""
    # ensure_ascii=False -> 한글이 유니코드 이스케이프 없이 그대로 출력
    # indent=2 -> 보기 좋게 들여쓰기
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    print("[dumps] 결과:\n", json_str)
    return json_str


def save_to_file(data, path: Path):
    """파이썬 객체를 JSON 파일로 저장 (json.dump)"""
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[dump] 파일 저장 완료: {path.resolve()}")


def load_from_file(path: Path):
    """JSON 파일을 읽어서 파이썬 객체로 로드 (json.load)"""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    print("[load] 파일에서 읽은 데이터:", data)
    return data


class DateTimeEncoder(json.JSONEncoder):
    """datetime 등 기본적으로 직렬화 안 되는 타입을 처리하는 커스텀 인코더"""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def dump_with_custom_encoder():
    """json 모듈은 datetime, set 등을 기본 지원하지 않으므로 커스텀 인코더 필요"""
    data = {"created_at": datetime.now(), "score": 95.5}
    json_str = json.dumps(data, cls=DateTimeEncoder, ensure_ascii=False, indent=2)
    print("[custom encoder] 결과:\n", json_str)


def handle_invalid_json():
    """잘못된 JSON 파싱 시 예외 처리 (json.JSONDecodeError)"""
    bad_json = '{"name": "홍길동", }'  # trailing comma -> 문법 오류
    try:
        json.loads(bad_json)
    except json.JSONDecodeError as e:
        print(f"[error] JSON 파싱 실패: {e}")


if __name__ == "__main__":
    data = parse_json_string()
    dump_to_string(data)
    save_to_file(data, DATA_FILE)
    load_from_file(DATA_FILE)
    dump_with_custom_encoder()
    handle_invalid_json()
