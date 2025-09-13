# Packages Directory

This directory contains version-specific packages of the Landscape Architecture Tool.

## Structure

```
packages/
├── v1.00/              # Protected stable release
│   ├── frontend/       # Frontend production build
│   ├── backend/        # Backend production code
│   ├── docs/          # V1.00 documentation
│   └── deploy/        # V1.00 deployment scripts
└── v1.00D/            # Development package
    ├── frontend/       # Development frontend
    ├── backend/        # Development backend
    ├── docs/          # Development documentation
    └── deploy/        # Development deployment scripts
```

## Version Management

### V1.00 (Protected Release)
- **Status**: Protected, production-ready
- **Purpose**: Stable deployment that powers the live VPS instance
- **Updates**: Only critical security patches and hotfixes
- **Protection**: Branch protection rules prevent direct modifications

### V1.00D (Development Package)
- **Status**: Active development
- **Purpose**: Ongoing feature development and improvements
- **Updates**: All new features, enhancements, and non-critical fixes
- **Testing**: Full CI/CD pipeline validation before merging

## Deployment Workflow

1. **Development**: Work on V1.00D branch
2. **Testing**: Full validation on V1.00D package
3. **Review**: Manual approval process for V1.00 updates
4. **Deployment**: Automated script copies tested changes from V1.00D to V1.00
5. **Release**: V1.00 package deployed to production

## Manual Update Process

Use the provided update script to promote changes from V1.00D to V1.00:

```bash
./scripts/update_v1_from_dev.sh
```

This script will:
- Run all tests on V1.00D
- Create a backup of current V1.00
- Copy validated changes to V1.00 package
- Update production deployment

---

**Important**: Never modify V1.00 package directly. All changes must flow through V1.00D development process.