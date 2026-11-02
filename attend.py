import json
import os
from datetime import datetime

# ── 데이터 파일 경로 (스크립트와 같은 폴더에 저장) ──────────────────────────
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attend_data.json")

SEPARATOR = "=" * 52


# ── 파일 입출력 ──────────────────────────────────────────────────────────────

def load_data() -> list[dict]:
    """저장된 출석 데이터를 불러옵니다. 파일이 없으면 빈 리스트를 반환합니다."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(records: list[dict]) -> None:
    """출석 데이터를 JSON 파일에 저장합니다."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


# ── 날짜 유효성 검사 ─────────────────────────────────────────────────────────

def parse_date(date_str: str) -> str | None:
    """
    'YYYY-MM-DD' 또는 'YYYYMMDD' 형식을 받아 'YYYY-MM-DD'로 정규화합니다.
    잘못된 형식이면 None을 반환합니다.
    """
    for fmt in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


# ── 기능 함수들 ──────────────────────────────────────────────────────────────

def check_attendance(records: list[dict]) -> None:
    """출석을 체크하고 기록에 추가합니다."""
    print("\n[ 출석 체크 ]")

    # 날짜 입력
    while True:
        date_input = input("  날짜 입력 (YYYY-MM-DD 또는 오늘=Enter): ").strip()
        if date_input == "":
            date_str = datetime.today().strftime("%Y-%m-%d")
            print(f"  → 오늘 날짜로 설정: {date_str}")
            break
        date_str = parse_date(date_input)
        if date_str:
            break
        print("  ⚠  날짜 형식이 올바르지 않습니다. 예) 2025-06-01")

    # 이름 입력 (쉼표로 여러 명 동시 입력 가능)
    while True:
        name_input = input("  이름 입력 (여러 명은 쉼표로 구분): ").strip()
        names = [n.strip() for n in name_input.split(",") if n.strip()]
        if names:
            break
        print("  ⚠  이름을 한 명 이상 입력해 주세요.")

    added, skipped = [], []
    for name in names:
        # 같은 날짜·이름 중복 방지
        if any(r["date"] == date_str and r["name"] == name for r in records):
            skipped.append(name)
        else:
            records.append({"date": date_str, "name": name})
            added.append(name)

    save_data(records)

    if added:
        print(f"\n  ✅ 출석 완료 [{date_str}]: {', '.join(added)}")
    if skipped:
        print(f"  ⚠  이미 출석 처리됨 (건너뜀): {', '.join(skipped)}")


def show_all(records: list[dict]) -> None:
    """날짜순으로 전체 출석 기록을 출력합니다."""
    print("\n[ 전체 출석 목록 ]")
    if not records:
        print("  기록이 없습니다.")
        return

    sorted_records = sorted(records, key=lambda r: (r["date"], r["name"]))

    # 날짜별로 묶어서 출력
    current_date = None
    for r in sorted_records:
        if r["date"] != current_date:
            current_date = r["date"]
            print(f"\n  📅 {current_date}")
        print(f"      - {r['name']}")

    print(f"\n  총 {len(records)}건")


def search_by_date(records: list[dict]) -> None:
    """특정 날짜의 출석자를 조회합니다."""
    print("\n[ 날짜별 조회 ]")
    while True:
        date_input = input("  조회할 날짜 (YYYY-MM-DD): ").strip()
        date_str = parse_date(date_input)
        if date_str:
            break
        print("  ⚠  날짜 형식이 올바르지 않습니다.")

    result = sorted(
        [r for r in records if r["date"] == date_str],
        key=lambda r: r["name"]
    )

    print(f"\n  📅 {date_str} 출석자 ({len(result)}명)")
    if result:
        for i, r in enumerate(result, 1):
            print(f"    {i:>2}. {r['name']}")
    else:
        print("    해당 날짜의 기록이 없습니다.")


