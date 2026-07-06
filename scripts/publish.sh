#!/usr/bin/env bash
# Publish a skill from future-skills to future-server via the admin API.
# Usage: bash scripts/publish.sh <skill-path> [overwrite]
#
#   skill-path: path relative to repo root, e.g. "builtin/future-account"
#               or "third-party/my-skill".
#   overwrite:  "true" or "false" (default: false).
#
# Reads SKILL.md frontmatter (name, version, description) and skills.json
# (category, price, formats, limit, admin credentials). Creates a zip,
# then POSTs it to the platform admin API.

set -euo pipefail

SKILL_PATH="${1:?Usage: $0 <skill-path> [overwrite]}"
OVERWRITE="${2:-false}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_JSON="$REPO_ROOT/skills.json"

# ---- helpers ----

die() { echo "ERROR: $*" >&2; exit 1; }

# Parse a top-level key from the YAML frontmatter block (between first two ---).
# Handles single-line values and multi-line ">" blocks.
parse_frontmatter() {
    local file="$1"
    local key="$2"
    /usr/bin/awk -v key="$key" '
        /^---$/ { count++; next }
        count == 1 {
            if ($0 ~ "^" key ": *>") {
                in_ml = 1
                sub("^" key ": *> *", "")
                val = $0
                next
            }
            if (in_ml) {
                if ($0 ~ "^  ") { sub("^  ", " "); val = val $0; next }
                else { gsub(/^ +| +$/, "", val); print val; in_ml = 0 }
            }
            if ($0 ~ "^" key ":") { sub("^" key ": *", ""); print $0; exit }
        }
        count == 2 { exit }
    ' "$file"
}

# Parse version from SKILL.md frontmatter.
# Compatible with two formats:
#   1. Top-level:  version: 2.5.0  (Future skills)
#   2. Nested JSON: metadata: {"version": "1.3", ...}  (third-party skills)
parse_version() {
    local file="$1"
    local ver
    # 1. Try top-level version first
    ver=$(parse_frontmatter "$file" "version")
    if [ -n "$ver" ]; then
        echo "$ver"
        return
    fi
    # 2. Fallback: extract version from metadata block.
    #    Supports two formats:
    #      a. inline JSON:  metadata: {"version": "1.3", ...}
    #      b. multi-line YAML:
    #           metadata:
    #             version: "1.1"
    #             skill-author: "..."
    python3 -c "
import sys, json
text = open('$file').read()
parts = text.split('---')
if len(parts) >= 3:
    fm = parts[1]
    lines = fm.split('\n')
    in_meta = False
    meta_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('metadata:'):
            # Try inline JSON first
            rest = stripped.split(':', 1)[1].strip()
            if rest:
                try:
                    meta = json.loads(rest)
                    v = meta.get('version', '')
                    if v:
                        print(v)
                        break
                except Exception:
                    pass
            # Fall through to multi-line parsing
            in_meta = True
            continue
        if in_meta:
            if line and line[0] in (' ', '\t'):
                meta_lines.append(stripped)
            else:
                # End of metadata block
                in_meta = False
                # Parse collected lines as simple key: value pairs
                for ml in meta_lines:
                    if ml.startswith('version:'):
                        v = ml.split(':', 1)[1].strip().strip('\"')
                        if v:
                            print(v)
                            break
                break
" 2>/dev/null
}

# ---- main ----

SKILL_DIR="$REPO_ROOT/$SKILL_PATH"
[ -d "$SKILL_DIR" ] || die "Skill directory not found: $SKILL_PATH"

SKILL_MD="$SKILL_DIR/SKILL.md"
[ -f "$SKILL_MD" ] || die "SKILL.md not found in $SKILL_PATH"

SKILL_NAME=$(basename "$SKILL_PATH")

echo "Publishing $SKILL_PATH..."

# 1. Extract metadata from SKILL.md frontmatter
NAME=$(parse_frontmatter "$SKILL_MD" "name")
VERSION=$(parse_version "$SKILL_MD")
DESC=$(parse_frontmatter "$SKILL_MD" "description")
NAME_ZH=$(parse_frontmatter "$SKILL_MD" "name_zh")
DESC_ZH=$(parse_frontmatter "$SKILL_MD" "description_zh")

