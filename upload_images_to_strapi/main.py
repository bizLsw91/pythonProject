import os
import json
import requests
from datetime import datetime
from requests_toolbelt.multipart.encoder import MultipartEncoder

def save_to_json(data, output_path):
    """JSON 저장 핸들러"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON 저장 성공: {output_path}")
    except Exception as e:
        print(f"❌ JSON 저장 실패: {str(e)}")

def upload_to_existing_folders(root_path, strapi_url, api_token):
    """기존 폴더 구조에 업로드"""
    media_map = {}

    for root, _, files in os.walk(root_path):
        relative_dir = os.path.relpath(root, root_path).replace('\\', '/')

        for filename in files:
            if not filename.lower().endswith('.webp'):
                continue

            file_path = os.path.join(root, filename)

            try:
                # 멀티파트 데이터 생성
                multipart_data = MultipartEncoder(
                    fields={
                        'files': (filename, open(file_path, 'rb'), 'image/webp'),
                        'folder': relative_dir if relative_dir != '.' else '/'
                    }
                )

                headers = {
                    'Authorization': f'Bearer {api_token}',
                    'Content-Type': multipart_data.content_type
                }

                # 업로드 요청
                response = requests.post(
                    f'{strapi_url}/api/upload',
                    data=multipart_data,
                    headers=headers
                )

                if response.status_code in [200, 201]:
                    media_data = response.json()[0]
                    media_map[filename] = {
                        'id': media_data['id'],
                        'path': f"{relative_dir}/{filename}" if relative_dir != '.' else filename,
                        'url': media_data['url']
                    }
                    print(f'📤 업로드 성공: {media_map[filename]["path"]}')
                else:
                    print(f'⚠️ 실패: {filename} - {response.text}')

            except Exception as e:
                print(f'🚨 에러: {filename} - {str(e)}')

    return media_map

if __name__ == "__main__":
    # 설정값
    LOCAL_FOLDER = r'D:\컬쳐마케팅컴퍼니\이미지파일\PortfolioImages_webp_optimized'
    STRAPI_URL = 'https://cmcstrapi-production.up.railway.app'
    OUTPUT_DIR = r'D:\컬쳐마케팅컴퍼니\이미지파일'
    API_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTAsImlhdCI6MTczODg2OTkxMSwiZXhwIjoxNzM5NDc0NzExfQ._w6uMyyK0dKgL3po5EuSIOlql0K5gVYwTwg5qsz9Aqc'  # 실제 토큰으로 교체

    # 디렉토리 생성
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 업로드 실행
    result = upload_to_existing_folders(LOCAL_FOLDER, STRAPI_URL, API_TOKEN)

    # JSON 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f'media_mapping_{timestamp}.json')
    save_to_json(result, output_path)
