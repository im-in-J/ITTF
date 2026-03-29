"""웹 크롤링 도구 — fetch_url, parse_html, parse_rss"""

import httpx
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET


async def fetch_url(url: str, headers: dict | None = None) -> dict:
    """URL에서 HTML을 가져온다."""
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if headers:
        default_headers.update(headers)

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            resp = await client.get(url, headers=default_headers)
            return {
                "success": True,
                "status_code": resp.status_code,
                "html": resp.text if resp.status_code == 200 else "",
                "url": str(resp.url),
                "error": None,
            }
    except Exception as e:
        return {
            "success": False,
            "status_code": 0,
            "html": "",
            "url": url,
            "error": str(e),
        }


def parse_html(html: str, selectors: dict | None = None) -> list[dict]:
    """HTML에서 기사 목록을 파싱한다.

    selectors 예시: {"container": "article", "title": "h2 a", "link": "h2 a"}
    셀렉터 없이 호출하면 일반적인 <a> 태그에서 제목+링크를 추출한다.
    """
    soup = BeautifulSoup(html, "lxml")
    articles = []

    if selectors and "container" in selectors:
        containers = soup.select(selectors["container"])
        for container in containers:
            title_el = container.select_one(selectors.get("title", "h2 a"))
            link_el = container.select_one(selectors.get("link", "a[href]"))
            summary_el = container.select_one(selectors.get("summary", "p"))

            title = title_el.get_text(strip=True) if title_el else ""
            link = ""
            if link_el and link_el.get("href"):
                link = link_el["href"]
            summary = summary_el.get_text(strip=True) if summary_el else ""

            if title and link:
                articles.append({
                    "title": title,
                    "url": link,
                    "summary": summary,
                })
    else:
        # 범용 파싱: <article>, <div class="post">, <h2>/<h3> 안의 링크
        for tag in soup.select("article, div.post, div.blog-post, div.entry"):
            heading = tag.find(["h1", "h2", "h3"])
            if not heading:
                continue
            link_el = heading.find("a") or tag.find("a")
            if not link_el or not link_el.get("href"):
                continue
            summary_el = tag.find("p")
            articles.append({
                "title": heading.get_text(strip=True),
                "url": link_el["href"],
                "summary": summary_el.get_text(strip=True) if summary_el else "",
            })

    return articles


def parse_rss(xml_text: str) -> list[dict]:
    """RSS/Atom 피드 XML을 파싱하여 기사 목록을 반환한다."""
    articles = []

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return articles

    # RSS 2.0 (<rss><channel><item>)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items = root.findall(".//item")
    if items:
        for item in items:
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            desc = item.findtext("description", "").strip()
            pub_date = item.findtext("pubDate", "").strip()
            if title and link:
                articles.append({
                    "title": title,
                    "url": link,
                    "summary": _strip_html(desc)[:500],
                    "published": pub_date,
                })
        return articles

    # Atom (<feed><entry>)
    entries = root.findall("atom:entry", ns) or root.findall("{http://www.w3.org/2005/Atom}entry")
    for entry in entries:
        title_el = entry.find("atom:title", ns) or entry.find("{http://www.w3.org/2005/Atom}title")
        link_el = entry.find("atom:link", ns) or entry.find("{http://www.w3.org/2005/Atom}link")
        summary_el = entry.find("atom:summary", ns) or entry.find("{http://www.w3.org/2005/Atom}summary")
        updated_el = entry.find("atom:updated", ns) or entry.find("{http://www.w3.org/2005/Atom}updated")

        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        link = link_el.get("href", "") if link_el is not None else ""
        summary = summary_el.text.strip() if summary_el is not None and summary_el.text else ""
        published = updated_el.text.strip() if updated_el is not None and updated_el.text else ""

        if title and link:
            articles.append({
                "title": title,
                "url": link,
                "summary": _strip_html(summary)[:500],
                "published": published,
            })

    return articles


def _strip_html(text: str) -> str:
    """HTML 태그를 제거한다."""
    if "<" in text:
        return BeautifulSoup(text, "lxml").get_text(strip=True)
    return text
