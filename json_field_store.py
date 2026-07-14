"""
JSON 파일의 개별 필드를 read / write 하는 인터페이스.
점(.)으로 구분된 경로(예: "user.address.city")로 중첩 필드에 접근 가능.
"""

import json
from pathlib import Path

_MISSING = object()


class JsonFieldStore:
    """JSON 파일 하나를 감싸서 필드 단위로 읽고 쓰는 클래스"""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._data = self._load()

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save(self) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def reload(self) -> None:
        """디스크의 최신 내용으로 메모리 상태를 갱신"""
        self._data = self._load()

    def get(self, field_path: str, default=None):
        """'a.b.c' 형태의 경로로 중첩 필드 값을 조회"""
        node = self._data
        for key in field_path.split("."):
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    def set(self, field_path: str, value, save: bool = True) -> None:
        """'a.b.c' 형태의 경로로 중첩 필드 값을 설정. 중간 dict는 자동 생성"""
        keys = field_path.split(".")
        node = self._data
        for key in keys[:-1]:
            if not isinstance(node.get(key), dict):
                node[key] = {}
            node = node[key]
        node[keys[-1]] = value
        if save:
            self.save()

    def delete(self, field_path: str, save: bool = True) -> None:
        """필드를 삭제. 존재하지 않으면 조용히 무시"""
        keys = field_path.split(".")
        node = self._data
        for key in keys[:-1]:
            if not isinstance(node, dict) or key not in node:
                return
            node = node[key]
        node.pop(keys[-1], _MISSING)
        if save:
            self.save()

    def has(self, field_path: str) -> bool:
        return self.get(field_path, _MISSING) is not _MISSING

    def to_dict(self) -> dict:
        return self._data


if __name__ == "__main__":
    store = JsonFieldStore("sample.json")

    # write: 필드 읽기
    print("age:", store.get("age"))
    print("존재하지 않는 필드:", store.get("email", default="없음"))

    # write: 새 필드 추가 / 중첩 필드 생성
    store.set("age", 31)
    store.set("address.city", "서울")
    store.set("address.zipcode", "06236")

    # write: 필드 존재 여부 확인 후 삭제
    print("address 존재?:", store.has("address.city"))
    store.delete("is_admin")

    print("최종 데이터:", json.dumps(store.to_dict(), ensure_ascii=False, indent=2))
