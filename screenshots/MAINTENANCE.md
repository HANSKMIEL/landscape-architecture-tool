# Screenshot Maintenance Guide

## Overview

This guide explains how to maintain and update screenshots for the Landscape Architecture Tool frontend interfaces.

## Screenshot Organization

All screenshots are stored in the `/screenshots/` directory with the following structure:

```
screenshots/
├── README.md                                    # This file
├── dashboard/
│   └── dashboard-main-view-20250816.png       # Dashboard interface
├── suppliers/
│   └── suppliers-management-20250816.png       # Supplier management interface
├── plant-recommendations/
│   └── plant-recommendations-20250816.png      # Plant recommendation system
├── reports/
│   └── reports-analytics-20250816.png          # Reports and analytics
├── settings/
│   └── settings-placeholder-20250816.png       # Settings interface (placeholder)
├── products/
│   └── products-management-error-20250816.png  # Products management (error state)
├── plants/
│   └── plants-management-error-20250816.png    # Plants management (error state)
├── clients/
│   └── clients-management-error-20250816.png   # Clients management (error state)
└── projects/
    └── projects-management-error-20250816.png  # Projects management (error state)
```

## Screenshot Status

### ✅ Functional Screenshots (5 screens)
- **Dashboard**: Main business interface with analytics
- **Suppliers**: Supplier management with API connectivity issues
- **Plant Recommendations**: AI-powered plant selection (fully functional)
- **Reports**: Advanced business intelligence dashboard
- **Settings**: Configuration interface (placeholder)

### ❌ Error State Screenshots (4 screens)
- **Products**: Management interface with API connectivity errors
- **Plants**: Database interface with fetch errors
- **Clients**: Relationship management with connection failures
- **Projects**: Project management with API failures

## How to Update Screenshots

### 1. Set Up Local Environment

```bash
# Start backend server
cd /path/to/landscape-architecture-tool
python src/main.py

# Start frontend development server
cd frontend
npm run dev
```

### 2. Take New Screenshots

Use a browser automation tool like Playwright or manually capture screenshots:

- Navigate to each URL (`/dashboard`, `/suppliers`, etc.)
- Wait for page to load completely
- Take full-page screenshot
- Save with descriptive filename: `{section}-{description}-{date}.png`

### 3. Update Documentation

After capturing new screenshots:

1. Place new files in appropriate subdirectories
2. Update `SCREENSHOTS.md` with new file references
3. Update this README if structure changes
4. Commit changes to git

### 4. Naming Convention

Screenshots should follow this pattern:
- `{section}-{view-type}-{YYYYMMDD}.png`
- Example: `dashboard-main-view-20250816.png`

## Integration with Documentation

All screenshots are referenced in `SCREENSHOTS.md` using relative paths:

```markdown
![Description](screenshots/section/filename.png)
```

This ensures screenshots are version-controlled and available offline.

## Maintenance Schedule

- **After UI changes**: Update affected screenshots immediately
- **Monthly**: Review all screenshots for currency
- **Before releases**: Ensure all screenshots reflect current state
- **After bug fixes**: Update error state screenshots if issues resolved

## Tools Used

- **Playwright**: Browser automation for consistent screenshots
- **Manual capture**: For quick updates and verification

Last updated: August 16, 2025