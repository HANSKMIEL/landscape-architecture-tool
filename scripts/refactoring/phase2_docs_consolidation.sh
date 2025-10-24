#!/bin/bash
# V1.00D Refactoring Implementation Script - Phase 2
# Documentation Consolidation
# 
# This script implements Phase 2 of the refactoring plan
# Run from repository root: bash scripts/refactoring/phase2_docs_consolidation.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Phase 2: Documentation Consolidation                     ║${NC}"
echo -e "${BLUE}║  V1.00D Branch Refactoring                                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Safety check
if [ ! -d ".git" ]; then
    echo -e "${RED}Error: Must run from repository root${NC}"
    exit 1
fi

echo -e "${BLUE}Current documentation state:${NC}"
echo "  • docs/: $(find docs/ -name "*.md" 2>/dev/null | wc -l) markdown files"
echo "  • _internal/docs/: $(find _internal/docs/ -name "*.md" 2>/dev/null | wc -l) markdown files"
echo "  • _internal/documentation/: $(find _internal/documentation/ -name "*.md" 2>/dev/null | wc -l) markdown files"
echo "  • archive/: ~1000+ markdown files (massive duplicates)"
echo "  • .manus/: Temporary handoff files"
echo ""

# Ask for confirmation
echo -e "${YELLOW}This will:${NC}"
echo "  1. Move unique content from _internal/docs/ to docs/"
echo "  2. Move _internal/documentation/ content to docs/"
echo "  3. Compress archive/packages/ to save space"
echo "  4. Add .manus/ to .gitignore (temporary files)"
echo "  5. Create consolidated structure"
echo ""
read -p "Continue? [y/N]: " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cancelled."
    exit 0
fi

# Phase 2a: Merge _internal/docs/ into docs/
echo -e "${BLUE}Merging _internal/docs/ into docs/...${NC}"

# Create target directories in docs/ if they don't exist
mkdir -p docs/architecture
mkdir -p docs/api
mkdir -p docs/development
mkdir -p docs/guides

# Move unique _internal/docs/ content
if [ -d "_internal/docs/issues" ]; then
    echo "  • Moving _internal/docs/issues/ to docs/development/"
    git mv _internal/docs/issues docs/development/ 2>/dev/null || mv _internal/docs/issues docs/development/
fi

if [ -d "_internal/docs/pipeline" ]; then
    echo "  • Moving _internal/docs/pipeline/ to docs/deployment/"
    git mv _internal/docs/pipeline docs/deployment/ 2>/dev/null || mv _internal/docs/pipeline docs/deployment/
fi

