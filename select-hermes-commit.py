#!/usr/bin/env python3
"""Select a nousresearch/hermes-agent Docker image tag and write it to .env."""
import json
import sys
import urllib.request
from pathlib import Path

IMAGE = "nousresearch/hermes-agent"
ENV_FILE = Path(__file__).parent / ".env"
ENV_KEY = "HERMES_TAG"
TAGS_URL = f"https://hub.docker.com/v2/repositories/{IMAGE}/tags?page_size=10&ordering=last_updated"


def fetch_tags():
    req = urllib.request.Request(TAGS_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    return data.get("results", [])


def short_digest(tag):
    for img in tag.get("images", []):
        if img.get("architecture") == "amd64" and img.get("digest"):
            return img["digest"][:19]  # sha256:0123456789
    return ""


def main():
    print(f"Fetching tags for {IMAGE} from Docker Hub ...")
    try:
        tags = fetch_tags()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not tags:
        print("No tags found.")
        sys.exit(1)

    print()
    for i, tag in enumerate(tags, 1):
        name = tag["name"]
        size_mb = tag.get("full_size", 0) // 1_000_000
        pushed = (tag.get("tag_last_pushed") or "")[:10]
        digest = short_digest(tag)
        print(f"  {i:2}.  {name:<20}  {pushed}  {size_mb:>5} MB  {digest}")

    print()
    while True:
        try:
            raw = input(f"Select tag [1-{len(tags)}]: ").strip()
            idx = int(raw) - 1
            if 0 <= idx < len(tags):
                break
            print(f"  Please enter a number between 1 and {len(tags)}.")
        except (ValueError, EOFError):
            print("  Invalid input.")

    selected_tag = tags[idx]["name"]

    current = ENV_FILE.read_text()
    current_value = next(
        (line.split("=", 1)[1].strip() for line in current.splitlines()
         if line.startswith(f"{ENV_KEY}=")),
        None,
    )

    if current_value == selected_tag:
        print(f"\n{ENV_KEY} is already set to '{selected_tag}'. Nothing to do.")
        sys.exit(0)

    print(f"\nWill update {ENV_FILE.name}:")
    print(f"  {current_value or '(not set)'}  →  {selected_tag}")

    confirm = input("Confirm? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
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
        new_lines.insert(0, f"{ENV_KEY}={selected_tag}\n")

    ENV_FILE.write_text("".join(new_lines))
    print(f"Done. {ENV_KEY}={selected_tag}")
    print(f"\nRun:  docker compose pull && docker compose up -d")


if __name__ == "__main__":
    main()
