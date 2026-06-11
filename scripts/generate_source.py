#!/usr/bin/env python3
"""Generate an AltStore source.json from config.json.

Two modes per app:
  - "releases": pull versions automatically from a GitHub repo's Releases (default)
  - "static":   use an explicit versions list you write in config.json

AltStore reads versions[0] as the latest, so the newest release is always first.
"""
import json
import os
import re
import urllib.request
from datetime import datetime, timezone

GITHUB_API = "https://api.github.com"


def gh_get(url):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "altstore-source-generator",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def versions_from_releases(repo, pattern):
    pat = re.compile(pattern)
    out = []
    releases = gh_get(f"{GITHUB_API}/repos/{repo}/releases?per_page=100")
    for rel in releases:
        if rel.get("draft"):
            continue
        asset = next((a for a in rel.get("assets", []) if pat.search(a["name"])), None)
        if not asset:
            continue
        ver = (rel.get("tag_name") or "").lstrip("v") or "0.0"
        date = (rel.get("published_at") or "")[:10] or \
            datetime.now(timezone.utc).strftime("%Y-%m-%d")
        out.append({
            "version": ver,
            "date": date,
            "downloadURL": asset["browser_download_url"],
            "size": asset["size"],
        })
    # GitHub returns releases newest-first already; keep that order.
    return out


def build_app(app):
    meta = {k: app[k] for k in (
        "name", "bundleIdentifier", "developerName",
        "localizedDescription", "iconURL",
    ) if k in app}

    src = app.get("source", {})
    mode = src.get("mode", "releases")
    if mode == "releases":
        versions = versions_from_releases(
            src["repo"], src.get("ipaAssetPattern", r"\.ipa$"))
    else:  # static
        versions = src.get("versions", [])

    for v in versions:
        v.setdefault("minOSVersion", app.get("minOSVersion", "14.0"))

    meta["versions"] = versions
    return meta


def main():
    with open("config.json") as f:
        cfg = json.load(f)

    source = {"name": cfg["name"], "identifier": cfg["identifier"]}
    for k in ("iconURL", "headerURL", "tintColor", "subtitle", "description", "website"):
        if cfg.get(k):
            source[k] = cfg[k]

    source["apps"] = [build_app(a) for a in cfg.get("apps", [])]

    with open("source.json", "w") as f:
        json.dump(source, f, indent=2)
    print(f"Wrote source.json with {len(source['apps'])} app(s)")


if __name__ == "__main__":
    main()
