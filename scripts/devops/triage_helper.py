"""Utility to map changed files to development categories and guardrails.

Usage examples:
    python scripts/devops/triage_helper.py src/routes/plants.py frontend/src/App.jsx
    python scripts/devops/triage_helper.py --list-categories
    python scripts/devops/triage_helper.py --format json src/routes/main.py

The output highlights:
- matched categories for the provided file paths
- guardrail instruction documents to review
- recommended commands/tests per category
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency
    yaml = None


CATEGORY_MAP_PATH = Path(__file__).resolve().parents[2] / "config" / "category_map.yml"


@dataclass
class Category:
    key: str
    name: str
    instruction_file: Path
    instruction_display: str
    description: str
    patterns: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)

    def as_dict(self) -> Mapping[str, object]:
        return {
            "key": self.key,
            "name": self.name,
            "instruction_file": str(self.instruction_file),
            "instruction_display": self.instruction_display,
            "description": self.description,
            "patterns": self.patterns,
            "commands": self.commands,
        }


def load_category_map(path: Path) -> Mapping[str, Category]:
    if not path.exists():
        raise FileNotFoundError(f"Category map not found at {path}")

    if yaml is None:
        raise RuntimeError("PyYAML is required to parse category_map.yml. Install it or add it to the environment.")

    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    repo_root = path.resolve().parent.parent

    categories: dict[str, Category] = {}
    for key, entry in raw.get("categories", {}).items():
        instruction_file = Path(entry.get("instruction_file", ""))
        if instruction_file and not instruction_file.is_absolute():
            instruction_file = (repo_root / instruction_file).resolve()

        display_path = instruction_file
        try:
            display_path = instruction_file.relative_to(repo_root)
        except ValueError:
            pass

        categories[key] = Category(
            key=key,
            name=entry.get("name", key.title()),
            instruction_file=instruction_file,
            instruction_display=str(display_path).replace("\\", "/"),
            description=entry.get("description", ""),
            patterns=list(entry.get("patterns", []) or []),
            commands=list(entry.get("commands", []) or []),
        )
    return categories


def match_categories(paths: Sequence[Path], categories: Mapping[str, Category]) -> Mapping[str, list[Path]]:
    from fnmatch import fnmatch

    matches: dict[str, list[Path]] = {key: [] for key in categories}
    for file_path in paths:
        normalized = Path(file_path)
        rel = normalized
        if normalized.is_absolute():
            try:
                rel = normalized.relative_to(Path.cwd())
            except ValueError:
                rel = normalized
        str_rel = rel.as_posix()
        for key, category in categories.items():
            if any(fnmatch(str_rel, pattern) for pattern in category.patterns):
                matches[key].append(rel)
    return {key: value for key, value in matches.items() if value}


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Map file changes to development categories.")
    parser.add_argument(
        "paths",
        nargs="*",
        help="File paths (relative or absolute) to classify. When empty, the script will read file paths from stdin.",
    )
    parser.add_argument(
        "--category-map",
        default=str(CATEGORY_MAP_PATH),
        help="Path to category_map.yml (defaults to config/category_map.yml)",
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List all categories with descriptions and exit.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format for results (default: text)",
    )
    return parser.parse_args(argv)


def read_paths_from_stdin() -> list[Path]:
    raw = [line.strip() for line in sys.stdin if line.strip()]
    return [Path(item) for item in raw]


def print_categories(categories: Mapping[str, Category]) -> None:
    for category in categories.values():
        print(f"- {category.key}: {category.name}")
        print(f"  Description: {category.description}")
        print(f"  Instructions: {category.instruction_display}")
        if category.commands:
            print("  Commands:")
            for command in category.commands:
                print(f"    - {command}")
        print()


def output_text(results: Mapping[str, list[Path]], categories: Mapping[str, Category]) -> None:
    if not results:
        print("No categories matched the provided paths.")
        return

    for key, matched_paths in results.items():
        category = categories[key]
        print(f"Category: {category.name} ({key})")
        print(f"  Description: {category.description}")
        print(f"  Instruction file: {category.instruction_display}")
        print("  Matched files:")
        for path in matched_paths:
            print(f"    - {path.as_posix()}")
        if category.commands:
            print("  Recommended commands:")
            for command in category.commands:
                print(f"    - {command}")
        print()


def output_json(results: Mapping[str, list[Path]], categories: Mapping[str, Category]) -> None:
    payload = {
        key: {
            "category": categories[key].as_dict(),
            "files": [path.as_posix() for path in paths],
        }
        for key, paths in results.items()
    }
    print(json.dumps(payload, indent=2))


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    categories = load_category_map(Path(args.category_map))

    if args.list_categories:
        print_categories(categories)
        return 0

    paths: list[Path] = [Path(p) for p in args.paths] if args.paths else read_paths_from_stdin()

    if not paths:
        print("No file paths provided. Supply paths as arguments or via stdin.", file=sys.stderr)
        return 1

    matches = match_categories(paths, categories)
    if args.format == "json":
        output_json(matches, categories)
    else:
        output_text(matches, categories)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
