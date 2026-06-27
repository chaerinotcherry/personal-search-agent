import io
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

DOWNLOADABLE = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt",
    "text/markdown": ".md",
}
EXPORTABLE = {
    "application/vnd.google-apps.document": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".docx",
    ),
}


def get_drive_service(credentials_path: str, token_path: str):
    if not os.path.exists(token_path):
        raise FileNotFoundError(
            f"Google Drive 토큰이 없습니다. "
            f"먼저 scripts/gdrive_auth.py 를 실행해 인증해주세요."
        )
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    return build("drive", "v3", credentials=creds)


def list_files(service, folder_id: str | None = None) -> list[dict]:
    query_parts = ["trashed = false"]
    mime_filter = " or ".join(
        f"mimeType = '{m}'" for m in list(DOWNLOADABLE) + list(EXPORTABLE)
    )
    query_parts.append(f"({mime_filter})")
    if folder_id:
        query_parts.append(f"'{folder_id}' in parents")
    query = " and ".join(query_parts)

    seen, files, token = set(), [], None
    while True:
        resp = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, size)",
            pageToken=token,
            pageSize=100,
        ).execute()
        for f in resp.get("files", []):
            if f["id"] not in seen:
                seen.add(f["id"])
                files.append(f)
        token = resp.get("nextPageToken")
        if not token:
            break
    return files


def download_file(service, file_id: str, mime_type: str) -> bytes:
    if mime_type in EXPORTABLE:
        export_mime, _ = EXPORTABLE[mime_type]
        req = service.files().export_media(fileId=file_id, mimeType=export_mime)
    else:
        req = service.files().get_media(fileId=file_id)

    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, req)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue()


def get_extension(mime_type: str) -> str:
    if mime_type in EXPORTABLE:
        return EXPORTABLE[mime_type][1]
    return DOWNLOADABLE.get(mime_type, ".bin")
