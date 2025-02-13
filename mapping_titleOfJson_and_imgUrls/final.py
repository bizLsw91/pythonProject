import json
import os
import re

def load_json_with_validation(file_path):
    """JSON 파일 검증 및 로드"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON 구문 오류 발생: {e}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 일반적인 오류 패턴 수정
            content = content.replace("'", '"')  # 작은따옴표 -> 큰따옴표
            content = content.replace("\\", "\\\\")  # 역슬래시 이스케이프
            content = re.sub(r',\s*}', '}', content)  # 트레일링 콤마 제거
            content = re.sub(r',\s*]', ']', content)
            return json.loads(content)

# 매핑 데이터 로드 (자동 수정 시도)
try:
    mapping = load_json_with_validation("imageId-fName.json")
except Exception as e:
    print(f"❌ 치명적 오류: {str(e)}")
    exit(1)

# output.json 처리
with open('output.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 이미지 경로 치환 로직
for item in data:
    if 'images' in item:
        item['images'] = [
            mapping.get(os.path.basename(img_path), img_path)
            for img_path in item['images']
        ]

# 결과 저장
with open('output_processed.json', 'w', encoding='utf-8', errors='ignore') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ 처리 완료: output_processed.json")
