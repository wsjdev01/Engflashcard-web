"""YouTube 탭에서 영어(A열)는 있는데 한국어 뜻(B열)이 비어있는 행만 찾아서 채워주는 백필 스크립트.
+ 16행 캡션 반복 버그(문장이 3번 겹쳐 저장된 것) 수동 보정 포함."""
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import anthropic

from load_env import load_env
from youtube_to_sheets import get_korean_meaning, SPREADSHEET_ID, YOUTUBE_GID, get_youtube_tab_name, SCOPES

load_env()

# 16행 캡션 반복 버그 수동 보정 (자막이 3번 겹쳐 저장된 것 → 원래 문장 하나로)
MANUAL_FIXES = {
    16: "I'm in the middle of something.",
}

creds = Credentials.from_authorized_user_file('sheets_token.json', SCOPES)
sheets = build('sheets', 'v4', credentials=creds)
tab_name = get_youtube_tab_name(sheets)
print(f'탭: {tab_name}')

result = sheets.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=f"'{tab_name}'!A2:B"
).execute()
rows = result.get('values', [])

api_key = os.environ.get('ANTHROPIC_API_KEY', '').strip()
claude = anthropic.Anthropic(api_key=api_key) if api_key else None
if not claude:
    print('⚠️ API 키 없음, 종료')
    exit()

updates = []
for i, row in enumerate(rows, start=2):
    english = row[0] if len(row) > 0 else ''
    korean = row[1] if len(row) > 1 else ''

    if i in MANUAL_FIXES:
        fixed = MANUAL_FIXES[i]
        if english != fixed:
            print(f'{i}행 문장 보정: "{english}" → "{fixed}"')
            english = fixed
            updates.append({'range': f"'{tab_name}'!A{i}", 'values': [[fixed]]})

    if english and not korean:
        k = get_korean_meaning(claude, english)
        print(f'{i}행: {english} → {k}')
        updates.append({'range': f"'{tab_name}'!B{i}", 'values': [[k]]})

if not updates:
    print('✅ 채울 게 없어요.')
else:
    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={'valueInputOption': 'RAW', 'data': updates}
    ).execute()
    print(f'🎉 {len(updates)}개 셀 업데이트 완료')
