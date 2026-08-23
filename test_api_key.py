"""Anthropic API 키가 실제로 동작하는지만 확인하는 테스트 스크립트.
.env에 키가 있으면 그걸 쓰고, 없으면 화면에 안 보이게 입력받음.
키 값 자체는 어디에도 출력하지 않음 (길이/접두사 같은 비민감 정보만 표시)."""
import os
import getpass
import anthropic
from load_env import load_env

load_env()

api_key = os.environ.get('ANTHROPIC_API_KEY', '').strip()
source = '.env'
if not api_key:
    api_key = getpass.getpass('🔑 Anthropic API Key 입력: ').strip()
    source = '직접 입력'

# 키 값 자체는 절대 출력하지 않음 — 길이/고정 접두사(sk-ant-, 모든 키 공통이라 비민감)만 확인용으로 표시
print(f'(참고: {source}에서 읽음, 길이 {len(api_key)}자, 시작: {api_key[:7]}...)' if api_key else '⚠️ 키가 비어있음')

try:
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=20,
        messages=[{'role': 'user', 'content': 'say hi'}]
    )
    print('✅ 성공! 응답:', msg.content[0].text)
except Exception as e:
    detail = str(e)[:300]
    print('❌ 실패:', type(e).__name__)
    print('   상세:', detail)
