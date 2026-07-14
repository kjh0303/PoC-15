# Correctness TC (정확성 검증 테스트 케이스)

- **검증 목적**: 구현된 코드가 요구사항대로 정확히 동작하는지, 다양한 입력/조건에서 기대한 결과를 올바르게 반환하는지 확인
- **대상 코드**: `json_example.py`, `json_field_store.py`(`JsonFieldStore`), `crud_app.py`
- **자동화**: 모든 TC는 `tests/test_correctness.py`에 동일한 TC ID로 매핑되어 pytest로 실행/검증 가능

## 1. json_example.py — JSON 파싱/저장 (표준 json 모듈)

| TC ID | 테스트 목적 | 입력 | 기대 결과 |
|---|---|---|---|
| JX-01 | JSON 문자열 → 파이썬 객체 파싱 정확성 | `parse_json_string()`이 사용하는 고정 JSON 문자열 | dict, list, bool, int, str 타입이 각각 원래 값 그대로 파싱됨 |
| JX-02 | 파이썬 객체 → JSON 문자열 직렬화 정확성 | 한글 포함 dict `{"name": "홍길동"}` | `json.loads(결과)`가 원본과 동일 + 결과 문자열에 한글이 유니코드 이스케이프 없이 그대로 포함 |
| JX-03 | 파일 저장 → 로드 round-trip 정확성 | 임의 dict `{"name": "Alice", "age": 30}` | `save_to_file` 후 `load_from_file`로 읽은 값이 원본과 완전히 동일 |
| JX-04 | datetime 등 비표준 타입 커스텀 인코딩 | `datetime.now()`를 포함한 dict | 예외 없이 직렬화되며 결과에 ISO 8601 형식(`T` 구분자) 문자열로 포함됨 |
| JX-05 | 잘못된 JSON 입력 예외 처리 정확성 | trailing comma가 있는 잘못된 JSON 문자열 | `JSONDecodeError`가 내부에서 처리되어 프로그램이 중단되지 않고 에러 메시지 출력 |

## 2. json_field_store.py — JsonFieldStore

| TC ID | 테스트 목적 | 입력 | 기대 결과 |
|---|---|---|---|
| JF-01 | 존재하지 않는 파일 초기화 정확성 | 존재하지 않는 경로 | 예외 없이 빈 dict(`{}`) 상태로 초기화 |
| JF-02 | 단순 필드 set/get 정확성 | `set("age", 30)` 후 `get("age")` | `30` 반환 |
| JF-03 | 중첩 경로 set 시 중간 dict 자동 생성 | `set("address.city", "Seoul")` | `{"address": {"city": "Seoul"}}` 구조 생성, `get("address.city")` == `"Seoul"` |
| JF-04 | 존재하지 않는 필드 조회 시 default 반환 | `get("missing")`, `get("missing", default="x")` | 각각 `None`, `"x"` |
| JF-05 | non-dict 중간 노드 덮어쓰기 정확성 | `set("address", "not-a-dict")` 후 `set("address.city", "Seoul")` | 문자열이 dict로 대체되어 `{"city": "Seoul"}` 저장 |
| JF-06 | has() 존재 여부 판정 정확성 | 필드 설정 전/후 `has()` 호출 | 설정 전 `False`, 설정 후 `True` |
| JF-07 | delete() 대상 필드만 정확히 제거 | `address.city`, `address.zipcode` 설정 후 `zipcode`만 삭제 | `zipcode`는 제거, `city`는 그대로 유지 |
| JF-08 | 존재하지 않는 경로 삭제 시 무영향 | `delete("no.such.path")` | 예외 없음, 기존 데이터 변경 없음 |
| JF-09 | save() 디스크 반영 정확성 | `set("name", "Alice")` | 파일을 직접 `json.load`로 읽었을 때 `{"name": "Alice"}`와 완전히 일치 |
| JF-10 | reload() 외부 변경 반영 정확성 | 인스턴스A로 저장 후, 인스턴스B가 같은 파일을 덮어씀, 인스턴스A에서 `reload()` | A가 B가 저장한 최신 값을 정확히 반영 |

## 3. crud_app.py — CRUD 콘솔 앱

| TC ID | 테스트 목적 | 입력 | 기대 결과 |
|---|---|---|---|
| CA-01 | 레코드 생성 시 id 자동 채번 정확성 | 최초 레코드 생성 (name/age/email 입력) | `records.1`에 입력값 그대로 저장, `next_id`는 `2`로 증가 |
| CA-02 | 다중 레코드 생성 시 id 순차 증가 정확성 | 레코드 2건 연속 생성 | 각각 `id=1`, `id=2`로 저장되며 값이 서로 섞이지 않음 |
| CA-03 | 레코드 없을 때 목록 조회 안내 메시지 | 빈 저장소에서 `list_records()` | "없습니다" 문구 출력, 예외 없음 |
| CA-04 | 저장된 레코드 목록 조회 정확성 | 레코드 1건 저장 후 `list_records()` | 출력에 해당 id와 필드 값이 정확히 포함 |
| CA-05 | 존재하는 id 단건 조회 정확성 | 저장된 id로 `read_record()` | 해당 레코드 값이 정확히 출력 |
| CA-06 | 존재하지 않는 id 단건 조회 시 오류 처리 | 존재하지 않는 id로 `read_record()` | "[오류]" 메시지 출력, 예외 없음 |
| CA-07 | 수정 시 빈 입력은 기존 값 유지 | 모든 필드에 빈 입력(Enter)으로 `update_record()` | 레코드 값이 변경 전과 완전히 동일 |
| CA-08 | 수정 시 지정 필드만 정확히 갱신 | `age` 필드에만 새 값 입력 | `age`만 변경되고 `name`/`email`은 그대로 유지 |
| CA-09 | 존재하지 않는 id 수정 시 오류 처리 | 존재하지 않는 id로 `update_record()` | "[오류]" 메시지 출력, 데이터 변경 없음 |
| CA-10 | 삭제 시 지정 id만 정확히 제거 | id 2건 중 1건만 삭제 | 삭제 대상만 제거되고 나머지 레코드는 영향받지 않음 |
| CA-11 | 존재하지 않는 id 삭제 시 오류 처리 | 존재하지 않는 id로 `delete_record()` | "[오류]" 메시지 출력, 데이터 변경 없음 |
| CA-12 | 전체 시나리오(생성→조회→수정→삭제) End-to-End 정확성 | `main()`에 생성 2건 → 수정 1건 → 삭제 1건 순서로 입력 | 최종 저장소 상태가 기대한 레코드 구성과 정확히 일치 |
