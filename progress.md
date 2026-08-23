# 진행 상황 (progress.md)

> 마지막 갱신: 2026-08-23 (실제 작업 반영 기준일: 2026-07-17)

## 서비스 정보
- 플래시카드 앱: https://engflashcard-web.vercel.app
- 기획서: https://engflashcard-web.vercel.app/proposal.html
- 포트폴리오: https://wsj-portfolio.vercel.app (별도 저장소 `~/portfolio/`)
- GitHub: `git@github.com:wsjdev01/Engflashcard-web.git` → `~/engflashcard-web/` (main 브랜치, push하면 Vercel 자동 배포, 1~2분 소요)
- 구글 시트: https://docs.google.com/spreadsheets/d/107UOIQE9trA6lvoSMSmxRxGHKNt2rVakCBCyVsQItPA/edit

## 구글 시트 구조
- **Book 탭 (gid=0)**: A=Sentence(영어), B=Sentence meaning(의미), C=Comment(설명), D=Source(출처), E=Part of speech(품사), F=Keyword, G=Keyword meaning
- **YouTube 탭 (gid=915780563)**: A=English, B=Korean, C=Comment, D=Source (keyword 컬럼 없음)
- ⚠️ 컬럼 순서가 과거 2번 바뀐 전적 있음 — 작업 전 반드시 실제 헤더 행으로 재확인할 것
- `index.html`의 `DECKS.books.colMap` / `DECKS.youtube.colMap`이 실제 컬럼 인덱스 정의 — 시트 순서 바뀌면 이것도 같이 수정
- Keyword/Keyword meaning은 **Book 탭에만** 존재 (YouTube 탭은 대상 아님)

## 앱 구조 (index.html)
- 홈 화면 메뉴 순서: **키워드별 예문 보기 → 교재(Book) 예문 → YouTube 예문**
- 각 덱 독립 상태 관리 (localStorage, storageKey 분리)
- 시트 데이터는 "게시된 웹 CSV"로 fetch (Sheets API 아님)
- 키워드별 예문 보기: `openKeywordBrowse()` → Book 탭에서 keyword 있는 행만 모아 고유 목록 표시 → 탭하면 같은 keywordMeaning끼리 그룹핑해서 표시
  - 관련 함수: `openKeywordBrowse`, `renderKeywordIndex`, `renderKeywordDetail`, `exitKeywordView`
  - 키워드 목록에 품사(E컬럼)를 작고 흐리게 병기
- 목록/상세 화면(`.list-view`/`.list-content`): 헤더 고정 + 내부 스크롤, 상세 진입 시 스크롤 위치 항상 맨 위로 리셋 ("공부한 카드"/"저장한 카드" 화면도 동일 구조 공유)
- 덱 화면 좌상단 "← 목록" → 집 모양 SVG 아이콘 버튼(`.home-btn`)
- 카드 하단 출처(source): URL이면 "영상 보기 ↗" 클릭 가능한 링크로 자동 렌더링

## 완료된 것 (최신순)
1. **2026-07-17**: Book 탭 E/F/G(품사/키워드/키워드 의미) 채움 완료, colMap 갱신(커밋 9928922). 홈 메뉴 순서 변경 + 키워드 목록에 품사 병기. 목록/상세 화면 스크롤 UX 개선(커밋 a1e8377). 기획서에 위 2건 반영(커밋 f3138a0).
2. **2026-07-12**: 키워드별 예문 보기 기능 신규 구현·배포. 구글시트 컬럼 순서 정리/영문화. 홈 화면 UI 개선(아이콘, 출처 링크 등). 백버튼 개선 여러 차례 시도했으나 실기기에서 실패해 전부 원복(아래 참고).

