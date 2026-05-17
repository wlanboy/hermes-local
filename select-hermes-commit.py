#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

REPO = "NousResearch/hermes-agent"
ENV_FILE = Path(__file__).parent / ".env"
ENV_KEY = "HERMES_COMMIT"


def gh(*args):
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"gh error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def resolve_tag_to_commit(tag):
    ref_data = json.loads(gh("api", f"repos/{REPO}/git/ref/tags/{tag}"))
    obj = ref_data["object"]
    if obj["type"] == "commit":
        return obj["sha"]
    # annotated tag — need one more hop
    tag_data = json.loads(gh("api", f"repos/{REPO}/git/tags/{obj['sha']}"))
    return tag_data["object"]["sha"]


def main():
    print(f"Fetching last 10 releases from {REPO}...")
    releases = json.loads(
        gh("release", "list", "--repo", REPO, "--limit", "10",
           "--json", "tagName,name,publishedAt,isPrerelease")
    )

    if not releases:
        print("No releases found.")
        sys.exit(1)

    print()
    for i, r in enumerate(releases, 1):
        pre = " [pre]" if r["isPrerelease"] else ""
        date = r["publishedAt"][:10]
        print(f"  {i:2}.  {r['tagName']:<20}  {r['name']:<30}  {date}{pre}")

    print()
    while True:
        try:
            raw = input(f"Select release [1-{len(releases)}]: ").strip()
            idx = int(raw) - 1
            if 0 <= idx < len(releases):
                break
            print(f"  Please enter a number between 1 and {len(releases)}.")
        except (ValueError, EOFError):
            print("  Invalid input.")

    selected = releases[idx]
    tag = selected["tagName"]
    print(f"\nResolving commit SHA for tag {tag} ...")
    commit = resolve_tag_to_commit(tag)
    print(f"  Commit: {commit}")

    current = ENV_FILE.read_text()
    current_value = next(
        (line.split("=", 1)[1].strip() for line in current.splitlines()
         if line.startswith(f"{ENV_KEY}=")),
        None,
    )
    if current_value == commit:
        print(f"\n{ENV_KEY} is already set to this commit. Nothing to do.")
        sys.exit(0)

    print(f"\nWill update {ENV_FILE.name}:")
    if current_value:
        print(f"  {current_value}  →  {commit}")
    else:
        print(f"  (not set)  →  {commit}")

    confirm = input("Confirm? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        sys.exit(0)

    lines = current.splitlines(keepends=True)
    updated = False
    new_lines = []
    for line in lines:
        if line.startswith(f"{ENV_KEY}="):
            new_lines.append(f"{ENV_KEY}={commit}\n")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.insert(0, f"{ENV_KEY}={commit}\n")

    ENV_FILE.write_text("".join(new_lines))
    print(f"Done. {ENV_KEY}={commit}")


if __name__ == "__main__":
    main()
