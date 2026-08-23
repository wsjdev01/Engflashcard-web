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
- **다음 세션 시작 지점**: "지금 제일 진도가 안 나가는(가장 시간 드는) 작업이 정확히 뭔지" 사용자 답변부터 이어서 진행 — Book 탭 가공(번역/품사/키워드) / YouTube 탭 가공(자막 정제+번역) / 시트 직접 타이핑 자체, 이 중 어디가 병목인지 확인 필요