[ -n "$NAME" ]    || die "Could not parse 'name' from SKILL.md frontmatter"
[ -n "$VERSION" ] || die "Could not parse 'version' from SKILL.md frontmatter"
[ -n "$DESC" ]    || die "Could not parse 'description' from SKILL.md frontmatter"
[ -n "$NAME_ZH" ] || die "Could not parse 'name_zh' from SKILL.md frontmatter"
[ -n "$DESC_ZH" ] || die "Could not parse 'description_zh' from SKILL.md frontmatter"

# 2. Read skills.json config
[ -f "$SKILLS_JSON" ] || die "skills.json not found at $SKILLS_JSON"

CATEGORY=$(python3 -c "import json; d=json.load(open('$SKILLS_JSON')); print(d['$NAME']['category'])")
PRICE=$(python3 -c "import json; d=json.load(open('$SKILLS_JSON')); print(d['$NAME']['price'])")
FORMATS=$(python3 -c "import json; d=json.load(open('$SKILLS_JSON')); print(d['$NAME']['formats'])")
LIMIT=$(python3 -c "import json; d=json.load(open('$SKILLS_JSON')); print(d['$NAME']['limit'])")

# Read admin config (env vars override skills.json)
ADMIN_BASE_URL="${FUTURE_ADMIN_BASE_URL:-$(python3 -c "import json; d=json.load(open('$SKILLS_JSON')); print(d['admin']['base_url'])")}"
ADMIN_TOKEN="${FUTURE_ADMIN_TOKEN:-$(python3 -c "import json; d=json.load(open('$SKILLS_JSON')); print(d['admin']['token'])")}"

# 3. Create zip in temp location
ZIP_NAME="${NAME}-${VERSION}.zip"
ZIP_PATH="${TMPDIR:-/tmp}/${ZIP_NAME}"
rm -f "$ZIP_PATH"

echo "  Packaging $ZIP_NAME..."
cd "$SKILL_DIR"
/usr/bin/zip -r "$ZIP_PATH" . -x ".*" 2>/dev/null
cd "$REPO_ROOT"

echo "  Zip size: $(wc -c < "$ZIP_PATH" | tr -d ' ') bytes"

# 4. POST to admin API
API_URL="${ADMIN_BASE_URL}/admin/v1/skills/${NAME}/versions"

echo "  POST $API_URL (overwrite=${OVERWRITE})"
HTTP_CODE=$(curl -s -o /tmp/future-publish-response.json -w "%{http_code}" \
    -X POST "$API_URL" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -F "name=${NAME}" \
    -F "version=${VERSION}" \
    -F "description=${DESC}" \
    -F "name_zh=${NAME_ZH}" \
    -F "description_zh=${DESC_ZH}" \
    -F "category=${CATEGORY}" \
    -F "price=${PRICE}" \
    -F "formats=${FORMATS}" \
    -F "limit=${LIMIT}" \
    -F "overwrite=${OVERWRITE}" \
    -F "file=@${ZIP_PATH}" \
    2>/dev/null || die "Failed to connect to $API_URL. Is the platform service running?")

# 5. Clean up temp zip
rm -f "$ZIP_PATH"

# 6. Output result
echo ""
if [ "$HTTP_CODE" = "201" ]; then
    echo "=== Published ${NAME} v${VERSION} ==="
    python3 -m json.tool /tmp/future-publish-response.json 2>/dev/null || cat /tmp/future-publish-response.json
    echo ""
    echo "Upload complete."
elif [ "$HTTP_CODE" = "409" ]; then
    echo "=== Version already exists ==="
    python3 -m json.tool /tmp/future-publish-response.json 2>/dev/null || cat /tmp/future-publish-response.json
    die "Skill ${NAME} v${VERSION} already exists. Use 'make publish SKILL=${NAME} OVERWRITE=true' to replace it."
else
    echo "=== Upload failed (HTTP $HTTP_CODE) ==="
    python3 -m json.tool /tmp/future-publish-response.json 2>/dev/null || cat /tmp/future-publish-response.json
    rm -f /tmp/future-publish-response.json
    exit 1
fi

rm -f /tmp/future-publish-response.json
