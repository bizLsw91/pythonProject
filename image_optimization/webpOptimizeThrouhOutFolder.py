"""
[📁 webpOptimizeThrouhOutFolder.py - 이미지 처리 자동화 시스템]
■ 주요 기능: CR2/이미지 변환, WebP 최적화, 파일 동기화
■ 처리 대상: RAW(.cr2), WebP, JPG, PNG, GIF
■ 핵심 기술:
  - 🖼️ CR2 → WebP 변환 (rawpy 엔진 지원)
  - 📏 높이 900px 기준 리사이징
  - 🎭 투명도 채널 보존(RGBA)
  - 🔄 원본 WebP 파일 유지 복사
  - 📊 입출력 폴더 파일 수 검증
  - ⚡ 4-Worker 멀티스레딩 처리

■ 사용처:
  - 개발자: 이미지 배치 처리
  - 디자이너: 웹 최적화 자동화
  - 관리자: 디지털 에셋 표준화

■ 버전 정보:
  - 최초 배포: 2025.02.08 (현재 시스템 날짜 기준)
  - 버전: 1.0.0
  - 제작: Perplexity AI Assistant, directed by dev웅.
"""

import os
import shutil
import rawpy
import traceback
from pathlib import Path
from PIL import Image, ImageFile
from concurrent.futures import ThreadPoolExecutor

ImageFile.LOAD_TRUNCATED_IMAGES = True

def process_image(args):
    input_file, output_file, target_height, quality = args

    try:
        # WebP 복사
        if input_file.suffix.lower() == '.webp':
            shutil.copy2(input_file, output_file)
            print(f"📄 Copied WebP: {input_file}")
            return

        # CR2 처리
        if input_file.suffix.lower() == '.cr2':
            with rawpy.imread(str(input_file)) as raw:
                rgb = raw.postprocess()
            img = Image.fromarray(rgb).convert('RGBA')

        # 일반 이미지 처리
        else:
            with Image.open(input_file) as _img:
                # 메모리에 이미지 완전 로드
                if _img.mode in ('P', 'LA'):
                    img = _img.convert('RGBA').copy()
                elif _img.mode == 'RGB':
                    img = _img.convert('RGBA').copy()
                else:
                    img = _img.copy()
                img.load()  # 핵심 수정 부분

        # 리사이징
        if target_height > 0 and img.height > target_height:
            ratio = img.width / img.height
            new_width = int(target_height * ratio)
            alpha = img.split()[-1].resize((new_width, target_height), Image.LANCZOS)
            img = img.resize((new_width, target_height), Image.LANCZOS)
            img.putalpha(alpha)

        # WebP 저장
        output_webp = output_file.with_suffix('.webp')
        img.save(output_webp, 'WEBP', quality=quality, method=6, exact=True)
        print(f"✅ Processed: {input_file} → {output_webp}")

    except Exception as e:
        print(f"❌ Error: {input_file}\n{traceback.format_exc()}")

def sync_and_process(input_dir, output_dir, target_height=900, quality=85):
    """메인 처리 함수"""
    args_list = []

    for root, _, files in os.walk(input_dir):
        rel_path = os.path.relpath(root, input_dir)
        output_path = Path(output_dir) / rel_path
        output_path.mkdir(parents=True, exist_ok=True)

        for file in files:
            input_file = Path(root) / file
            output_file = output_path / file

            # 지원 포맷: CR2 + 이미지 + WebP
            if input_file.suffix.lower() in ('.cr2', '.jpg', '.jpeg', '.png', '.gif', '.webp'):
                args_list.append((input_file, output_file, target_height, quality))
            else:  # 기타 파일 복사
                shutil.copy2(input_file, output_file)
                print(f"📄 Copied: {input_file}")

    # 멀티스레딩 처리
    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(process_image, args_list)

def verify_file_count(input_dir, output_dir):
    """파일 수 검증 함수"""
    def count_files(path):
        return sum(len(files) for _, _, files in os.walk(path))

    input_count = count_files(input_dir)
    output_count = count_files(output_dir)

    print(f"\n🔍 검증 결과: 입력({input_count}) vs 출력({output_count})")
    return input_count == output_count

if __name__ == "__main__":
    INPUT_DIR = r"D:\컬쳐마케팅컴퍼니\이미지파일\PortfolioImages_webp_optimized\3. 기업 행사"
    OUTPUT_DIR = r"D:\컬쳐마케팅컴퍼니\이미지파일\PortfolioImages_webp_optimized\test"

    # 이미지 처리 실행
    sync_and_process(INPUT_DIR, OUTPUT_DIR)

    # 검증 수행
    if verify_file_count(INPUT_DIR, OUTPUT_DIR):
        print("✅ 모든 파일 수가 정확히 일치합니다!")
    else:
        print("⚠️ 경고: 파일 수 불일치 발생! 로그를 확인하세요.")
