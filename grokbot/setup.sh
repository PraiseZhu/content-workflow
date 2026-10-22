#!/usr/bin/env bash
# One-shot box setup for a fresh Grok Bot box (Linux). Idempotent: safe to re-run.
# Usage (from the repo root):  bash grokbot/setup.sh
# Optional env overrides: CW_HOME (default ~/content-work), FONT_DIR, SECRETS_DIR, SKIP_FONTS=1, SKIP_NODE=1
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CW_HOME="${CW_HOME:-$HOME/content-work}"
FONT_DIR="${FONT_DIR:-$HOME/.local/share/fonts}"
SECRETS_DIR="${SECRETS_DIR:-$HOME/.secrets}"
ENV_FILE="$HOME/.content-workflow.env"
say(){ printf '\n== %s\n' "$*"; }

say "1/8 env file -> $ENV_FILE"
cat > "$ENV_FILE" <<EOV
export CW_REPO="$REPO"
export WEWRITE_DIR="$REPO/skill/wewrite"
export CONTENT_ROOT="$CW_HOME/公众号"
export ARTICLES_DIR="$CW_HOME/articles"
export STYLE_LIBRARY_DIR="$CW_HOME/style-library/x-trending"
export FONT_DIR="$FONT_DIR"
export SECRETS_DIR="$SECRETS_DIR"
export X_SECRETS_DIR="$SECRETS_DIR/x"
export DEAI_RULES="$REPO/deai-rules"
export SIZES_JSON="$REPO/specs/image-sizes/sizes.json"
export STYLES_DIR="$REPO/renderer/article-image-styles"
export CHROMIUM="\${CHROMIUM:-\$(command -v chromium || command -v chromium-browser || command -v google-chrome || echo chromium)}"
export CHROME_PATH="\${CHROME_PATH:-\$(command -v google-chrome || command -v chromium || echo /usr/bin/google-chrome)}"
export PATH="$REPO/.venv/bin:\$PATH"
EOV
grep -q content-workflow.env "$HOME/.bashrc" 2>/dev/null || echo '[ -f ~/.content-workflow.env ] && . ~/.content-workflow.env' >> "$HOME/.bashrc"
. "$ENV_FILE"

say "2/8 directories"
mkdir -p "$CONTENT_ROOT"/{output/x,selections,preview,crosspost/x,automation/reports} "$ARTICLES_DIR/config" "$ARTICLES_DIR/early-human" "$STYLE_LIBRARY_DIR" "$SECRETS_DIR/x" "$SECRETS_DIR/wewrite"
chmod 700 "$SECRETS_DIR" "$SECRETS_DIR/x" "$SECRETS_DIR/wewrite"

