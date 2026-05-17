#!/usr/bin/env python3
"""Select an ollama/ollama Docker image tag and write it to .env."""
import json
import sys
import urllib.request
from pathlib import Path

IMAGE = "ollama/ollama"
GITHUB_REPO = "ollama/ollama"
ENV_FILE = Path(__file__).parent / ".env"
ENV_KEY = "OLLAMA_TAG"
TAGS_URL = f"https://hub.docker.com/v2/repositories/{IMAGE}/tags?page_size=100&ordering=last_updated"
RELEASES_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases?per_page=10"

GH_HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "select-ollama-tag"}


def fetch_docker_tags():
    req = urllib.request.Request(TAGS_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    return {t["name"]: t for t in data.get("results", [])}


def fetch_github_releases():
    try:
        req = urllib.request.Request(RELEASES_URL, headers=GH_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception:
        return []


def short_digest(tag):
    for img in tag.get("images", []):
        if img.get("architecture") == "amd64" and img.get("digest"):
            return img["digest"][:19]
    return ""


def format_body(body, indent="       ", max_lines=4, width=72):
    if not body:
        return ""
    lines = []
    for line in body.splitlines():
        line = line.rstrip()
        if not line or line.startswith("<!--"):
            continue
        if len(line) > width:
            line = line[:width - 3] + "..."
        lines.append(f"{indent}{line}")
        if len(lines) >= max_lines:
            lines.append(f"{indent}...")
            break
    return "\n".join(lines)


def pick(prompt, count):
    while True:
        try:
            raw = input(prompt).strip()
            idx = int(raw) - 1
            if 0 <= idx < count:
                return idx
            print(f"  Bitte eine Zahl zwischen 1 und {count} eingeben.")
        except (ValueError, EOFError):
            print("  Ungültige Eingabe.")


def main():
    print(f"Lade Tags von Docker Hub ({IMAGE}) ...")
    try:
        docker_tags = fetch_docker_tags()
    except Exception as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Lade Releases von GitHub ({GITHUB_REPO}) ...")
    releases = fetch_github_releases()

    options = []

    print()
    for rel in releases[:5]:
        tag_name = rel["tag_name"]  # e.g. "v0.6.8"
        # Ollama Docker tags use the version without "v" prefix (e.g. "0.6.8")
        docker_tag = docker_tags.get(tag_name) or docker_tags.get(tag_name.lstrip("v"))
        i = len(options) + 1
        options.append(docker_tag["name"] if docker_tag else tag_name)
        if docker_tag:
            size_mb = docker_tag.get("full_size", 0) // 1_000_000
            pushed = (docker_tag.get("tag_last_pushed") or "")[:10]
            digest = short_digest(docker_tag)
            meta = f"{pushed}  {size_mb:>5} MB  {digest}"
        else:
            meta = "(kein Docker-Tag gefunden)"
        pre = "  \033[33m[pre-release]\033[0m" if rel.get("prerelease") else ""
        display = docker_tag["name"] if docker_tag else tag_name
        print(f"  {i:2}.  \033[1;32m{display:<20}\033[0m  {meta}{pre}")
        print(f"       \033[1m{rel['name']}\033[0m")
        notes = format_body(rel.get("body", ""))
        if notes:
            print(notes)
        print()

    if not options:
        print("Keine Releases gefunden.")
        sys.exit(1)

    idx = pick(f"Tag auswählen [1-{len(options)}]: ", len(options))
    selected_tag = options[idx]

    if not ENV_FILE.exists():
        example = ENV_FILE.parent / ".env.example"
        ENV_FILE.write_text(example.read_text() if example.exists() else f"{ENV_KEY}=latest\n")
        print(f"\n{ENV_FILE.name} wurde neu angelegt.")

    current = ENV_FILE.read_text()
    current_value = next(
        (line.split("=", 1)[1].strip() for line in current.splitlines()
         if line.startswith(f"{ENV_KEY}=")),
        None,
    )

    if current_value == selected_tag:
        print(f"\n{ENV_KEY} ist bereits '{selected_tag}'. Nichts zu tun.")
        sys.exit(0)

    print(f"\n{ENV_FILE.name} wird aktualisiert:")
    print(f"  {current_value or '(nicht gesetzt)'}  →  {selected_tag}")

    confirm = input("Bestätigen? [y/N] ").strip().lower()
    if confirm != "y":
        print("Abgebrochen.")
        sys.exit(0)

    lines = current.splitlines(keepends=True)
    updated = False
    new_lines = []
    for line in lines:
        if line.startswith(f"{ENV_KEY}="):
            new_lines.append(f"{ENV_KEY}={selected_tag}\n")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f"{ENV_KEY}={selected_tag}\n")

    ENV_FILE.write_text("".join(new_lines))
    print(f"Fertig. {ENV_KEY}={selected_tag}")
    print(f"\nAusführen:  docker compose pull && docker compose up -d")


if __name__ == "__main__":
    main()
