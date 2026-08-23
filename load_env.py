"""'.env' 파일을 읽어 os.environ에 채워넣는 최소 로더.
키 값은 어디에도 print/log 하지 않음 — 파일에서 읽어 환경변수로 설정하기만 함.
이미 셸에 설정된 환경변수가 있으면 그걸 우선하고 .env 값으로 덮어쓰지 않음.
"""
import os


def load_env(path=None):
    path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, _, value = line.partition('=')
            key, value = key.strip(), value.strip()
            if value and key not in os.environ:
                os.environ[key] = value
