import asyncio
import hashlib
import io
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel

from config import settings
from db import get_collection
from embeddings import get_model

router = APIRouter()

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def _parse_pdf(data: bytes) -> str:
    import fitz  # pymupdf
    doc = fitz.open(stream=data, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def _parse_docx(data: bytes) -> str:
    import docx
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
        f.write(data)
        tmp = f.name
    try:
        doc = docx.Document(tmp)
        return "\n".join(p.text for p in doc.paragraphs)
    finally:
        os.unlink(tmp)


def _parse_md(data: bytes) -> str:
    import markdown
    from bs4 import BeautifulSoup
    html = markdown.markdown(data.decode("utf-8", errors="replace"))
    return BeautifulSoup(html, "html.parser").get_text()


def _parse_txt(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


_PARSERS = {
    ".pdf": _parse_pdf,
    ".docx": _parse_docx,
    ".md": _parse_md,
    ".txt": _parse_txt,
}


def extract_text(data: bytes, ext: str) -> str:
    parser = _PARSERS.get(ext.lower())
    if parser is None:
        raise ValueError(f"Unsupported extension: {ext}")
    return parser(data)


def ingest_document(text: str, doc_id_key: str, metadata: dict) -> int:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    import re
    # strip control chars and null bytes that break the Rust tokenizer
    def _clean(s: str) -> str:
        s = s.replace("\x00", "")
        s = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", s)
        return " ".join(s.split())

    raw = splitter.split_text(text[:200_000])  # cap at 200k chars (~400 chunks max)
    chunks = [_clean(c) for c in raw if c and isinstance(c, str)]
    chunks = [c for c in chunks if len(c) > 10]
    if not chunks:
        return 0

    embeddings = get_model().encode(chunks, show_progress_bar=False).tolist()

    source_hash = hashlib.md5(doc_id_key.encode()).hexdigest()[:8]
    ids = [f"{source_hash}_{i}" for i in range(len(chunks))]
    metadatas = [{**metadata, "chunk_index": i} for i in range(len(chunks))]

    get_collection().upsert(documents=chunks, embeddings=embeddings, ids=ids, metadatas=metadatas)
    return len(chunks)


# ── Response models ───────────────────────────────────────────────────────────

class IngestResponse(BaseModel):
    status: str
    source: str
    filename: str
    chunks_ingested: int
    collection: str


class LocalIngestResponse(BaseModel):
    status: str
    source: str
    files_processed: int
    files_skipped: int
    chunks_ingested: int
    collection: str


class ExternalIngestResponse(BaseModel):
    status: str
    source: str
    pages_processed: int
    pages_skipped: int
    chunks_ingested: int
    collection: str


class IngestJobResponse(BaseModel):
    status: str
    message: str


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/ingest", response_model=IngestResponse)
async def ingest_file(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type '{ext}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}",
        )

    data = await file.read()
    try:
        text = extract_text(data, ext)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse file: {e}")

    text = text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Document is empty after parsing.")

    metadata = {
        "source": "local",
        "file_name": file.filename,
        "file_path": file.filename,
        "created_at": datetime.now(timezone.utc).date().isoformat(),
    }
    n = ingest_document(text, doc_id_key=file.filename, metadata=metadata)
    return IngestResponse(
        status="ok",
        source="upload",
        filename=file.filename,
        chunks_ingested=n,
        collection=settings.collection_name,
    )


@router.post("/ingest/local", response_model=LocalIngestResponse)
async def ingest_local():
    folder = Path(settings.local_folder_path)
    if not folder.exists():
        raise HTTPException(status_code=404, detail=f"Local folder not found: {folder}")

    files_processed = 0
    files_skipped = 0
    total_chunks = 0

    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            files_skipped += 1
            continue
        try:
            text = extract_text(path.read_bytes(), path.suffix).strip()
        except Exception:
            files_skipped += 1
            continue

        if not text:
            files_skipped += 1
            continue

        try:
            created_at = int(datetime.fromtimestamp(
                path.stat().st_mtime, tz=timezone.utc
            ).date().isoformat().replace("-", ""))
        except Exception:
            created_at = datetime.now(timezone.utc).date().isoformat()

        metadata = {
            "source": "local",
            "file_name": path.name,
            "file_path": str(path),
            "created_at": created_at,
        }
        total_chunks += ingest_document(text, doc_id_key=str(path), metadata=metadata)
        files_processed += 1

    return LocalIngestResponse(
        status="ok",
        source="local",
        files_processed=files_processed,
        files_skipped=files_skipped,
        chunks_ingested=total_chunks,
        collection=settings.collection_name,
    )


@router.post("/ingest/notion", response_model=ExternalIngestResponse)
async def ingest_notion():
    if not settings.notion_api_key:
        raise HTTPException(status_code=503, detail="NOTION_API_KEY가 설정되지 않았습니다.")

    from ingest_notion import fetch_all_pages

    try:
        pages = await asyncio.to_thread(fetch_all_pages, settings.notion_api_key)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Notion API 오류: {e}")

    processed, skipped, total_chunks = 0, 0, 0
    for page in pages:
        text = page["text"].strip()
        if not text:
            skipped += 1
            continue
        metadata = {
            "source": "notion",
            "file_name": page["title"],
            "file_path": page["url"],
            "created_at": int(page["last_edited"].replace("-", "")) if page["last_edited"] else 0,
        }
        total_chunks += ingest_document(text, doc_id_key=page["page_id"], metadata=metadata)
        processed += 1

    return ExternalIngestResponse(
        status="ok",
        source="notion",
        pages_processed=processed,
        pages_skipped=skipped,
        chunks_ingested=total_chunks,
        collection=settings.collection_name,
    )


async def _run_gdrive_ingest(folder_id: str | None) -> None:
    """백그라운드에서 실행되는 실제 GDrive ingest 로직"""
    from ingest_gdrive import download_file, get_drive_service, get_extension, list_files
    try:
        service = await asyncio.to_thread(
            get_drive_service, settings.gdrive_credentials_path, settings.gdrive_token_path
        )
        files = await asyncio.to_thread(list_files, service, folder_id)
    except Exception as e:
        print(f"[gdrive] setup error: {e}")
        return

    MAX_FILE_BYTES = 10 * 1024 * 1024
    FILE_TIMEOUT = 60
    processed, skipped, total_chunks = 0, 0, 0

    for f in files:
        ext = get_extension(f["mimeType"])
        if ext not in SUPPORTED_EXTENSIONS:
            skipped += 1
            continue
        size = int(f.get("size", 0) or 0)
        if size > MAX_FILE_BYTES:
            print(f"[gdrive] skip too large ({size//1024//1024}MB): {f['name']}")
            skipped += 1
            continue
        print(f"[gdrive] processing: {f['name']}")
        try:
            data = await asyncio.wait_for(
                asyncio.to_thread(download_file, service, f["id"], f["mimeType"]),
                timeout=FILE_TIMEOUT,
            )
            text = await asyncio.wait_for(
                asyncio.to_thread(lambda d=data, e=ext: extract_text(d, e).strip()),
                timeout=FILE_TIMEOUT,
            )
        except asyncio.TimeoutError:
            print(f"[gdrive] timeout parsing: {f['name']}")
            skipped += 1
            continue
        except Exception as e:
            print(f"[gdrive] parse error {f['name']}: {e}")
            skipped += 1
            continue
        if not text:
            skipped += 1
            continue

        modified = f.get("modifiedTime", "")[:10].replace("-", "")
        metadata = {
            "source": "gdrive",
            "file_name": f["name"],
            "file_path": f"gdrive://{f['id']}",
            "created_at": int(modified) if modified else 0,
        }
        try:
            n = await asyncio.wait_for(
                asyncio.to_thread(ingest_document, text, f["id"], metadata),
                timeout=FILE_TIMEOUT,
            )
            total_chunks += n
            processed += 1
            print(f"[gdrive] done: {f['name']} ({n} chunks)")
        except asyncio.TimeoutError:
            print(f"[gdrive] timeout embedding: {f['name']}")
            skipped += 1
        except Exception as e:
            print(f"[gdrive] ingest error {f['name']}: {e}")
            skipped += 1

    print(f"[gdrive] 완료 — {processed}개 파일, {total_chunks}개 청크, {skipped}개 스킵")


@router.post("/ingest/gdrive", response_model=IngestJobResponse)
async def ingest_gdrive(background_tasks: BackgroundTasks, folder_id: str | None = None):
    from ingest_gdrive import get_drive_service

    try:
        await asyncio.to_thread(
            get_drive_service, settings.gdrive_credentials_path, settings.gdrive_token_path
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Google Drive 인증 오류: {e}")

    background_tasks.add_task(_run_gdrive_ingest, folder_id)
    return IngestJobResponse(
        status="started",
        message="GDrive ingest 백그라운드 시작됨. docker logs로 진행 확인 가능.",
    )
