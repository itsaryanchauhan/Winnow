#!/bin/bash
# deploy.sh - Winnow unified deploy script
# Usage: ./deploy.sh [patch|minor|major] [--skip-docker] [--skip-pypi] [--skip-hf]

set -e

# ─── Colors ───────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ─── Args ─────────────────────────────────────────────────
BUMP=${1:-patch}
SKIP_DOCKER=false
SKIP_PYPI=false
SKIP_HF=false

for arg in "$@"; do
  case $arg in
    --skip-docker) SKIP_DOCKER=true ;;
    --skip-pypi)   SKIP_PYPI=true ;;
    --skip-hf)     SKIP_HF=true ;;
  esac
done

# ─── Read current version from pyproject.toml ─────────────
CURRENT=$(grep '^version' pyproject.toml | head -1 | sed 's/version = "//;s/"//')
info "Current version: $CURRENT"

IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

case $BUMP in
  major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
  minor) MINOR=$((MINOR + 1)); PATCH=0 ;;
  patch) PATCH=$((PATCH + 1)) ;;
  *)     error "Invalid bump type: $BUMP. Use patch, minor, or major." ;;
esac

VERSION="$MAJOR.$MINOR.$PATCH"
success "New version: v$VERSION"

# ─── Confirm ──────────────────────────────────────────────
echo ""
echo "  Will deploy v$VERSION to:"
echo "    GitHub     → tag v$VERSION + push"
$SKIP_PYPI   || echo "    PyPI       → winnow-compress $VERSION"
$SKIP_DOCKER || echo "    Docker Hub → itsaryanchauhan/winnow:$VERSION + :latest"
$SKIP_HF     || echo "    HuggingFace → spaces/itsaryanchauhan/winnow"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
[[ $REPLY =~ ^[Yy]$ ]] || { info "Aborted."; exit 0; }

# ─── 1. Bump version ─────────────────────────────────────────
info "Bumping version in pyproject.toml..."
sed -i '' "s/^version = \"$CURRENT\"/version = \"$VERSION\"/" pyproject.toml
info "Bumping version in app/main.py..."
sed -i '' "s/version=\"[0-9]*\.[0-9]*\.[0-9]*\"/version=\"$VERSION\"/" app/main.py
success "Versions updated"

# ─── 2. GitHub - commit + tag + push ──────────────────────
info "Pushing to GitHub..."
git add -A
git commit -m "chore: release v$VERSION"
git tag "v$VERSION"
git push origin main
git push origin "v$VERSION"
success "GitHub: pushed v$VERSION"

# ─── 3. PyPI ──────────────────────────────────────────────
if [ "$SKIP_PYPI" = false ]; then
  info "Building and uploading to PyPI..."
  rm -rf dist/
  python -m build
  twine upload dist/*
  success "PyPI: winnow-compress $VERSION live"
else
  warn "Skipping PyPI"
fi

# ─── 4. Docker Hub ────────────────────────────────────────
if [ "$SKIP_DOCKER" = false ]; then
  info "Building Docker image (linux/amd64 for universally compatible deployment)..."
  docker build --platform linux/amd64 -t itsaryanchauhan/winnow:latest -t itsaryanchauhan/winnow:$VERSION .
  info "Pushing to Docker Hub..."
  docker push itsaryanchauhan/winnow:latest
  docker push itsaryanchauhan/winnow:$VERSION
  success "Docker Hub: itsaryanchauhan/winnow:$VERSION + :latest pushed"
else
  warn "Skipping Docker"
fi

# ─── 5. HuggingFace Space ─────────────────────────────────
if [ "$SKIP_HF" = false ]; then
  info "Deploying to HuggingFace Space..."
  HF_DIR=$(mktemp -d)
  git clone https://huggingface.co/spaces/itsaryanchauhan/winnow "$HF_DIR" --quiet
  rsync -a --delete \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='website' \
    --exclude='dist' \
    --exclude='*.egg-info' \
    --exclude='__pycache__' \
    --exclude='.env' \
    --exclude='benchmarks' \
    --exclude='tests' \
    ./ "$HF_DIR/"
  cd "$HF_DIR"
  git add -A
  git commit -m "release v$VERSION" --allow-empty
  git push
  cd - > /dev/null
  rm -rf "$HF_DIR"
  success "HuggingFace: Space updated to v$VERSION"
else
  warn "Skipping HuggingFace"
fi

# ─── Done ─────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Winnow v$VERSION deployed successfully 🌾${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  PyPI:        https://pypi.org/project/winnow-compress/$VERSION/"
echo "  Docker:      https://hub.docker.com/r/itsaryanchauhan/winnow"
echo "  HuggingFace: https://huggingface.co/spaces/itsaryanchauhan/winnow"
echo "  GitHub:      https://github.com/itsaryanchauhan/Winnow/releases/tag/v$VERSION"
echo ""
