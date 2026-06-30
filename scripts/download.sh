#!/usr/bin/env bash
# Download a skill from a GitHub tree URL into pending-review/ for review.
# Usage: bash scripts/download.sh <github-tree-url>
#
# Example:
#   bash scripts/download.sh https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/skills/database-lookup
#
# Downloads the entire directory into pending-review/<skill-name>/

set -euo pipefail

URL="${1:?Usage: $0 <github-tree-url>}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PENDING_DIR="$REPO_ROOT/pending-review"

die() { echo "ERROR: $*" >&2; exit 1; }

# ---- parse GitHub URL ----
# Expected format: https://github.com/<owner>/<repo>/tree/<branch>/<path...>
rest="${URL#https://github.com/}"
[ "$rest" != "$URL" ] || die "URL must start with https://github.com/"

OWNER="${rest%%/*}"; rest="${rest#*/}"
REPO="${rest%%/*}"; rest="${rest#*/}"
tree_kw="${rest%%/*}"; rest="${rest#*/}"
[ "$tree_kw" = "tree" ] || die "URL must contain /tree/<branch>/<path>"

BRANCH="${rest%%/*}"; rest="${rest#*/}"
REMOTE_PATH="$rest"
SKILL_NAME="$(basename "$REMOTE_PATH")"

[ -n "$OWNER" ] || die "Could not parse owner from URL"
[ -n "$REPO" ] || die "Could not parse repo from URL"
[ -n "$BRANCH" ] || die "Could not parse branch from URL"
[ -n "$REMOTE_PATH" ] || die "Could not parse path from URL"
[ -n "$SKILL_NAME" ] || die "Could not determine skill name from path"

DEST_DIR="$PENDING_DIR/$SKILL_NAME"
[ ! -d "$DEST_DIR" ] || die "Destination already exists: $DEST_DIR\nRemove it first or choose a different skill."

echo "Downloading skill '$SKILL_NAME'..."
echo "  Source: github.com/${OWNER}/${REPO}/tree/${BRANCH}/${REMOTE_PATH}"
echo "  Dest:   ${DEST_DIR#$REPO_ROOT/}"

mkdir -p "$DEST_DIR"

python3 - "$OWNER" "$REPO" "$BRANCH" "$REMOTE_PATH" "$DEST_DIR" <<'PYEOF'
import json, os, sys, subprocess, urllib.request

owner, repo, branch, remote_path, dest_dir = sys.argv[1:]

def detect_cmd():
    """Return the API fetch command to use: 'gh' or 'curl'."""
    r = subprocess.run(["which", "gh"], capture_output=True, text=True)
    if r.returncode == 0:
        # Verify gh is authenticated
        auth = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
        if auth.returncode == 0:
            return "gh"
    return "curl"

api_cmd = detect_cmd()

def api_get(path):
    url = f"/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    if api_cmd == "gh":
        r = subprocess.run(
            ["gh", "api", "-H", "Accept: application/vnd.github.v3+json", url],
            capture_output=True, text=True
        )
    else:
        full_url = f"https://api.github.com{url}"
        r = subprocess.run(
            ["curl", "-sS", "-H", "Accept: application/vnd.github.v3+json", full_url],
            capture_output=True, text=True
        )

    if r.returncode != 0:
        print(f"ERROR: fetch failed for {path}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"ERROR: GitHub API returned non-JSON for {path}", file=sys.stderr)
        print(f"  Response: {r.stdout[:500]}", file=sys.stderr)
        sys.exit(1)

def download_file(download_url, local_path):
    print(f"  -> {local_path}")
    full = os.path.join(dest_dir, local_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    urllib.request.urlretrieve(download_url, full)

def walk(remote_path, local_dir):
    data = api_get(remote_path)

    # API error response
    if isinstance(data, dict) and "message" in data and "name" not in data:
        msg = data["message"]
        print(f"ERROR: GitHub API error for '{remote_path}': {msg}", file=sys.stderr)
        if "rate limit" in msg.lower():
            if api_cmd == "curl":
                print(f"  Unauthenticated API rate limit hit. Run 'gh auth login' and try again.", file=sys.stderr)
            else:
                print(f"  Your gh token may have hit the rate limit or lacks permission.", file=sys.stderr)
        elif msg == "Not Found":
            print(f"  Check that the path exists in {owner}/{repo} on branch '{branch}'", file=sys.stderr)
        sys.exit(1)

    # Single file
    if isinstance(data, dict) and data.get("type") == "file":
        download_file(data["download_url"], f"{local_dir}/{data['name']}".lstrip("/"))
        return

    # Directory listing
    if isinstance(data, dict):
        data = [data]

    for item in data:
        if item.get("type") == "file":
            download_file(item["download_url"], f"{local_dir}/{item['name']}".lstrip("/"))
        elif item.get("type") == "dir":
            walk(item["path"], f"{local_dir}/{item['name']}")

walk(remote_path, "")
PYEOF

echo ""
echo "=== Downloaded $SKILL_NAME to ${DEST_DIR#$REPO_ROOT/} ==="
echo "Pending review. After approval, move to future/ or third-party/ and add to skills.json."
