import os
import json
from difflib import SequenceMatcher

# 1. 카테고리 매핑 및 기본 경로 설정
CATEGORY_MAP = {
    "pubGov": "1. 정부,공공기관(15-24)",
    "performance": "2. 문화 공연",
    "event": "3. 기업 행사"
}
# 실제 경로로 수정 필요
BASE_DIR = "D:\컬쳐마케팅컴퍼니\이미지파일\PortfolioImages_webp_optimized"

# 2. 유사도 비교 함수
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# 3. 이미지 경로 찾기 함수
def find_image_paths(category, year, title):
    # 카테고리 폴더 확인
    category_dir = os.path.join(BASE_DIR, CATEGORY_MAP.get(category, ""))
    if not os.path.exists(category_dir):
        return None, "Category folder not found"

    # 연도 폴더 탐색 (예: "2024년")
    year_dir_pattern = f"{year}년"
    year_dirs = [d for d in os.listdir(category_dir)
                 if os.path.isdir(os.path.join(category_dir, d))
                 and year_dir_pattern in d]

    if not year_dirs:
        return None, "Year folder not found"

    # 연도 폴더 내 행사 폴더 탐색
    event_dirs = []
    for y_dir in year_dirs:
        full_year_path = os.path.join(category_dir, y_dir)
        event_dirs.extend([(os.path.join(full_year_path, ed), ed)
                           for ed in os.listdir(full_year_path)
                           if os.path.isdir(os.path.join(full_year_path, ed))])

    # 유사도 기반 매칭
    best_match = None
    highest_score = 0

    for ed_path, ed_name in event_dirs:
        score = similar(title, ed_name)
        if score > highest_score:
            highest_score = score
            best_match = ed_path

    # 임계값 설정 (0.6 이상만 유사한 것으로 판단)
    if not best_match or highest_score < 0.6:
        return None, "No similar folder found"

    # 이미지 파일 수집
    image_exts = ('.webp')
    images = [os.path.join(best_match, f)
              for f in os.listdir(best_match)
              if f.lower().endswith(image_exts)]

    return images, None

# 4. JSON 처리 로직
def process_json(data):
    found_issues = []

    for item in data:
        category = item.get('category')
        year = item.get('year')
        title = item.get('title')

        if not all([category, year, title]):
            continue

        images, error = find_image_paths(category, year, title)

        if images:
            item['images'] = images
        else:
            found_issues.append(f"{category}/{year}/{title}: {error}")

    # 결과 출력
    if found_issues:
        print("⚠️ 다음 항목에서 문제 발생:")
        print("\n".join(found_issues))

    return data

# 5. 실행 예시
if __name__ == "__main__":
    # JSON 데이터 로드 (실제 데이터 경로로 변경 필요)
    with open('input.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    processed_data = process_json(data)

    # 처리된 데이터 저장
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)