def search_by_name(records: list[dict]) -> None:
    """특정 이름의 출석 이력을 조회합니다."""
    print("\n[ 이름별 조회 ]")
    name = input("  조회할 이름: ").strip()
    if not name:
        print("  ⚠  이름을 입력해 주세요.")
        return

    result = sorted(
        [r for r in records if r["name"] == name],
        key=lambda r: r["date"]
    )

    print(f"\n  👤 {name} 님의 출석 이력 (총 {len(result)}회)")
    if result:
        for i, r in enumerate(result, 1):
            print(f"    {i:>2}. {r['date']}")
    else:
        print("    해당 이름의 기록이 없습니다.")


def delete_record(records: list[dict]) -> None:
    """잘못 입력된 출석 기록을 삭제합니다."""
    print("\n[ 출석 삭제 ]")

    while True:
        date_input = input("  삭제할 날짜 (YYYY-MM-DD): ").strip()
        date_str = parse_date(date_input)
        if date_str:
            break
        print("  ⚠  날짜 형식이 올바르지 않습니다.")

    name = input("  삭제할 이름: ").strip()
    if not name:
        print("  ⚠  이름을 입력해 주세요.")
        return

    target = [r for r in records if r["date"] == date_str and r["name"] == name]
    if not target:
        print(f"  ⚠  [{date_str}] {name} 님의 기록을 찾을 수 없습니다.")
        return

    confirm = input(f"  [{date_str}] {name} 님의 기록을 삭제할까요? (y/N): ").strip().lower()
    if confirm == "y":
        records[:] = [r for r in records if not (r["date"] == date_str and r["name"] == name)]
        save_data(records)
        print("  🗑  삭제 완료.")
    else:
        print("  취소되었습니다.")


def show_stats(records: list[dict]) -> None:
    """인원별 출석 횟수 통계를 출력합니다."""
    print("\n[ 출석 통계 ]")
    if not records:
        print("  기록이 없습니다.")
        return

    # 이름별 카운트
    counter: dict[str, int] = {}
    for r in records:
        counter[r["name"]] = counter.get(r["name"], 0) + 1

    # 출석 횟수 내림차순 → 이름 오름차순 정렬
    sorted_stats = sorted(counter.items(), key=lambda x: (-x[1], x[0]))

    total_sessions = len({r["date"] for r in records})   # 고유 날짜 수
    print(f"  전체 세션 수: {total_sessions}회  |  등록 인원: {len(counter)}명\n")
    print(f"  {'순위':>4}  {'이름':<12}  {'출석':>4}회  {'비율':>6}")
    print("  " + "-" * 36)
    for rank, (name, cnt) in enumerate(sorted_stats, 1):
        ratio = cnt / total_sessions * 100 if total_sessions else 0
        bar = "█" * cnt
        print(f"  {rank:>4}. {name:<12}  {cnt:>4}회  {ratio:>5.1f}%  {bar}")


# ── 메인 루프 ────────────────────────────────────────────────────────────────

def print_menu() -> None:
    print(f"\n{SEPARATOR}")
    print("         📋  스터디 출석부")
    print(SEPARATOR)
    print("  1. 출석 체크")
    print("  2. 전체 목록 보기")
    print("  3. 날짜별 조회")
    print("  4. 이름별 조회")
    print("  5. 출석 삭제")
    print("  6. 출석 통계")
    print("  0. 종료")
    print(SEPARATOR)


def main() -> None:
    records = load_data()
    print("\n  스터디 출석부에 오신 것을 환영합니다! 👋")

    menu_map = {
        "1": check_attendance,
        "2": show_all,
        "3": search_by_date,
        "4": search_by_name,
        "5": delete_record,
        "6": show_stats,
    }

    while True:
        print_menu()
        choice = input("  메뉴 선택 (0~6): ").strip()

        if choice == "0":
            print("\n  프로그램을 종료합니다. 수고하셨습니다! 👏\n")
            break
        elif choice in menu_map:
            menu_map[choice](records)
        else:
            print("  ⚠  0~6 사이의 번호를 입력해 주세요.")


if __name__ == "__main__":
    main()
