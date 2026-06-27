from notion_client import Client


def _blocks_to_text(blocks: list) -> str:
    lines = []
    for block in blocks:
        btype = block.get("type")
        if not btype:
            continue
        rich = block.get(btype, {}).get("rich_text", [])
        text = "".join(rt.get("plain_text", "") for rt in rich)
        if text:
            lines.append(text)
    return "\n".join(lines)


def fetch_page_text(client: Client, page_id: str) -> str:
    blocks, cursor = [], None
    while True:
        resp = client.blocks.children.list(
            block_id=page_id, start_cursor=cursor, page_size=100
        )
        blocks.extend(resp["results"])
        if not resp.get("has_more"):
            break
        cursor = resp["next_cursor"]
    return _blocks_to_text(blocks)


def get_page_title(page: dict) -> str:
    for prop in page.get("properties", {}).values():
        if prop.get("type") == "title":
            return "".join(t.get("plain_text", "") for t in prop.get("title", []))
    return "Untitled"


def fetch_all_pages(api_key: str) -> list[dict]:
    """Returns list of {title, page_id, url, last_edited}"""
    client = Client(auth=api_key)
    pages, cursor = [], None
    while True:
        resp = client.search(
            filter={"property": "object", "value": "page"},
            start_cursor=cursor,
            page_size=100,
        )
        pages.extend(resp["results"])
        if not resp.get("has_more"):
            break
        cursor = resp["next_cursor"]

    results = []
    for page in pages:
        page_id = page["id"]
        title = get_page_title(page)
        text = fetch_page_text(client, page_id)
        if not text.strip():
            continue
        results.append({
            "page_id": page_id,
            "title": title,
            "text": text,
            "url": page.get("url", ""),
            "last_edited": page.get("last_edited_time", "")[:10],
        })
    return results
