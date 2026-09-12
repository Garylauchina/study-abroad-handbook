"""MkDocs hook: keep each page's custom styles, scripts and catalog data in sync."""
import hashlib
import json
from pathlib import Path
import posixpath
import re
import subprocess
from urllib.parse import urlsplit, urlunsplit

ATTR_URL = re.compile(r'(?P<attribute>\b(?:href|src|data-catalog-url))=(?P<quote>[\"\x27])(?P<url>.*?)(?P=quote)')


def retain_previous_assets(root, paths, repository):
    """Cached HTML must still find the public asset bytes from the preceding deploy.

    HEAD covers a local dirty preview; HEAD^ covers a clean CI release checkout.
    Only the explicitly configured public assets are read from Git.
    """
    for revision in ('HEAD', 'HEAD^'):
        for name in paths:
            url = urlsplit(name)
            if url.scheme or url.netloc:
                continue
            result = subprocess.run(['git', 'show', f'{revision}:docs/{url.path}'], cwd=repository, capture_output=True)
            if result.returncode:
                continue  # A new asset or a first commit has no preceding version.
            source = root / url.path
            digest = hashlib.sha256(result.stdout).hexdigest()[:12]
            previous = source.with_name(f'{source.stem}.{digest}{source.suffix}')
            previous.parent.mkdir(parents=True, exist_ok=True)
            previous.write_bytes(result.stdout)


def on_post_build(config):
    root = Path(config.site_dir)
    site_url = urlsplit(config.site_url)
    paths = list(config.extra_css) + [str(script) for script in config.extra_javascript]
    paths.append('assets/data/catalog-index.json')
    retain_previous_assets(root, paths, Path(__file__).resolve().parents[1])
    versions = {}
    for name in paths:
        url = urlsplit(name)
        if url.scheme or url.netloc:
            continue
        source = root / url.path
        content = source.read_bytes()
        digest = hashlib.sha256(content).hexdigest()[:12]
        versioned = source.with_name(f'{source.stem}.{digest}{source.suffix}')
        versioned.write_bytes(content)
        versions[url.path] = versioned.relative_to(root).as_posix()

    for page in root.rglob('*.html'):
        parent = page.parent.relative_to(root).as_posix()

        def replace(match):
            url = urlsplit(match['url'])
            if url.scheme or url.netloc:
                if (url.scheme, url.netloc) != (site_url.scheme, site_url.netloc):
                    return match[0]
            if url.path.startswith('/'):
                if not url.path.startswith(site_url.path):
                    return match[0]
                key = url.path[len(site_url.path):]
                versioned = site_url.path + versions.get(key, key)
            else:
                key = posixpath.normpath(posixpath.join(parent, url.path))
                if key not in versions:
                    return match[0]
                versioned = posixpath.relpath(versions[key], parent)
            if key not in versions:
                return match[0]
            value = urlunsplit(url._replace(path=versioned))
            return f'{match["attribute"]}={match["quote"]}{value}{match["quote"]}'

        page.write_text(ATTR_URL.sub(replace, page.read_text()))
    (root / 'assets/asset-manifest.json').write_text(json.dumps(versions, indent=2) + '\n')
