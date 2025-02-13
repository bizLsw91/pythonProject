import os
import requests
import json
from typing import List, Optional, Dict

STRAPI_HOST = "https://cmcstrapi-production.up.railway.app"
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiaWF0IjoxNzM5MTYyMDE4LCJleHAiOjE3NDE3NTQwMTh9.GN_jXoAO1D292NYd2cu8Yphk54POrUuYgXZnVVDnW0g"
LOCAL_FOLDER_T = "D:\컬쳐마케팅컴퍼니\이미지파일\PortfolioImages_webp_optimized"
OUTPUT_JSON_PATH = "../mapping_titleOfJson_and_imgUrls/imageId-fName.json"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

with open(OUTPUT_JSON_PATH, 'r', encoding='utf-8') as f:
    existing_data = json.load(f)


def get_folders(parent_id: Optional[int] = None) -> List[Dict]:
    """스트라피 폴더 조회 함수"""
    params = {"filters[$and][0][parent][id]": parent_id} if parent_id else {"filters[$and][0][parent][id][$null]": "true"}
    response = requests.get(f"{STRAPI_HOST}/upload/folders", params=params, headers=headers)
    response.raise_for_status()
    return response.json()['data']


def find_target_folder_id(path_components: List[str]) -> Optional[int]:
    """경로 기반으로 폴더 ID 탐색"""
    def _find(parent_id: Optional[int], components: List[str]) -> Optional[int]:
        if not components:
            return parent_id
        for folder in get_folders(parent_id):
            if folder['name'] == components[0]:
                return _find(folder['id'], components[1:])
        return None
    return _find(None, path_components)

def upload_webp(file_path: str, folder_id: int) -> str:
    """WEBP 파일 업로드"""
    file_name = os.path.basename(file_path)
    print("file_name = ", file_name)
    print("folder_id = ", folder_id)
    with open(file_path, 'rb') as f:
        response = requests.post(
            f"{STRAPI_HOST}/upload",
            files={'files': (file_name, f, 'image/webp')},
            data={'fileInfo': json.dumps({"name": file_name, "folder": folder_id})},
            headers=headers
        )

    response.raise_for_status()
    return response.json()[0]['id']

def main():
    uploaded_files = set(existing_data.keys())
    upd_cnt = len(uploaded_files)
    print("기존 업로드한 파일개수: = ", upd_cnt)
    result = {}
    upload_fail_files = []
    fail_cnt = 0

    # WEBP 파일 수집
    for root, _, files in os.walk(LOCAL_FOLDER_T):
        for file in files:
            if not file.lower().endswith('.webp'):
                continue

            if file in uploaded_files:
                uploaded_files.remove(file)
            else:
                full_path = os.path.join(root, file)
                print("누락 파일 full_path = ", full_path)
                rel_path = 'PortfolioImages_webp_optimized\\'+os.path.relpath(full_path, LOCAL_FOLDER_T)
                dir_components = os.path.dirname(rel_path).split(os.sep) if os.path.dirname(rel_path) != '.' else []
                # 폴더 ID 탐색
                folder_id = find_target_folder_id(dir_components)
                if not folder_id:
                    print(f"폴더 미존재: {rel_path}")
                    continue

                # 파일 업로드
                try:
                    file_id = upload_webp(full_path, folder_id)
                    result[os.path.basename(file)] = file_id
                except Exception as e:
                    upload_fail_files.append(file)
                    fail_cnt += 1
                    print(f"업로드 실패: {rel_path} - {str(e)}")

    # 결과 저장
    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print("기존 업로드한 파일개수: = ", upd_cnt)
    print(f"업로드 완료: {len(result)}개 파일 처리")
    print(f"업로드 실패: {fail_cnt}개")


if __name__ == "__main__":
    main()
