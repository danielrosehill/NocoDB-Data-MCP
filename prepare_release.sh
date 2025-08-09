#!/bin/bash

# NoCoDB Data MCP Server - Release Preparation Script
# This script prepares the repository for a new release

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if version argument is provided
if [ $# -eq 0 ]; then
    print_error "Usage: $0 <version> [--dry-run]"
    print_error "Example: $0 1.0.1"
    print_error "Example: $0 1.1.0 --dry-run"
    exit 1
fi

VERSION=$1
DRY_RUN=false

if [ "$2" = "--dry-run" ]; then
    DRY_RUN=true
    print_warning "Running in DRY RUN mode - no changes will be made"
fi

# Validate version format
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$ ]]; then
    print_error "Invalid version format. Use semantic versioning (e.g., 1.0.0, 1.0.0-beta.1)"
    exit 1
fi

print_status "Preparing release for version $VERSION"

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_warning "You are not on the main branch (current: $CURRENT_BRANCH)"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Aborted by user"
        exit 1
    fi
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    print_warning "You have uncommitted changes"
    git status --porcelain
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Aborted by user"
        exit 1
    fi
fi

# Check if tag already exists
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    print_error "Tag v$VERSION already exists"
    exit 1
fi

print_status "Running pre-release checks..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating one..."
    if [ "$DRY_RUN" = false ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -e ".[dev]"
    fi
else
    source venv/bin/activate
fi

# Run tests
print_status "Running tests..."
if [ "$DRY_RUN" = false ]; then
    if ! python -m pytest testing/ -v; then
        print_error "Tests failed. Please fix before releasing."
        exit 1
    fi
    print_success "All tests passed"
fi

# Run linting
print_status "Running code formatting check..."
if [ "$DRY_RUN" = false ]; then
    if ! python -m black --check src/; then
        print_warning "Code formatting issues found. Auto-fixing..."
        python -m black src/
        print_success "Code formatted"
    fi
fi

# Update version
print_status "Updating version to $VERSION..."
if [ "$DRY_RUN" = false ]; then
    python version_bump.py "$VERSION"
    print_success "Version updated in pyproject.toml and server.py"
fi

# Update changelog
print_status "Please update CHANGELOG.md with release notes for version $VERSION"
if [ "$DRY_RUN" = false ]; then
    read -p "Press Enter after updating CHANGELOG.md..."
fi

# Build package
print_status "Building package..."
if [ "$DRY_RUN" = false ]; then
    python -m build
    print_success "Package built successfully"
fi

# Commit changes
print_status "Committing version bump..."
if [ "$DRY_RUN" = false ]; then
    git add pyproject.toml src/nocodb_mcp/server.py CHANGELOG.md
    git commit -m "Bump version to $VERSION

- Updated version in pyproject.toml and server.py
- Updated CHANGELOG.md with release notes"
    print_success "Changes committed"
fi

# Create and push tag
print_status "Creating and pushing tag v$VERSION..."
if [ "$DRY_RUN" = false ]; then
    git tag -a "v$VERSION" -m "Release version $VERSION

See CHANGELOG.md for details."
    
    print_status "Pushing changes and tags to origin..."
    git push origin main
    git push origin "v$VERSION"
    print_success "Tag v$VERSION created and pushed"
fi

print_success "Release preparation complete!"
print_status "Next steps:"
echo "  1. GitHub Actions will automatically create a release"
echo "  2. Monitor the release workflow at: https://github.com/danielrosehill/NocoDB-Data-MCP/actions"
echo "  3. The release will be available at: https://github.com/danielrosehill/NocoDB-Data-MCP/releases"

if [ "$DRY_RUN" = true ]; then
    print_warning "DRY RUN completed - no actual changes were made"
fi