## 보류/미해결 항목
1. **뒤로가기(백버튼) 커스터마이징** — 원하는 동작: 카드/리스트 화면에서 뒤로가기 → 홈으로 이동, 홈에서 뒤로가기 → 확인창 없이 바로 종료.
   - `history.pushState`+`popstate` 트릭으로 구현·헤드리스 브라우저 검증까지 했으나 **삼성 인터넷·카카오톡 인앱 브라우저에서 전혀 동작 안 함** → 전체 원복(커밋 58ccdad).
   - 다음 시도 힌트: PWA로 홈 화면에 추가해서 `display: standalone`으로 띄우면 가능성 있음. popstate 트릭 재시도는 무의미.
2. **YouTube 자막 자동 추출 자동화** — `youtube_to_sheets.py` 코드는 있으나 YouTube IP 차단으로 막힘(일시적 rate limit 아니고 구조적 차단). 해결책: Webshare 등 프록시(WebshareProxyConfig) 연동 필요. 재개 시 스크립트가 예전 컬럼 순서(A=Korean/B=English) 기준이라 새 순서에 맞게 수정 필요.
   - 최종 목표 파이프라인: 유튜브 좋아요 → 자막 자동 추출(Claude API로 한국어 뜻 생성) → 구글시트 자동 추가 → 앱 자동 반영(이미 완성). 실시간 아님, 주기적 자동 실행(예: 하루 1회, launchd/cron)으로 충분하다고 확정됨.
   - 지금은 **구글시트에 직접 수동 타이핑**으로 운영 중 (기본 운영 방식).
