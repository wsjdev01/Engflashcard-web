import os
import re
import time
import getpass
import anthropic
from load_env import load_env

load_env()
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
]

SPREADSHEET_ID = '107UOIQE9trA6lvoSMSmxRxGHKNt2rVakCBCyVsQItPA'
YOUTUBE_GID = 915780563

CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), 'google_oauth_client.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'sheets_token.json')


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        refreshed = False
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                refreshed = True
            except Exception as e:
                print(f'⚠️  토큰 갱신 실패, 재로그인 필요: {e}')
        if not refreshed:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return creds


def get_youtube_tab_name(sheets):
    meta = sheets.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    for sheet in meta['sheets']:
        if sheet['properties']['sheetId'] == YOUTUBE_GID:
            return sheet['properties']['title']
    return None


def get_existing_english(sheets, tab_name):
    # Column A = English, Column B = Korean meaning (colMap: english:0, meaning:1, explanation:2, source:3)
    result = sheets.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{tab_name}'!A2:A"
    ).execute()
    rows = result.get('values', [])
    return {_norm(row[0]) for row in rows if row}


def _norm(s):
    return re.sub(r'[^a-zA-Z\s]', '', s).lower().strip()


def get_liked_videos(youtube):
    videos = []
    request = youtube.videos().list(
        part='snippet',
        myRating='like',
        maxResults=50
    )
    while request:
        response = request.execute()
        for item in response.get('items', []):
            videos.append({
                'id': item['id'],
                'title': item['snippet']['title'],
                'url': f"https://www.youtube.com/watch?v={item['id']}",
            })
        request = youtube.videos().list_next(request, response)
    return videos


def get_transcript(video_id):
    try:
        api = YouTubeTranscriptApi()
        tl = api.list(video_id)
        t = tl.find_transcript(['en', 'en-US', 'en-GB'])
        return [e.text.strip() for e in t.fetch() if e.text.strip()]
    except Exception as e:
        print(f"  → 자막 없음: {e}")
        return None


def collapse_repetitions(s):
    """'X X X X...' → 'X.' when a phrase repeats 2+ times."""
    words = s.split()
    n = len(words)
    if n < 6:
        return s
    # Strip punctuation from each word for comparison only
    norm_words = [re.sub(r'[.!?,;]+$', '', w) for w in words]
    # 짧은 반복 단위부터 검사해야 최소 주기를 찾음 (긴 것부터 찾으면 "여러 번 겹친 덩어리"를
    # 하나의 반복 단위로 착각해서, 실제로 한 번만 나온 문장을 여러 번 남기는 버그가 있었음)
    for length in range(3, n // 2 + 1):
        phrase = tuple(norm_words[:length])
        pos, count = length, 1
        while pos + length <= n:
            if tuple(norm_words[pos:pos + length]) == phrase:
                count += 1
                pos += length
            else:
                break
        if count >= 2:
            remaining = tuple(norm_words[pos:])
            if not remaining or remaining == phrase[:len(remaining)]:
                result = re.sub(r'[.!?,;]+$', '', ' '.join(words[:length]).strip())
                return result + '.'
    return s


def clean_sentences(raw):
    # Join all captions into one text block and split into proper sentences.
    # This handles rolling-window captions (same phrase repeated across entries).
    full_text = ' '.join(raw)
    full_text = re.sub(r'>>\s*', ' ', full_text)
    full_text = re.sub(r'\s+', ' ', full_text).strip()

    # Split on sentence-ending punctuation followed by a capital letter
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', full_text)

    # Deduplicate by normalized form
    seen = {}  # norm -> best string
    for s in parts:
        s = collapse_repetitions(s.strip())
        s = s.strip()
        if len(s.split()) < 3:
            continue
        norm = _norm(s)
        if not norm or len(norm) < 8:
            continue
        if norm not in seen:
            seen[norm] = s

    sentences = list(seen.values())

    # Merge very similar sentences (Jaccard >= 0.75), keep the shorter one
    word_sets = [set(_norm(s).split()) for s in sentences]
    kept = [True] * len(sentences)
    for i in range(len(sentences)):
        if not kept[i]:
            continue
        for j in range(i + 1, len(sentences)):
            if not kept[j]:
                continue
            inter = word_sets[i] & word_sets[j]
            union = word_sets[i] | word_sets[j]
            if union and len(inter) / len(union) >= 0.75:
                if len(sentences[i]) <= len(sentences[j]):
                    kept[j] = False
                else:
                    kept[i] = False
                    break

    return [sentences[i] for i in range(len(sentences)) if kept[i]]


def get_korean_meaning(claude, sentence):
    try:
        msg = claude.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=80,
            messages=[{
                'role': 'user',
                'content': (
                    f'다음 영어 표현의 한국어 뜻을 간결하게 알려줘 (예: "즉흥으로 하다", "준비가 다 됐다"). '
                    f'뜻만, 설명 없이:\n{sentence}'
                ),
            }]
        )
        result = msg.content[0].text.strip()
        # 가끔 프롬프트를 무시하고 줄바꿈 섞인 여러 뜻을 줄 때가 있음 — 구글시트 CSV 내보내기에서
        # 셀 안 줄바꿈이 파싱을 깨뜨리므로(카드가 여러 개로 쪼개져 나옴), 한 줄로 합쳐둠
        result = re.sub(r'\s*\n+\s*', ' / ', result).strip()
        return result
    except Exception as e:
        print(f'  ⚠️  Claude API 오류: {e}')
        return ''


