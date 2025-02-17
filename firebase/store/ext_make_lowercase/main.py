import os
import re
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from firebase_admin import storage, initialize_app, credentials
from firebase_admin.exceptions import FirebaseError

# 환경 설정
env = 'prod'
current_dir = Path(__file__).resolve().parent
env_path = current_dir.parent.parent.parent / f'.env.{env}'
env_file = f'.env.{env}'
if not env_path.exists():
    raise FileNotFoundError(f"{env_file} not found")
load_dotenv(str(env_path))

# 전역 변수
failed_items = []
processed_count = 0
TARGET_FOLDER = 'gnuboard5/'  # 변경할 대상 폴더
DRY_RUN = False  # 실제 변경 전 테스트 실행

def initialize_firebase():
    """Firebase 초기화"""
    try:
        cred = credentials.Certificate(json.loads(os.getenv("FIREBASE_SERVICE_ACCOUNT")))
        return initialize_app(cred, {
            'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET")
        })
    except Exception as e:
        log_error(f"Firebase 초기화 실패: {str(e)}")
        raise

def process_files(bucket):
    """파일 처리 메인 함수"""
    try:
        blobs = bucket.list_blobs(prefix=TARGET_FOLDER)
        for blob in blobs:
            if should_process(blob.name):
                process_single_file(blob, bucket)
    except FirebaseError as e:
        handle_firebase_error(e)
    except Exception as e:
        log_error(f"치명적 오류: {str(e)}")

def should_process(filename):
    """처리 대상 파일 여부 확인"""
    return re.search(r'\.(JPEG|JPG|PNG|GIF)$', filename, re.IGNORECASE)

def process_single_file(blob, bucket):
    """단일 파일 처리"""
    global processed_count
    try:
        original_name = blob.name
        new_name = generate_new_name(original_name)

        if DRY_RUN:
            print(f"[DRY RUN] {original_name} -> {new_name}")
            return

        if isExt_upper(original_name):
            rename_file(blob, bucket, new_name)
            processed_count += 1
    except Exception as e:
        log_error(f"{original_name} 처리 실패: {str(e)}")
        failed_items.append({'name': original_name, 'error': str(e)})

def rename_file(blob, bucket, new_name):
    """실제 파일 이름 변경"""
    try:
        new_blob = bucket.rename_blob(blob, new_name)
        print(f"성공: {blob.name} -> {new_blob.name}")
    except Exception as e:
        raise RuntimeError(f"리네임 실패: {str(e)}")

def generate_new_name(original):
    """새 파일명 생성"""
    base, ext = os.path.splitext(original)
    return f"{base}{ext.lower()}"
def isExt_upper(original):
    """새 파일명 생성"""
    base, ext = os.path.splitext(original)
    return ext.isupper()

def handle_firebase_error(e):
    """Firebase 특정 오류 처리"""
    error_code = e.code
    if error_code == 404:
        log_error("파일을 찾을 수 없음")
    elif error_code == 403:
        log_error("권한 부족")
    else:
        log_error(f"Firebase 오류: {error_code} - {e.message}")

def log_error(message):
    """에러 로깅"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] ❌ {message}")

def save_failed_items():
    """실패 항목 저장"""
    with open('rename_failures.json', 'w', encoding='utf-8') as f:
        json.dump(failed_items, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    try:
        app = initialize_firebase()
        bucket = storage.bucket()
        process_files(bucket)
        print(f"\n처리 완료: {processed_count}개 파일")
        print(f"실패: {len(failed_items)}개 파일")
    except Exception as e:
        log_error(f"초기화 실패: {str(e)}")
    finally:
        if failed_items:
            save_failed_items()
