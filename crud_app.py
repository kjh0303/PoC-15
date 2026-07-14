"""
json_field_store.JsonFieldStore를 저장소로 사용하는 CRUD 콘솔 애플리케이션.
"사람(person)" 레코드를 JSON 파일(db.json)에 등록/조회/수정/삭제한다.

데이터 구조 (db.json):
{
  "next_id": 3,
  "records": {
    "1": {"name": "...", "age": 0, "email": "..."},
    "2": {...}
  }
}
"""

from json_field_store import JsonFieldStore

DB_FILE = "db.json"
FIELDS = ["name", "age", "email"]


def create_record(store: JsonFieldStore) -> None:
    record_id = store.get("next_id", 1)

    record = {}
    for field in FIELDS:
        record[field] = input(f"{field}: ").strip()

    store.set(f"records.{record_id}", record, save=False)
    store.set("next_id", record_id + 1)
    print(f"[생성 완료] id={record_id}")


def list_records(store: JsonFieldStore) -> None:
    records = store.get("records", {})
    if not records:
        print("등록된 레코드가 없습니다.")
        return
    for record_id, record in records.items():
        print(f"- id={record_id}: {record}")


def read_record(store: JsonFieldStore) -> None:
    record_id = input("조회할 id: ").strip()
    record = store.get(f"records.{record_id}")
    if record is None:
        print(f"[오류] id={record_id} 레코드를 찾을 수 없습니다.")
        return
    print(f"id={record_id}: {record}")


def update_record(store: JsonFieldStore) -> None:
    record_id = input("수정할 id: ").strip()
    if not store.has(f"records.{record_id}"):
        print(f"[오류] id={record_id} 레코드를 찾을 수 없습니다.")
        return

    for field in FIELDS:
        current = store.get(f"records.{record_id}.{field}")
        new_value = input(f"{field} (현재: {current}, 그대로 두려면 Enter): ").strip()
        if new_value:
            store.set(f"records.{record_id}.{field}", new_value, save=False)

    store.save()
    print(f"[수정 완료] id={record_id}")


def delete_record(store: JsonFieldStore) -> None:
    record_id = input("삭제할 id: ").strip()
    if not store.has(f"records.{record_id}"):
        print(f"[오류] id={record_id} 레코드를 찾을 수 없습니다.")
        return
    store.delete(f"records.{record_id}")
    print(f"[삭제 완료] id={record_id}")


MENU = """
===== JSON CRUD =====
1. 등록 (Create)
2. 목록 조회 (List)
3. 단건 조회 (Read)
4. 수정 (Update)
5. 삭제 (Delete)
0. 종료
======================
"""

ACTIONS = {
    "1": create_record,
    "2": list_records,
    "3": read_record,
    "4": update_record,
    "5": delete_record,
}


def main() -> None:
    store = JsonFieldStore(DB_FILE)
    while True:
        print(MENU)
        choice = input("선택: ").strip()
        if choice == "0":
            print("종료합니다.")
            break
        action = ACTIONS.get(choice)
        if action is None:
            print("[오류] 잘못된 선택입니다.")
            continue
        action(store)


if __name__ == "__main__":
    main()