def main():
    print('🔐 구글 인증 중...')
    creds = get_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    sheets = build('sheets', 'v4', credentials=creds)

    tab_name = get_youtube_tab_name(sheets)
    if not tab_name:
        print('❌ YouTube 탭을 찾을 수 없어요!')
        return
    print(f'✅ YouTube 탭: "{tab_name}"')

    existing = get_existing_english(sheets, tab_name)
    print(f'✅ 기존 항목 {len(existing)}개 확인')

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        try:
            api_key = getpass.getpass('🔑 Anthropic API Key 입력 (Enter 건너뛰기): ').strip()
        except Exception:
            api_key = ''
    claude = anthropic.Anthropic(api_key=api_key) if api_key else None
    if claude:
        print('✅ Claude API 연결됨 → 한국어 의미 자동 추가')
    else:
        print('⚠️  API Key 없음 → 한국어 의미 비워둠')

    print('\n📺 좋아요 영상 가져오는 중...')
    videos = get_liked_videos(youtube)
    print(f'총 {len(videos)}개 영상')

    new_rows = []
    seen = set(existing)

    for i, video in enumerate(videos):
        print(f'\n[{i+1}/{len(videos)}] {video["title"]}')
        raw = get_transcript(video['id'])
        if not raw:
            continue

        sentences = clean_sentences(raw)
        print(f'  → {len(sentences)}개 문장')
        time.sleep(2)

        for s in sentences:
            norm = _norm(s)
            if norm in seen or len(norm) < 8:
                continue
            seen.add(norm)

            korean = ''
            if claude:
                print(f'  💬 {s}')
                korean = get_korean_meaning(claude, s)
                if korean:
                    print(f'     → {korean}')

            # Column A = English, Column B = Korean meaning, C = Comment, D = Source
            new_rows.append([s, korean, '', video['url']])

    if not new_rows:
        print('\n✅ 추가할 새 문장이 없어요.')
        return

    print(f'\n📝 {len(new_rows)}개 문장 구글 시트에 추가 중...')
    sheets.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{tab_name}'!A:D",
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': new_rows}
    ).execute()

    print(f'🎉 완료! {len(new_rows)}개 문장이 유튜브 탭에 추가됐어요.')


if __name__ == '__main__':
    main()
