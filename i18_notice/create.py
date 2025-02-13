import requests
import json
from typing import Dict, Any
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import os

prod_token = '8f134d46255641e1d19204e4bd40a0287140fda43e8dbfaf9f30d8d3bd2b2c7b33e03f2dfab63cfcd6ba85617c7aa54545b37971c4e3e00818da1454671b11767980182448598c11e0cd8d6d387c679a09da6ec5cf102b1ff16c628375ff926849b50fd3a470e50ca7a1d2fcfa69b40f86c7178dac616aac38d494ff1fd3fd36'
local_token = "8391a93fa00b44be7374a80c96d265cb4051ae4b670ef93760ce509f754821989056743ab6251631519f97483b4958e468a7bd89de6b52ea653f52f8b409adf5856e42e33e518914faf7dc41269071488db502e69accf13c63c259fcdf404437599314017c3d0e39f288fbc0c8a9c4b3f70426e7407252caf0d93e2c04ed33af"
prod_STRAPI_HOST = 'https://cmcstrapi-production.up.railway.app'
local_STRAPI_HOST = 'http://localhost:1337'

headers = {
    'Content-Type': 'application/json',
    'Authorization': prod_token
}
API_HOST = prod_STRAPI_HOST
fail_items = []
is_create_Retry = False
title = ''
id = 0



def load_environment(env: str = 'prod'):
    """환경별 설정 파일 로드"""
    env_file = f'.env.{env}'
    if not os.path.exists(env_file):
        raise FileNotFoundError(f"{env_file} not found")

    load_dotenv(env_file)
    return {
        'host': os.getenv('STRAPI_HOST'),
        'token': os.getenv('API_TOKEN')
    }

def translate_korean_to_english(text: str) -> str:
    """한국어 텍스트를 영어로 번역"""
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except Exception as e:
        print(f"⚠️ 번역 실패: {text} - {str(e)}")
        return ""


def process_outline(outline: Dict[str, Any]) -> Dict[str, Any]:
    """아웃라인 데이터 변환 함수"""
    if not outline:
        return {}

    processed = outline.copy()
    # topic 배열을 topics 객체 배열로 변환
    if 'topic' in processed:
        processed['topics'] = [{'content': t} for t in processed['topic']]
        del processed['topic']
    del processed['startDate']
    del processed['endDate']
    return processed


def create_notice(data: Dict[str, Any], locale: str = None) -> Dict[str, Any]:
    """포트폴리오 업로드 공통 함수"""
    global is_create_Retry
    url = f"{API_HOST}/api/notices"

    try:
        response = requests.post(
            url,
            headers=headers,
            json={'data': data}
        )
        if response:
            response.raise_for_status()
            return response.json()
        else:
            raise Exception(f"Response was invalid: {response}")
    except Exception as e:
        is_create_Retry = True
        print(f"⚠️ 업로드 실패: id:{id} // {response}")
        raise


def process_and_createAPI(json_items: list):
    """데이터 처리 및 업로드 메인 함수"""
    global is_create_Retry, title, id
    for item in json_items:
        try:

            title = item['wr_subject']
            id = item['wr_id']

            if '[' in title and ']' in title:
                category_start = title.find('[')
                category_end = title.find(']')
                category = title[category_start + 1:category_end]
                event_title = title[category_end + 1:].strip()
            else:
                category = None
                event_title = title.strip()

            req_data = {
                'title': event_title,
                'content': item['wr_content'],
                'category': category,
                'ip': item['wr_ip'],
                'view_cnt': item['wr_hit'],
                'author': '관리자',
            }
            if 'is_create_Retry' not in item or item['is_create_Retry']:
                create_notice(req_data)

            print(f"✅ ------성공: id:{id} title:{title}")

        except Exception as e:
            item['is_create_Retry'] = is_create_Retry
            fail_items.append(item)
            is_create_Retry = False

            print(f"❌ ------오류: id:{id} - {str(e)}")


# 실행 예시
if __name__ == "__main__":
    with open('g5_write_notice_202502132315.json', 'r', encoding='utf-8') as f:
        notice_data = json.load(f)
    process_and_createAPI(notice_data)
    with open('fail_info.json', 'w', encoding='utf-8', errors='ignore') as f2:
        json.dump(fail_items, f2, ensure_ascii=False, indent=2)
