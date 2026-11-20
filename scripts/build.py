"""Validate local page assets and assemble the static site. No AWS calls."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import shutil

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

class AssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("src"):
            self.assets.append(attrs["src"])
        if tag == "link" and attrs.get("rel") == "stylesheet" and attrs.get("href"):
            self.assets.append(attrs["href"])

parser = AssetParser()
parser.feed((ROOT / "index.html").read_text())
for reference in parser.assets:
    url = urlsplit(reference)
    if url.scheme or url.netloc:
        raise ValueError("Unexpected external page asset: " + reference)
    asset = (ROOT / unquote(url.path).lstrip("/")).resolve()
    if not asset.is_relative_to(ROOT) or not asset.is_file():
        raise ValueError("Missing or invalid page asset: " + reference)

required = ("index.html", "styles.css", "app.js", "sdk/apigClient.js")
for name in required:
    if not (ROOT / name).is_file():
        raise ValueError("Missing required file: " + name)

# Copy only deployable assets. Never publish Git metadata, build scripts, or env files.
if DIST.exists():
    shutil.rmtree(DIST)
DIST.mkdir()
for name in ("index.html", "styles.css", "app.js"):
    shutil.copy2(ROOT / name, DIST / name)
shutil.copytree(ROOT / "sdk", DIST / "sdk", ignore=shutil.ignore_patterns(
    ".DS_Store", ".git", ".env", ".env.*", "__pycache__", "*.pyc", "README.md"
))
for reference in parser.assets:
    assert (DIST / unquote(urlsplit(reference).path).lstrip("/")).is_file()
print("Built static site with", len(parser.assets), "verified page assets.")
print("Upload the CONTENTS of dist/ to the frontend bucket root.")
