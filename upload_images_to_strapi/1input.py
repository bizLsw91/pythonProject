import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

def upload_single_image(file_path, folder_path, strapi_url, api_token):
    try:
        filename = file_path.split('/')[-1]

        multipart_data = MultipartEncoder(
            fields={
                'files': (filename, open(file_path, 'rb'), 'image/webp'),
                'folder': folder_path
            }
        )

        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': multipart_data.content_type
        }

        response = requests.post(
            f'{strapi_url}/api/upload',
            data=multipart_data,
            headers=headers
        )

        if response.status_code in [200, 201]:
            media_data = response.json()[0]
            return {filename: media_data['id']}

        else:
            print(f'⚠️ 업로드 실패: {filename} - {response.text}')
            return None

    except Exception as e:
        print(f'🚨 에러: {filename} - {str(e)}')
        return None

# 사용 예시
STRAPI_URL = 'https://cmcstrapi-production.up.railway.app'
API_TOKEN = '07ba3ca87d5705c4f62f5c97bb1106c534728f51f3cd47ebf43900298849cbae5fcd20a9fed2741c736b1dae7cbe0c53ce12def396a7181e1a88a40b25b5d518fdfa8f82aae765af4b3ce37dfc2317f5c735dbd26579b32f862bf0454b3204ddb3022360caf1b80f6047f696caed6ceadf7cb08748b6838829b790c9122dd514'
FILE_PATH = 'D:/컬쳐마케팅컴퍼니/이미지파일/PortfolioImages_webp_optimized/1. 정부,공공기관(15-24)/2017년/2017 언론인 대상 기상과학 이해와 제고_기상청/01070080_2_11zon.webp'
FOLDER_PATH = '/PortfolioImages_webp_optimized/1. 정부,공공기관(15-24)/2017년/2017 언론인 대상 기상과학 이해와 제고_기상청'

result = upload_single_image(FILE_PATH, FOLDER_PATH, STRAPI_URL, API_TOKEN)
print(result)
