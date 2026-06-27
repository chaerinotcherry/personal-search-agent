import os

import httpx
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="문서 관리", page_icon="📥", layout="wide")
st.title("📥 문서 관리")
st.caption("문서를 ChromaDB에 저장합니다. 저장된 문서는 검색·분석·채팅에 활용됩니다.")

st.divider()

# ── 파일 업로드 ────────────────────────────────────────────────────────────────
st.subheader("📁 파일 업로드")
uploaded = st.file_uploader(
    "PDF, DOCX, TXT, MD 파일을 올려주세요",
    type=["pdf", "docx", "txt", "md"],
    accept_multiple_files=True,
)
if st.button("업로드 & 저장", disabled=not uploaded, type="primary"):
    success, fail = 0, 0
    for f in uploaded:
        with st.spinner(f"{f.name} 처리 중..."):
            try:
                res = httpx.post(
                    f"{BACKEND_URL}/ingest",
                    files={"file": (f.name, f.getvalue(), f.type)},
                    timeout=60,
                )
                if res.status_code == 200:
                    d = res.json()
                    st.success(f"✅ {f.name} — {d['chunks_ingested']}개 청크 저장")
                    success += 1
                else:
                    st.error(f"❌ {f.name}: {res.json().get('detail', res.text)}")
                    fail += 1
            except Exception as e:
                st.error(f"❌ {f.name}: {e}")
                fail += 1
    if success:
        st.info(f"{success}개 파일 완료" + (f", {fail}개 실패" if fail else ""))

st.divider()

# ── 로컬 폴더 ──────────────────────────────────────────────────────────────────
st.subheader("🗂️ 로컬 폴더 일괄 저장")
st.caption(f"`.env`의 `LOCAL_FOLDER_PATH` 경로에 있는 문서를 전부 저장합니다.")
if st.button("로컬 폴더 ingest"):
    with st.spinner("처리 중..."):
        try:
            res = httpx.post(f"{BACKEND_URL}/ingest/local", timeout=120)
            if res.status_code == 200:
                d = res.json()
                st.success(
                    f"✅ {d['files_processed']}개 파일, {d['chunks_ingested']}개 청크 저장"
                    + (f" ({d['files_skipped']}개 스킵)" if d["files_skipped"] else "")
                )
            else:
                st.error(res.json().get("detail", res.text))
        except Exception as e:
            st.error(f"오류: {e}")

st.divider()

# ── Notion ─────────────────────────────────────────────────────────────────────
st.subheader("📝 Notion")
st.caption("Integration이 공유된 모든 페이지를 가져옵니다.")
if st.button("Notion 동기화"):
    with st.spinner("Notion 페이지 가져오는 중... (페이지 수에 따라 수십 초 소요)"):
        try:
            res = httpx.post(f"{BACKEND_URL}/ingest/notion", timeout=180)
            if res.status_code == 200:
                d = res.json()
                st.success(
                    f"✅ {d['pages_processed']}개 페이지, {d['chunks_ingested']}개 청크 저장"
                    + (f" ({d['pages_skipped']}개 스킵)" if d["pages_skipped"] else "")
                )
            elif res.status_code == 503:
                st.error(res.json().get("detail"))
                st.code("NOTION_API_KEY=ntn_... # .env에 추가 후 docker 재시작")
            else:
                st.error(res.json().get("detail", res.text))
        except Exception as e:
            st.error(f"오류: {e}")

st.divider()

# ── Google Drive ───────────────────────────────────────────────────────────────
st.subheader("☁️ Google Drive")

col1, col2 = st.columns([3, 1])
folder_id = col1.text_input(
    "폴더 ID (선택)",
    placeholder="비워두면 Drive 전체 검색 (URL의 /folders/... 부분)",
)

if col2.button("Drive 동기화", use_container_width=True):
    with st.spinner("Google Drive 파일 가져오는 중..."):
        try:
            params = {"folder_id": folder_id} if folder_id.strip() else {}
            res = httpx.post(f"{BACKEND_URL}/ingest/gdrive", params=params, timeout=300)
            if res.status_code == 200:
                d = res.json()
                st.success(
                    f"✅ {d['pages_processed']}개 파일, {d['chunks_ingested']}개 청크 저장"
                    + (f" ({d['pages_skipped']}개 스킵)" if d["pages_skipped"] else "")
                )
            elif res.status_code == 503:
                st.error(res.json().get("detail"))
                st.info("터미널에서 `python scripts/gdrive_auth.py` 실행 후 다시 시도하세요.")
            else:
                st.error(res.json().get("detail", res.text))
        except Exception as e:
            st.error(f"오류: {e}")
