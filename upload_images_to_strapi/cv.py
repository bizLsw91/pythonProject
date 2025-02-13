import json

# JSON 파일 로드
with open('imageId-fName-Retry.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 한글로 디코딩된 JSON 파일 저장
with open('imageId-fName-Retry.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=2)