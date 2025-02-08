"""
📁 [디렉토리 동기화 검증 시스템]
■ 주요 기능:
  - 📂 재귀적 파일 수 카운팅
  - 🔄 입력/출력 폴더 구조 비교
  - ⚠️ 불일치 항목 자동 검출
  - 📊 서브디렉토리별 상세 분석

■ 기술 사양:
  - Python 3.8+ 호환
  - OS 파일 시스템 직접 접근
  - Cross-platform 지원 (Win/macOS/Linux)

■ 사용 시나리오:
  - 개발: CI/CD 파이프라인 파일 검증
  - 테스트: 데이터 마이그레이션 검증
  - 운영: 백업 시스템 무결성 점검

■ 버전 정보:
  - 배포: 2025.02.08 (현재 시스템 날짜 기준)
  - 버전: 1.1.0
  - 라이선스: MIT
  - 제작: Perplexity AI Assistant, directed by dev웅.
"""

import os
from pathlib import Path

def count_files(dir_path):
    """디렉토리별 파일 수 카운트"""
    file_count = {}
    for root, dirs, files in os.walk(dir_path):
        rel_path = os.path.relpath(root, dir_path)
        file_count[rel_path] = len(files)
    return file_count

def compare_directories(input_dir, output_dir):
    """디렉토리 비교 핵심 로직"""
    input_counts = count_files(input_dir)
    output_counts = count_files(output_dir)

    # 전체 파일 수 비교
    total_input = sum(input_counts.values())
    total_output = sum(output_counts.values())
    print(f"■ 전체 파일 수\n입력: {total_input}개, 출력: {total_output}개\n")

    # 불일치 항목 검출
    mismatch_found = False
    all_dirs = set(input_counts.keys()) | set(output_counts.keys())

    for rel_dir in sorted(all_dirs):
        in_cnt = input_counts.get(rel_dir, 0)
        out_cnt = output_counts.get(rel_dir, 0)

        if in_cnt != out_cnt:
            print(f"[불일치] {rel_dir or '<루트>'}: 입력({in_cnt}) ≠ 출력({out_cnt})")
            mismatch_found = True

    # 누락/추가 디렉토리 검사
    missing_in_output = set(input_counts.keys()) - set(output_counts.keys())
    extra_in_output = set(output_counts.keys()) - set(input_counts.keys())

    if missing_in_output:
        print("\n⚠️ 출력에 없는 디렉토리:")
        for d in missing_in_output:
            print(f"  - {d}")

    if extra_in_output:
        print("\n⚠️ 출력에만 있는 디렉토리:")
        for d in extra_in_output:
            print(f"  - {d}")

    if not mismatch_found and not missing_in_output and not extra_in_output:
        print("✅ 모든 디렉토리의 파일 수가 일치합니다.")

# 실행 예시
if __name__ == "__main__":
    INPUT = r"D:\컬쳐마케팅컴퍼니\이미지파일\문화 및 기업 행사\3. 기업 행사"
    OUTPUT = r"D:\컬쳐마케팅컴퍼니\이미지파일\문화 및 기업 행사\3. 기업 행사_webp_optimized"

    compare_directories(INPUT, OUTPUT)
