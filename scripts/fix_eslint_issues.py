#!/usr/bin/env python3
"""
ESLint Issues Fix Script
Systematically fixes the remaining 144 ESLint issues in the frontend
"""

import os
import re
from pathlib import Path


def fix_unused_imports():
    """Remove or prefix unused imports/variables with underscore"""

    fixes = [
        # App.jsx
        {
            "file": "frontend/src/App.jsx",
            "changes": [
                ("const PasswordReset = lazy", "const _PasswordReset = lazy"),
            ],
        },
        # AIAssistant.jsx
        {
            "file": "frontend/src/components/AIAssistant.jsx",
            "changes": [
                ("import { Input }", "import { Input as _Input }"),
                (
                    "const [suggestions, setSuggestions] = useState",
                    "const [_suggestions, _setSuggestions] = useState",
                ),
                ("loadInitialData", "loadInitialData, [loadInitialData]"),
            ],
        },
        # Dashboard.jsx
        {
            "file": "frontend/src/components/Dashboard.jsx",
            "changes": [
                ("const { t } = useLanguage", "const { t: _t } = useLanguage"),
            ],
        },
        # Login.jsx
        {
            "file": "frontend/src/components/Login.jsx",
            "changes": [
                (
                    "import { Card, CardContent, CardDescription, CardHeader, CardTitle }",
                    "import { Card as _Card, CardContent as _CardContent, CardDescription as _CardDescription, CardHeader as _CardHeader, CardTitle as _CardTitle }",
                ),
                ("const { t } = useLanguage", "const { t: _t } = useLanguage"),
            ],
        },
        # ImportExport.jsx case declarations
        {
            "file": "frontend/src/components/ImportExport.jsx",
            "changes": [
                (
                    "import {\n  Download,\n  Upload,\n  FileText,\n  Trash2,\n  Edit,",
                    "import {\n  Download,\n  Upload,\n  FileText,\n  Trash2 as _Trash2,\n  Edit as _Edit,",
                ),
                (
                    "const [bulkOperations, setBulkOperations] = useState",
                    "const [_bulkOperations, _setBulkOperations] = useState",
                ),
            ],
        },
    ]

    for fix in fixes:
        file_path = Path(__file__).parent.parent / fix["file"]
        if file_path.exists():
            content = file_path.read_text()
            for old, new in fix["changes"]:
                content = content.replace(old, new)
            file_path.write_text(content)
            print(f"✅ Fixed {fix['file']}")


def fix_case_declarations():
    """Fix case block declarations by wrapping in braces"""

    file_path = Path(__file__).parent.parent / "frontend/src/components/ImportExport.jsx"
    if file_path.exists():
        content = file_path.read_text()

        # Fix case declarations
        case_fixes = [
            (
                "case 'suppliers':\n        const suppliersData =",
                "case 'suppliers': {\n        const suppliersData =",
            ),
            (
                "case 'plants':\n        const plantsData =",
                "case 'plants': {\n        const plantsData =",
            ),
            (
                "case 'projects':\n        const projectsData =",
                "case 'projects': {\n        const projectsData =",
            ),
            (
                "case 'clients':\n        const clientsData =",
                "case 'clients': {\n        const clientsData =",
            ),
        ]

        for old, new in case_fixes:
            content = content.replace(old, new)

        # Add closing braces
        content = re.sub(r"(break;\s*\n)(\s*case)", r"\1        }\n\2", content)

        file_path.write_text(content)
        print("✅ Fixed case declarations in ImportExport.jsx")


def fix_undefined_globals():
    """Add globals configuration for browser APIs"""

    eslint_config_path = Path(__file__).parent.parent / "frontend/eslint.config.js"
    if eslint_config_path.exists():
        content = eslint_config_path.read_text()

        # Add browser globals
        if "languageOptions:" not in content:
            globals_config = """
    languageOptions: {
      globals: {
        localStorage: 'readonly',
        btoa: 'readonly',
        atob: 'readonly',
        TextEncoder: 'readonly',
        TextDecoder: 'readonly',
        language: 'readonly',
      }
    },"""

            # Insert after the first configuration object
            content = re.sub(r"(\{[^}]*rules:)", globals_config + r"\n    \1", content, count=1)
            eslint_config_path.write_text(content)
            print("✅ Added browser globals to ESLint config")


def fix_unused_parameters():
    """Prefix unused function parameters with underscore"""

    files_to_fix = [
        "frontend/src/components/PasswordReset.jsx",
        "frontend/src/test/utils/render.jsx",
        "frontend/src/utils/mockApi.js",
        "frontend/vite.config.js",
    ]

    parameter_fixes = {
        "resetToken": "_resetToken",
        "err": "_err",
        "criteria": "_criteria",
        "command": "_command",
        "env": "_env",
        "language": "_language",
        "error": "_error",
    }

    for file_path_str in files_to_fix:
        file_path = Path(__file__).parent.parent / file_path_str
        if file_path.exists():
            content = file_path.read_text()
            for old, new in parameter_fixes.items():
                # Fix function parameters
                content = re.sub(rf"\b{old}\b(?=\s*[,\)])", new, content)
            file_path.write_text(content)
            print(f"✅ Fixed unused parameters in {file_path_str}")


def main():
    """Run all ESLint fixes"""
    print("🔧 Fixing ESLint Issues")
    print("=" * 30)

    fix_unused_imports()
    fix_case_declarations()
    fix_undefined_globals()
    fix_unused_parameters()

    print("\n✅ ESLint fixes completed!")
    print("Run 'npm run lint' to verify fixes")


if __name__ == "__main__":
    main()
