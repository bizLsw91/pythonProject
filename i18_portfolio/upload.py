import requests
import json
from typing import Dict, Any
from deep_translator import GoogleTranslator

STRAPI_HOST = 'https://cmcstrapi-production.up.railway.app'
headers = {
    'Content-Type': 'application/json'
}
fail_items = []
is_upload_Retry_ko = False
is_upload_Retry_en = False
title_ko = ''

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


def upload_portfolio(data: Dict[str, Any], locale: str = None, doc_id: str = '') -> Dict[str, Any]:
    """포트폴리오 업로드 공통 함수"""
    global is_upload_Retry_ko, is_upload_Retry_en
    params = {'locale': locale} if locale else {}
    url = f"{STRAPI_HOST}/api/portfolios{('/'+doc_id) if doc_id else ''}"

    try:
        response = None
        if not locale:
            response = requests.post(
                url,
                headers=headers,
                params=params,
                json={'data': data}
            )
        else:
            response = requests.put(
                url,
                headers=headers,
                params=params,
                json={'data': data}
            )
        if response:
            response.raise_for_status()
            return response.json()
        else:
            return {}
    except Exception as e:
        if locale:
            is_upload_Retry_en = True
        else:
            is_upload_Retry_ko = True
        print(f"⚠️ 업로드 실패: [{locale if locale else 'ko'}] // {title_ko} // {response}")
        raise


def process_and_upload(portfolio_items: list):
    """데이터 처리 및 업로드 메인 함수"""
    global is_upload_Retry_ko, is_upload_Retry_en, title_ko
    for item in portfolio_items:
        try:
            if not item['outline'] and not item['outline_en']:
                continue

            title_ko = item['title']
            doc_id = ''

            if item['outline']:
                # 기본(한글) 데이터
                ko_data = {
                    'year': item['year'],
                    'category': item['category'],
                    'title': item['title'],
                    'institution': item['institution'],
                    'startDate': item['outline']['startDate'],
                    'endDate': item['outline']['endDate'],
                    'images': item['images'],
                    'outline': process_outline(item['outline'])
                }
                res = None
                if 'is_upload_Retry_ko' not in item or item['is_upload_Retry_ko']:
                    res = upload_portfolio(ko_data)
                if res:
                    doc_id = res['data']['documentId']

            if item['outline_en']:
                tran_to_en = ''
                title_en_translate = False
                if not item['title_en']:
                    tran_to_en = translate_korean_to_english(item['title'])
                    if tran_to_en:
                        title_en_translate = True
                # 영어 데이터
                en_data = {
                    'year': item['year'],
                    'category': item['category'],
                    'title': tran_to_en,
                    'institution': item['institution'],
                    'startDate': item['outline']['startDate'],
                    'endDate': item['outline']['endDate'],
                    'images': item['images'],
                    'outline': process_outline(item['outline_en']),
                    'title_en_translate': title_en_translate
                }
                if 'is_upload_Retry_en' not in item or item['is_upload_Retry_en']:
                    upload_portfolio(en_data, locale='en', doc_id=doc_id)

            print(f"✅ ------성공: {item['title']}")

        except Exception as e:
            item['is_upload_Retry_ko'] = is_upload_Retry_ko
            item['is_upload_Retry_en'] = is_upload_Retry_en
            fail_items.append(item)
            is_upload_Retry_ko = False
            is_upload_Retry_en = False

            print(f"❌ ------오류: {item.get('title', 'Unknown')} - {str(e)}")


# 실행 예시
if __name__ == "__main__":
    with open('fail_info.json', 'r', encoding='utf-8') as f:
        portfolio_data = json.load(f)
    process_and_upload(portfolio_data)
    with open('fail_info2.json', 'w', encoding='utf-8', errors='ignore') as f2:
        json.dump(fail_items, f2, ensure_ascii=False, indent=2)
