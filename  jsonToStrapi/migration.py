import os
import json
import requests
from pathlib import Path

STRAPI_URL = "http://localhost:1337"
FIREBASE_STORAGE_BUCKET = "store-892ea.firebasestorage.app"
class StrapiMigrator:
    def __init__(self):
        self.base_url = STRAPI_URL
        self.headers = {
            "Content-Type": "application/json"
        }

    def upload_image(self, image_path: str) -> int:
        """Firebase Storage 또는 로컬 스토리지 선택 업로드"""
        file_name = Path(image_path).name

        # Firebase Storage 업로드 (우선시)
        if FIREBASE_STORAGE_BUCKET:
            from firebase_admin import storage
            bucket = storage.bucket(FIREBASE_STORAGE_BUCKET)
            blob = bucket.blob(f"portfolio/{file_name}")
            blob.upload_from_filename(image_path)
            return blob.public_url  # Firebase URL 반환
        else:
            # Strapi Media Library 업로드
            with open(image_path, 'rb') as f:
                files = {'files': (file_name, f)}
                response = requests.post(
                    f"{self.base_url}/api/upload",
                    files=files,
                    headers={"Authorization": self.headers["Authorization"]}
                )
            return response.json()[0]['id']

    def create_portfolio_entry(self, data: dict):
        """중첩 JSON 구조 처리"""
        transformed = {
            "data": {
                "title": {"ko": data["title"], "en": data["title_en"]},
                "institution": data["institution"],
                "year": data["year"],
                "outline": {
                    "dateText": data["outline"]["dateText"],
                    "startDate": data["outline"]["startDate"],
                    "location": data["outline"]["location"],
                    "topics": data["outline"]["topic"]
                },
                "images": [self.upload_image(img) for img in data["images"]]
            }
        }
        response = requests.post(
            f"{self.base_url}/api/portfolios",
            json=transformed,
            headers=self.headers
        )
        return response.json()

# 실행 예제
if __name__ == "__main__":
    migrator = StrapiMigrator()

    with open("portfolio_data.json", "r", encoding="utf-8") as f:
        portfolio_data = json.load(f)

    for item in portfolio_data:
        try:
            result = migrator.create_portfolio_entry(item)
            print(f"✅ {item['title']} 이관 성공")
        except Exception as e:
            print(f"🚨 {item['title']} 오류: {str(e)}")