say "3/8 seed content root from repo (never overwrites existing files)"
cp -rn "$REPO/content/." "$CONTENT_ROOT/"
[ -f "$STYLE_LIBRARY_DIR/index.md" ] || cp "$REPO/style-library/index.template.md" "$STYLE_LIBRARY_DIR/index.md"
for f in voice.md channels.yaml glossary.json style-profile.json voice-anchors.md; do cp -n "$REPO/config/$f" "$ARTICLES_DIR/config/$f"; done
if [ -d "$REPO/handoff" ]; then
  cp -n "$REPO/handoff/private-config/private-names.txt" "$REPO/config/private-names.txt"
  cp -n "$REPO/handoff/private-config/private-names.txt" "$ARTICLES_DIR/config/private-names.txt"
  cp -n "$REPO/handoff/private-config/blacklist.txt" "$CONTENT_ROOT/automation/blacklist.txt"
  cp -n "$REPO/handoff/history.yaml" "$CONTENT_ROOT/history.yaml"
  cp -n "$REPO"/handoff/selections/*.md "$CONTENT_ROOT/selections/" 2>/dev/null || true
  cp -n "$REPO"/handoff/early-human/*.md "$ARTICLES_DIR/early-human/"
  cp -n "$REPO"/handoff/fixtures/handoff-thin-en.md "$CONTENT_ROOT/output/x/" 2>/dev/null || true
  mkdir -p "$CONTENT_ROOT/exemplars" && cp -rn "$REPO/handoff/third-party/exemplars/." "$CONTENT_ROOT/exemplars/"
  mkdir -p "$REPO/skills/idea-outline/references" && cp -rn "$REPO/handoff/third-party/style-corpus" "$REPO/handoff/third-party/style-corpus-ak.md" "$REPO/skills/idea-outline/references/" 2>/dev/null || true
else
  cp -n "$REPO/config/private-names.example.txt" "$REPO/config/private-names.txt"
  cp -n "$REPO/config/private-names.example.txt" "$ARTICLES_DIR/config/private-names.txt"
fi
# wewrite expects these next to SKILL.md (same layout as the original symlinks)
cd "$WEWRITE_DIR"
mkdir -p "$CONTENT_ROOT/corpus" "$CONTENT_ROOT/lessons"
for n in output history.yaml playbook.md corpus lessons; do [ -e "$n" ] || [ -L "$n" ] || ln -s "$CONTENT_ROOT/$n" "$n"; done
[ -e references/exemplars ] || [ -L references/exemplars ] || ln -s "$CONTENT_ROOT/exemplars" references/exemplars
[ -e config.yaml ] || [ -L config.yaml ] || ln -s "$SECRETS_DIR/wewrite/config.yaml" config.yaml   # target created by the author, never by the bot
cd "$REPO"

say "4/8 python venv + deps"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r skill/wewrite/requirements.txt pytest

say "5/8 fonts"
if [ "${SKIP_FONTS:-0}" != 1 ] && [ ! -f "$FONT_DIR/misans/MiSans-Bold.ttf" ]; then
  mkdir -p "$FONT_DIR/misans"; tmp=$(mktemp -d)
  curl -fsSL --max-time 300 -o "$tmp/ms.zip" https://cdn.cnbj1.fds.api.mi-img.com/vipmlmodel/font/MiSans/MiSans.zip
  for w in Regular Medium Semibold Bold; do unzip -j -o -q "$tmp/ms.zip" "*/MiSans-$w.ttf" -d "$FONT_DIR/misans"; done
  rm -rf "$tmp"
fi
has_font(){ fc-list : family 2>/dev/null | grep -i "$1" >/dev/null; }
has_font 'Noto Sans CJK' || (sudo apt-get install -y -q fonts-noto-cjk >/dev/null 2>&1 || echo "WARN: install fonts-noto-cjk manually")
has_font '^Inter' || { mkdir -p "$FONT_DIR/inter"; t=$(mktemp -d); curl -fsSL --max-time 300 -o "$t/i.zip" https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip && unzip -j -o -q "$t/i.zip" 'extras/ttf/Inter-*.ttf' -d "$FONT_DIR/inter" || echo "WARN: install Inter manually"; rm -rf "$t"; }
has_font 'JetBrains Mono' || (sudo apt-get install -y -q fonts-jetbrains-mono >/dev/null 2>&1 || echo "WARN: install JetBrains Mono manually")
fc-cache -f >/dev/null 2>&1 || true

say "6/8 headless chrome + node renderer"
command -v "$CHROMIUM" >/dev/null 2>&1 || (sudo apt-get install -y -q chromium >/dev/null 2>&1 || echo "WARN: install chromium/google-chrome manually")
if [ "${SKIP_NODE:-0}" != 1 ] && command -v npm >/dev/null; then (cd renderer/html-render && npm install --silent >/dev/null); fi

say "7/8 tests"
.venv/bin/python specs/image-sizes/check_spec.py >/dev/null && echo "check_spec OK"
.venv/bin/python deai-lint/deai_lint.py test | tail -1
(cd skill/wewrite && ../../.venv/bin/python -m pytest -q toolkit scripts | tail -1)

say "8/8 render smoke test"
.venv/bin/python examples/sample-article/make_photos.py >/dev/null
.venv/bin/python renderer/article-image-template/lib/render.py examples/sample-article --check
.venv/bin/python renderer/article-image-template/lib/render.py examples/sample-article --only cover-wechat-2350x1000,header-x-2000x800 | tail -3
echo; echo "DONE. Run:  . ~/.content-workflow.env"
echo "Secrets are NOT set up by this script: the author enters them (see grokbot/MIGRATION.md step 6)."
