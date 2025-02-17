import re

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


# 실행 예시
if __name__ == "__main__":
    test_cases = [
        'src="//culturemarketing.co.kr/gnuboard5/data/a/b.jpg"',  # 프로토콜 생략
        "src='http:/culturemarketing.co.kr/gnuboard5/data/x/y_z.png'",  # 경로 오타
        'SRC="HTTP://CULTUREMARKETING.CO.KR/GNUBOARD5/DATA/2024/IMG.PNG"',  # 대문자
        'src="http:\/\/www.culturemarketing.co.kr/gnuboard5/data/editor/2101/2d9a8c4020412cbaa6b7663f903df1dc_1610691078_7389.jpg">',  # 대문자
        '<img src="https://www.culturemarketing.co.kr/gnuboard5/data/editor/2101/2d9a8c4020412cbaa6b7663f903df1dc_1610691078_7389.jpg"><img src=\"http:\/\/culturemarketing.co.kr\/gnuboard5\/data\/editor\/2310\/test.jpg\">',  # 대문자)
        'SRC="HTTPs://CULTUREMARKETING.CO.KR/GNUBOARD5/DATA/2024/IMG.PNG"'  # 대문자
    ]
    for case in test_cases:
        print(firebase_url_converter(case))
