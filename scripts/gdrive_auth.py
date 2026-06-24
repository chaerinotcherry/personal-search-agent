#!/usr/bin/env python3
"""
Google Drive 인증 스크립트 — 최초 1회만 실행하면 됩니다.
브라우저가 열리면 구글 계정으로 로그인 후 허용하세요.
토큰은 ~/.config/mcp-gdrive/token.json 에 저장됩니다.
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
CREDS_PATH = os.path.expanduser("~/.config/mcp-gdrive/credentials.json")
TOKEN_PATH = os.path.expanduser("~/.config/mcp-gdrive/token.json")

if not os.path.exists(CREDS_PATH):
    print(f"❌ credentials.json 없음: {CREDS_PATH}")
    print("Google Cloud Console에서 OAuth 데스크톱 앱 credentials.json을 다운받아 해당 경로에 저장하세요.")
    exit(1)

flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
creds = flow.run_local_server(port=0)

with open(TOKEN_PATH, "w") as f:
    f.write(creds.to_json())

print(f"✅ 인증 완료. 토큰 저장됨: {TOKEN_PATH}")
print("이제 docker compose up 하면 Google Drive ingest가 작동합니다.")
