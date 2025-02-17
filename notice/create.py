import requests
import json
from typing import Dict, Any
from deep_translator import GoogleTranslator
from pathlib import Path
from dotenv import load_dotenv
import os
import re
import urllib.parse

fail_items = []
is_create_Retry = False
title = ''
id = 0

def firebase_url_converter(html):
    # 1단계: 이스케이프 문자 정규화
    # 1단계: 모든 이스케이프 슬래시 정규화
    normalized = re.sub(r'\\+/', '/', html).lower()

    # 2단계: 강화된 정규식 패턴 (Raw 문자열 사용)
    pattern = r'''
    (src\s*=\s*["'])      
    (https?:)?            
    (//)?                 
    (www\.)?              
    (culturemarketing\.co\.kr/)  
    ([\w%\/\._-]+)        
    (["'])                
    '''
    # 그룹1: src 속성 시작
    # 그룹2: 프로토콜
    # 그룹3: 슬래시
    # 그룹4: www
    # 그룹5: 고정 경로
    # 그룹6: 파일 경로
    # 그룹7: 속성 닫기

    def replace_url(match):
        # 그룹 인덱스 재설정
        prefix = match.group(1)
        file_path = match.group(6)  # 실제 경로는 그룹6
        suffix = match.group(7)

        # 경로 인코딩 검증
        if not file_path:
            return match.group(0)  # 매칭 실패시 원본 반환

        encoded = file_path.replace('/', '%2F')
        return f'{prefix}https://firebasestorage.googleapis.com/v0/b/store-892ea.firebasestorage.app/o/{encoded}?alt=media{suffix}'

    return re.sub(pattern, replace_url, normalized, flags=re.X | re.IGNORECASE)


def load_environment(env: str = 'prod'):
    """환경별 설정 파일 로드"""
    current_dir = Path(__file__).resolve().parent
    root_dir = current_dir.parent
    env_path = root_dir / f'.env.{env}'
    env_file = f'.env.{env}'
    if not env_path.exists():
        raise FileNotFoundError(f"{env_file} not found")

    load_dotenv(str(env_path))
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
    url = f"{API_HOST}{API_URL}"

    response = None
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
            raise Exception(f"Response was invalid:")
    except Exception as e:
        is_create_Retry = True
        print(f"⚠️ 업로드 실패: id:{id} // {data.title}")
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
                category = title[(category_start + 1):category_end]
                event_title = title[(category_end + 1):].strip()
            else:
                category = None
                event_title = title.strip()

            req_data = {
                'title': event_title,
                'content': firebase_url_converter(item['wr_content']),
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
    env = 'local'
    # env = os.getenv('ENV', 'prod')  # ENV 환경변수로 설정 가능
    config = load_environment(env)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {config['token']}"
    }
    API_HOST = config['host']
    API_URL = '/api/notices'

    with open('g5_write_notice_202502132315.json', 'r', encoding='utf-8') as f:
        notice_data = json.load(f)
    process_and_createAPI(notice_data)
    with open('fail_info.json', 'w', encoding='utf-8', errors='ignore') as f2:
        json.dump(fail_items, f2, ensure_ascii=False, indent=2)
