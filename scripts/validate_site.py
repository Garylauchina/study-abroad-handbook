"""Check built internal links, anchors, assets and search coverage."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import sys

BASE = "/study-abroad-handbook/"
ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "site").resolve()


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids = set()
        self.links = []
        self.text = []
        self.feed(source)

    def handle_data(self, data):
        self.text.append(data)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("name"):
            self.ids.add(attrs["name"])
        field = "href" if tag in ("a", "link") else "src" if tag in ("script", "img") else None
        if field and attrs.get(field):
            self.links.append(attrs[field])


pages = {p.resolve(): Page(p.read_text()) for p in ROOT.rglob("*.html")}
errors = []
checked = 0
for path, page in pages.items():
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            if url.netloc.lower() != "garylauchina.github.io" or not url.path.startswith(BASE):
                continue
        target_path = unquote(url.path)
        if target_path.startswith(BASE):
            target = ROOT / target_path[len(BASE):]
        elif target_path.startswith("/"):
            errors.append(f"{path.relative_to(ROOT)}: root path misses project prefix: {link}")
            continue
        else:
            target = path.parent / target_path if target_path else path
        if target.is_dir():
            target /= "index.html"
        target = target.resolve()
        checked += 1
        if not target.is_relative_to(ROOT) or not target.exists():
            errors.append(f"{path.relative_to(ROOT)}: missing {link}")
        elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            errors.append(f"{path.relative_to(ROOT)}: missing anchor {link}")

index = json.loads((ROOT / "search/search_index.json").read_text())
uk_text = "".join(pages[ROOT / "destinations/uk/index.html"].text)
if "A-level 为 A*AA，其中数学 A*" not in uk_text:
    errors.append("UK chapter: A-level grade asterisks were lost during Markdown rendering")
locations = {doc["location"].split("#")[0] for doc in index["docs"]}
for route in ("start/undergraduate/", "destinations/uk/", "tools/budget/", "tools/compare/"):
    if route not in locations:
        errors.append(f"Search index misses {route}")
search_text = " ".join(d.get("text", "") for d in index["docs"])
for term in ("预算", "高考", "Sheffield", "UCAS"):
    if term not in search_text:
        errors.append(f"Search text misses {term}")
if errors:
    print("\n".join(errors))
    raise SystemExit(1)
print(f"Validated {len(pages)} HTML pages, {checked} internal references and {len(index['docs'])} search entries")
