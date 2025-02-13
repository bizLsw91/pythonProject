import os
from collections import defaultdict

def find_duplicate_filenames(root_dir):
    """중복 파일명 찾기"""
    filename_dict = defaultdict(list)

    for root, _, files in os.walk(root_dir):
        for filename in files:
            full_path = os.path.join(root, filename)
            filename_dict[filename].append(full_path)

    return {k: v for k, v in filename_dict.items() if len(v) > 1}

def print_results(duplicates):
    """결과 출력"""
    if duplicates:
        print("🔄 중복된 파일명 발견:")
        for filename, paths in duplicates.items():
            print(f"\n📁 파일명: {filename}")
            print("📍 위치:")
            for path in paths:
                print(f"  → {path}")
    else:
        print("✅ 중복된 파일명이 없습니다.")

if __name__ == "__main__":
    target_dir = input("검색할 폴더 경로를 입력하세요: ")

    if os.path.isdir(target_dir):
        duplicates = find_duplicate_filenames(target_dir)
        print_results(duplicates)
    else:
        print("❌ 유효하지 않은 폴더 경로입니다.")