if [ -d "_internal/docs/guides" ]; then
    echo "  • Moving _internal/docs/guides/ to docs/"
    git mv _internal/docs/guides/* docs/guides/ 2>/dev/null || mv _internal/docs/guides/* docs/guides/
fi

# Move standalone files from _internal/docs/
echo "  • Moving unique _internal/docs/ files to docs/architecture/"
for file in _internal/docs/*.md; do
    if [ -f "$file" ]; then
        basename=$(basename "$file")
        # Check if file doesn't already exist in docs/
        if [ ! -f "docs/$basename" ] && [ ! -f "docs/architecture/$basename" ]; then
            git mv "$file" docs/architecture/ 2>/dev/null || mv "$file" docs/architecture/
        fi
    fi
done

# Phase 2b: Merge _internal/documentation/ into docs/
echo -e "${BLUE}Merging _internal/documentation/ into docs/...${NC}"

if [ -d "_internal/documentation/deployment" ]; then
    echo "  • Moving _internal/documentation/deployment/ files..."
    for file in _internal/documentation/deployment/*.md; do
        if [ -f "$file" ]; then
            basename=$(basename "$file")
            if [ ! -f "docs/deployment/$basename" ]; then
                git mv "$file" docs/deployment/ 2>/dev/null || mv "$file" docs/deployment/
            fi
        fi
    done
fi

if [ -d "_internal/documentation/development" ]; then
    echo "  • Moving _internal/documentation/development/ files..."
    for file in _internal/documentation/development/*.md; do
        if [ -f "$file" ]; then
            basename=$(basename "$file")
            if [ ! -f "docs/development/$basename" ]; then
                git mv "$file" docs/development/ 2>/dev/null || mv "$file" docs/development/
            fi
        fi
    done
fi

# Phase 2c: Compress archive/packages/ 
echo -e "${BLUE}Compressing archive/packages/...${NC}"

if [ -d "archive/packages/v1.00" ]; then
    echo "  • Compressing archive/packages/v1.00/ (~3.1MB)"
    tar -czf archive/packages/v1.00-archived.tar.gz -C archive/packages v1.00
    rm -rf archive/packages/v1.00
    echo "    ✓ Compressed to v1.00-archived.tar.gz"
fi

if [ -d "archive/packages/v1.00D" ]; then
    echo "  • Compressing archive/packages/v1.00D/ (~3.1MB)"
    tar -czf archive/packages/v1.00D-archived.tar.gz -C archive/packages v1.00D
    rm -rf archive/packages/v1.00D
    echo "    ✓ Compressed to v1.00D-archived.tar.gz"
fi

# Phase 2d: Add .manus/ to .gitignore
echo -e "${BLUE}Adding .manus/ to .gitignore...${NC}"

if ! grep -q "^\.manus/$" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# Manus temporary handoff files" >> .gitignore
    echo ".manus/" >> .gitignore
    echo "  ✓ Added .manus/ to .gitignore"
else
    echo "  • .manus/ already in .gitignore"
fi

# Phase 2e: Clean up empty directories
echo -e "${BLUE}Cleaning up empty directories...${NC}"

find _internal/docs/ -type d -empty -delete 2>/dev/null || true
find _internal/documentation/ -type d -empty -delete 2>/dev/null || true

# Remove _internal/ directories if mostly empty
if [ -d "_internal/docs" ] && [ $(find _internal/docs -type f | wc -l) -lt 5 ]; then
    echo "  • Removing mostly empty _internal/docs/"
    rm -rf _internal/docs
fi

if [ -d "_internal/documentation" ] && [ $(find _internal/documentation -type f | wc -l) -lt 3 ]; then
    echo "  • Removing mostly empty _internal/documentation/"
    rm -rf _internal/documentation
fi

# Phase 2f: Create documentation index
echo -e "${BLUE}Creating documentation index...${NC}"

cat > docs/README.md << 'DOCINDEX'
# Documentation Index

Welcome to the Landscape Architecture Tool documentation!

## 📚 Documentation Structure

### 🚀 Getting Started
- [VPS Deployment Instructions](VPS_DEPLOYMENT_INSTRUCTIONS.md)
- [Quick VPS Deploy Guide](QUICK_VPS_DEPLOY.md)
- [User Instructions](INSTRUCTIONS_FOR_USER.txt)

### 🏗️ Architecture & Design
- [Architecture Documentation](architecture/)
- [API Documentation](api/)

### 📖 Development
- [Development Guides](development/)
- [Issue Tracking](development/issues/)
- [Contributing Guidelines](development/CONTRIBUTING.md)

### 🚢 Deployment
- [Deployment Guides](deployment/)
- [VPS Deployment](deployment/VPS_DEPLOYMENT_INSTRUCTIONS.md)
- [Pipeline Documentation](deployment/pipeline/)

### 📝 Planning & Roadmaps
- [Planning Documents](planning/)
- [Production Readiness](planning/PRODUCTION_READINESS_CHECKLIST.md)

### 💡 Solutions & Fixes
- [Solution Reports](solutions/)
- [Refactoring Analysis](solutions/V1_00D_REFACTORING_ANALYSIS.md)
- [VPS Deployment Solution](solutions/VPS_DEPLOYMENT_SOLUTION.md)

### 📘 Guides
- [Implementation Guides](guides/)
- [N8n Integration](guides/)

## 📊 Reports

Analysis and validation reports are located in the `/reports` directory:
- [Analysis Reports](/reports/analysis/)
- [Validation Reports](/reports/validation/)

## 🔧 Scripts

Utility scripts are organized in the `/scripts` directory:
- [Testing Scripts](/scripts/testing/)
- [Analysis Scripts](/scripts/analysis/)
- [Deployment Scripts](/scripts/deployment/)

---

**Last Updated**: October 1, 2025  
**Branch**: V1.00D (Development)
DOCINDEX

echo ""
echo -e "${GREEN}✅ Phase 2 Complete!${NC}"
echo ""
echo -e "${BLUE}Summary of changes:${NC}"
echo "  • Merged _internal/docs/ into docs/"
echo "  • Merged _internal/documentation/ into docs/"
echo "  • Compressed archive/packages/ (~6MB saved)"
echo "  • Added .manus/ to .gitignore"
echo "  • Created documentation index"
echo "  • Cleaned up empty directories"
echo ""
echo -e "${BLUE}Documentation structure after consolidation:${NC}"
echo "  • docs/ now contains all documentation"
echo "  • _internal/ reduced significantly"
echo "  • archive/ compressed (saved ~6MB)"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review changes: git status"
echo "  2. Check docs/README.md for new index"
echo "  3. Commit changes: git add -A && git commit -m 'refactor: Phase 2 - Documentation consolidation'"
echo "  4. Run Phase 3: Workflow optimization (optional)"
echo ""
