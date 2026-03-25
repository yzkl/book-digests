from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from src.schemas import Links


def update_page_param(url: str, new_page: int) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query["page"] = [str(new_page)]
    new_query = urlencode(query, doseq=True)

    return urlunparse(parsed._replace(query=new_query))


def make_pagination_links(url: str, page: int, size: int, total: int) -> Links:
    end = (page - 1) * size + size
    prev_url = update_page_param(url, page - 1) if page > 1 else None
    next_url = update_page_param(url, page + 1) if end < total else None

    return Links(prev=prev_url, next=next_url)
