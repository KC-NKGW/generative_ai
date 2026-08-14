import json
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

REQUEST_TIMEOUT = 5
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
MAX_BYTES = 3 * 1024 * 1024


def _address_to_string(address):
    if isinstance(address, str):
        text = address.strip()
        return text or None
    if isinstance(address, dict):
        parts = [
            address.get("addressRegion"),
            address.get("addressLocality"),
            address.get("streetAddress"),
        ]
        parts = [p.strip() for p in parts if isinstance(p, str) and p.strip()]
        if parts:
            return "".join(parts)
    return None


def _location_from_jsonld(soup):
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or script.get_text() or "")
        except (ValueError, TypeError):
            continue

        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            graph = item.get("@graph")
            nodes = graph if isinstance(graph, list) else [item]
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                location = _address_to_string(node.get("address"))
                if location:
                    return location
    return None


def _location_from_og_business_tags(soup):
    def tag_content(prop):
        tag = soup.find("meta", attrs={"property": prop})
        return tag["content"].strip() if tag and tag.get("content") else None

    parts = [
        tag_content("business:contact_data:region"),
        tag_content("business:contact_data:locality"),
        tag_content("business:contact_data:street_address"),
    ]
    parts = [p for p in parts if p]
    return "".join(parts) if parts else None


def fetch_url_metadata(url):
    if not url or not url.startswith(("http://", "https://")):
        return {"ok": False}

    try:
        resp = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
            stream=True,
        )
        resp.raise_for_status()

        content_type = resp.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            return {"ok": False}

        chunks = []
        total = 0
        for chunk in resp.iter_content(chunk_size=8192):
            chunks.append(chunk)
            total += len(chunk)
            if total >= MAX_BYTES:
                break
        html = b"".join(chunks)
        final_url = resp.url
        # Prefer the charset declared in the HTTP header (reliable here since
        # requests parses it from Content-Type); BeautifulSoup's own byte-sniffing
        # heuristic can misfire on short/JSON-heavy pages and produce mojibake.
        encoding = resp.encoding if resp.encoding and resp.encoding.lower() != "iso-8859-1" else "utf-8"
    except requests.exceptions.RequestException:
        return {"ok": False}

    try:
        soup = BeautifulSoup(html.decode(encoding, errors="replace"), "html.parser")
    except Exception:
        return {"ok": False}

    def meta(*names, attr="property"):
        for name in names:
            tag = soup.find("meta", attrs={attr: name})
            if tag and tag.get("content"):
                return tag["content"].strip()
        return None

    title = meta("og:title")
    if not title and soup.title and soup.title.string:
        title = soup.title.string.strip()
    description = meta("og:description") or meta("description", attr="name")
    image = meta("og:image")
    if image:
        image = urljoin(final_url, image)

    try:
        location = _location_from_jsonld(soup) or _location_from_og_business_tags(soup)
    except Exception:
        location = None

    if not title and not image and not description and not location:
        return {"ok": False}

    return {
        "ok": True,
        "title": title,
        "image": image,
        "description": description,
        "location": location,
    }