3. **멀티에이전트 협업 아이디어** — [webtoon-harness](https://github.com/revfactory/webtoon-harness) 참고해서 여러 에이전트 공동 작업 방식에 관심 표명(2026-07-17). 아직 구체적 적용 방향(이 프로젝트에 적용할지 별도 프로젝트로 할지) 미정 — 아이디어 가져오면 그때 논의.
4. **교보ebook 교재 문장 자동 추출** — DRM + 저작권(대량 복제) 이유로 진행 안 하기로 확정(2026-07-17). 소량 개인 발췌만 허용, 대량 캡처/추출은 기기 불문 거절 방침.

## 기본 운영 방식 (계속 반복되는 작업)
- YouTube 탭: 좋아요한 영상 문장을 구글시트에 직접 수동 입력 (English, Korean, Comment, Source)
- Book 탭: 새 문장 추가 시 Sentence/Sentence meaning/Comment/Source/Part of speech/Keyword/Keyword meaning 순서로 직접 타이핑 — 시트만 채우면 앱에 자동 반영, 코드 작업 불필요
- UI/UX 변경은 작은 단위로 요청 → 구현 → 커밋+푸시까지 마쳐야 실제 배포됨 (git push = 자동 배포)

## 참고: 포트폴리오
- `~/portfolio/index.html`은 플래시카드 프로젝트 소개 카드 + 링크만 있음, 상세 내용은 전부 `proposal.html`(engflashcard-web 저장소 소속) 쪽에 있음
- "포트폴리오에 반영해줘" 요청이 와도 실제 커밋은 **engflashcard-web** 쪽에서 진행

## 세션 로그
### 2026-08-23
- 오랜만에 재접속 → 이전 작업 내용 파악 요청 → 기존 메모리(2026-07-17 기준) 내용을 정리해서 요약 보고
- 앞으로 세션 간 인수인계용으로 이 `progress.md` 파일을 신규 생성 (기존엔 Claude 메모리 시스템에만 기록돼 있었음)
- 커밋(`e029b54`)·푸시 완료 — 인증정보 파일(`google_oauth_client.json`, `sheets_token.json`, `youtube_token.json`)은 그대로 untracked 상태 유지, `progress.md`만 커밋
- 코드 변경/배포는 없었음, 문서 정리만 진행한 세션
- **(이어서, 같은 날) webtoon-harness 관련 논의 진행:**
  - 사용자가 전에 공유했던 [webtoon-harness](https://github.com/revfactory/webtoon-harness) 링크를 다시 언급 → 저장소 내용을 실제로 fetch해서 구조 파악
    - 27개 에이전트(`.claude/agents/*.md`, 역할 지침 텍스트 파일) + 4개 팀(리서치 5명/시나리오 9명/비주얼 8명/조립검수 4명)
    - 오케스트레이터는 `agents`가 아니라 `.claude/skills/webtoon-orchestrator/`에 있는 **스킬**(총괄 매뉴얼) — 에이전트는 매번 백지 상태로 시작해 맥락이 없고, 오케스트레이션은 맥락을 유지해야 하는 일이라 메인 대화 스레드가 스킬(매뉴얼)을 읽고 직접 지휘하는 구조임을 확인/설명
    - MIT 라이선스 확인
  - "Claude Code 하네스"라는 용어에 대해 사용자가 헷갈려함(Claude Code=내가 얘기하는 존재인데 하네스는 뭔가 싶었음) → Claude Code는 Anthropic 공식 하네스(모델을 감싸는 도구/설정 틀)이고, webtoon-harness는 그 위에 제3자(revfactory)가 얹은 비공식 커스텀 확장이라고 설명해서 해소함
  - 공개 GitHub 저장소를 Claude가 fetch해서 읽어와도 되는지 사용자가 확인 → 공개 저장소라 문제없음, 다만 코드를 그대로 가져다 쓰는 건 라이선스 확인이 별개 이슈라고 설명
  - **사용자가 실제 적용 아이디어를 처음 제시함**: "영어 플래시카드 수동작업이 너무 오래 걸리니, 에이전트에 역할을 정의해서 대신 시키고 싶다"
    - Claude가 병목 지점을 명확히 하려고 질문 시도(Book 탭 가공? YouTube 탭 가공? 시트 직접 입력 자체가 문제?) → 사용자가 자리 이동 사유로 세션 중단, **아직 답변 안 됨**
  - 참고: Book 탭 문장을 "대량 자동 캡처/추출"하는 건 이미 저작권상 금지 확정된 영역([[feedback_copyright_bulk_extraction]] 참고) — 에이전트 적용 논의 시 이 경계(문장을 구하는 일 vs 구한 문장을 가공하는 일)를 유지해야 함
- **(이어서, 같은 날) Book 탭 병목 원인 파악 완료 — 결론: 자동화 불가, 수동 유지로 확정**
  - 사용자 답변: 병목은 YouTube 탭이 아니라 **Book 탭에서 책 보며 문장 등록하는 작업**
  - 단계별로 좁혀들어간 결과, 진짜 병목은 "원문(Sentence) 자체를 손으로 타이핑하는 것" — 나머지 6컬럼(의미/설명/출처/품사/키워드/키워드의미)은 이미 복붙 등으로 빠르게 처리 중이라 자동화해도 큰 차이 없음
  - 원문 소스는 **전자책(Kindle/교보 등, DRM 걸림)** — 복사/붙여넣기가 막혀서 손으로 칠 수밖에 없는 상황
  - 이 책은 소설이 아니라 **영어 문장 학습 교재**라 예문이 끝없이 이어지는 구조 → 사용자는 책 전체 예문을 사실상 순차적으로 다 등록 중 ("가끔 맘에 드는 문장 발췌" 아님)
  - 검토했다가 기각된 대안들:
    1. 문장 1개씩 스크린샷 + OCR로 원문 자동 타이핑 → 이 책은 "소량 발췌"가 아니라 사실상 전체 예문을 계속 등록하는 구조라 이 방식 자체가 성립 안 함(사용자 지적)
    2. 전자책 플랫폼 공식 하이라이트/메모 내보내기 기능 활용 → "어차피 모든 문장에 다 해야 해서 의미 없다"며 기각
    3. 대량 자동 추출 + 로컬 저장만(배포 안 함) → 거절. 저작권은 복제권을 배포권과 별개로 보호하고, 한국 저작권법 104조의2가 DRM 무력화 자체를 금지하므로 비공개 로컬 저장도 문제됨을 설명
    4. 음성 딕테이션(아이패드 마이크로 읽어서 타이핑 대체, 저작권 이슈 없는 순수 생산성 제안) → 사용자가 "불편할 듯"이라며 거절
  - **최종 결론**: Book 탭 원문 입력 병목에 대한 뾰족한 해결책 없음 — 사용자가 기존 방식(수동 타이핑)대로 계속 진행하기로 확정. 이 주제는 2026-07-17에도 한 번 논의돼서 같은 결론(자동화 불가)에 도달한 적 있음 — 세 번째 재논의 시 [[feedback_copyright_bulk_extraction]] 메모 근거로 바로 결론 제시할 것, 처음부터 재탐색 불필요
  - 코드 변경/커밋 없음, 논의만 진행

- **(이어서, 같은 날) YouTube 자막 자동화 재개 성공 — 오랫동안 막혀있던 작업 완료**
  - "에이전트로 할 만한 작업 없나" 질문에 YouTube 자막 자동화(기존 `youtube_to_sheets.py`, IP 차단으로 보류 상태였던 것)를 재추천 → 사용자 동의, 재개
  - **IP 차단 풀림 확인** — 프록시(Webshare) 없이 재시도했더니 정상 동작. 더 이상 프록시 불필요
  - **코드 버그 2개 발견·수정**:
    1. 스크립트가 예전 컬럼 순서(A=한국어/B=영어) 기준으로 짜여 있어서 그대로 돌리면 한/영이 뒤바뀌어 저장될 뻔함 → 현재 실제 순서(A=영어/B=한국어)에 맞게 수정
    2. `get_credentials()`가 저장된 구글 토큰 갱신 실패(`invalid_grant`) 시 재로그인으로 폴백하지 않고 그냥 죽던 버그 → try/except로 감싸서 실패 시 브라우저 재인증으로 폴백하도록 수정
  - **Anthropic API 키 신규 발급 + 크레딧 충전($5) 완료** — 발급 과정에서 "Continue with an API key"(identity federation 아님) 선택, "No expiration" 설정, 첫 400 에러는 크레딧 부족 문제였고 결제 후 해결
  - **`.env` 기반 키 관리 체계 신규 구축** (사용자가 "로컬 저장하면 나도 읽을 수 있는 거 아니냐"고 우려 제기 → 정직하게 "기술적으로는 가능하지만 스크립트만 읽게 설계하고 직접 안 열어보겠다"고 설명 후 진행 합의):
    - `.gitignore` 신규 생성 (그동안 아예 없어서 인증파일들이 "우연히" untracked였음 — 이제 확실히 보호됨, 과거 커밋 이력에도 없었음을 확인함)
    - `.env`(`chmod 600`) + `load_env.py`(값 출력 안 하는 최소 로더) 추가
    - 실제 키 값은 사용자가 직접 실제 터미널(nano)에서 입력 — Claude가 직접 타이핑/열람하지 않음
    - **주의**: 파일 변경 감지 시스템 알림으로 `.env`의 실제 키 값이 한 번 Claude 컨텍스트에 그대로 노출된 적 있음 (harness가 자동으로 diff를 보여줌, Claude가 의도적으로 연 게 아님) — 사용자에게 즉시 투명하게 고지함. 앞으로 `.env` 재편집 시에도 같은 방식으로 노출될 수 있음을 인지하고 있을 것
  - **최종 실행 결과**: YouTube 탭 12~17행에 새 문장 6개 추가 성공 (좋아요한 영상 자막에서 추출), 한국어 뜻까지 Claude가 자동 생성해서 채움
  - **버그 하나 더 발견·수정**: `clean_sentences()`의 반복 캡션 병합 로직이 16행("I'm in the middle of something"이 3번 겹쳐 저장됨)을 못 잡음 → 원인 로직 자체는 아직 안 고치고, 해당 행 데이터만 `backfill_korean.py`로 수동 보정함 (근본 수정은 다음에 비슷한 사례 또 나오면 진행)
  - 커밋 `4d55051`: `.gitignore`, `load_env.py`, `reauth_only.py`, `test_api_key.py`, `backfill_korean.py` 신규 + `youtube_to_sheets.py` 버그 수정 2건. 푸시 완료 (단, `.env`는 gitignore돼서 당연히 커밋 안 됨)

- **(이어서, 같은 날) 주기 자동 실행 등록 완료 — `/schedule`(클라우드) 대신 로컬 `launchd` 사용**
  - `/schedule` 스킬(Anthropic 클라우드 예약 에이전트) 시도해봤으나 **이 작업엔 구조적으로 안 맞음이 판명됨**: 클라우드 에이전트는 로컬 파일/환경변수 접근 불가한데, 이 스크립트는 구글 토큰(`sheets_token.json`)과 Anthropic 키(`.env`)가 전부 아이맥 로컬 파일이라 그대로는 클라우드에서 못 돌림. (사용자가 "사이트 서버가 아이맥에 있어서 그런거냐"고 오해 → 아니라고 정정: 사이트 자체는 Vercel에 있고, 이 자동화 스크립트의 인증/키 파일만 로컬에 있는 것)
  - 대신 **macOS `launchd`**로 로컬 스케줄 등록 (기존 계획대로):
    - `~/Library/LaunchAgents/com.wsjdev01.engflashcard-youtube.plist` 생성, `launchctl bootstrap`으로 등록 완료
    - **매일 아침 9시(한국시간)** 자동 실행, 로그는 `~/engflashcard-web/logs/youtube_automation.log`(stdout)·`.err.log`(stderr)에 저장
    - 아이맥이 로그인 상태(화면 잠금은 무관)이고 꺼져있지/절전 상태가 아니어야 동작 — 그날 못 돌면 스킵되고 다음날 정상 재시도(밀린 거 몰아서 안 함)
    - `launchctl kickstart -k`로 즉시 강제 실행해서 **헤드리스(사람 개입 없이) 정상 동작 확인 완료**
  - **헤드리스 테스트 실행 중 실제 버그 재발견**: 16행에서 이미 겪었던 "자막 반복" 문제가 다른 영상에서 또 발생 → 이번엔 근본 원인까지 추적해서 수정함
    - 원인: 유튜브 롤링(자동생성) 자막은 같은 문구가 슬라이딩 윈도우로 겹쳐서 여러 번 나오는데(예: 6단어 문장이 7번 겹쳐 42단어 텍스트가 됨), 반복 제거 로직이 **긴 단위부터** 반복을 찾다 보니 "18단어(3번 반복) 뭉치"를 반복 단위로 잘못 판단해서 문장이 3번 겹친 채로 저장됨
    - 수정: 짧은 단위부터 오름차순으로 찾도록 변경 → 최소 반복 단위(원문 1회)를 정확히 찾음 (커밋 `3dfc5ea`)
    - 테스트 실행으로 잘못 들어간 행(18행, 16행과 완전 중복)은 삭제 처리함
  - 최종 시트 상태: 1~17행 정상 (12~17행은 이번 세션에서 새로 추가된 것)

- **다음 세션 시작 지점**:
  1. YouTube 자막 자동화 완전히 정상 동작 + 매일 아침 9시 자동 실행 등록 완료. 사람이 할 일 없음 — 그냥 며칠 지켜보면서 잘 쌓이는지 확인하면 됨
  2. 혹시 `launchd`가 예상대로 안 도는 것 같으면 `~/engflashcard-web/logs/` 안의 로그 파일 먼저 확인할 것
  3. 구글 토큰이 언젠가 또 만료(`invalid_grant`)될 수 있음 — 그땐 `launchd`가 자동 재로그인을 못 하므로(브라우저 인터랙션 필요) 그날 자동화가 조용히 실패함, 사람이 알아채면 `python3 reauth_only.py`로 재인증 필요
  4. Book 탭 입력 자동화는 막다른 길로 결론남(위 참고). 사용자가 다시 꺼내기 전까진 재논의하지 말 것
