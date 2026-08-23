"""구글 인증 토큰만 새로 발급받는 스크립트. youtube_to_sheets.py 본 실행 전에 따로 인증만 갱신할 때 사용."""
from youtube_to_sheets import get_credentials

if __name__ == '__main__':
    creds = get_credentials()
    print('✅ 인증 완료, 토큰 저장됨:', creds.valid)
