from __future__ import annotations

import json
from pathlib import Path
import re
import sys

try:
    from scripts.generate_brand_tokens import render_css
except ImportError:
    from generate_brand_tokens import render_css

ALLOWED_STATUSES = {"approved", "proposed", "rejected", "deprecated"}
REQUIRED_FILES = (
    "BRAND.md",
    "DECISIONS.md",
    "MEMORY.md",
    "brand/strategy.md",
    "brand/messaging.md",
    "brand/identity.md",
    "brand/clearance.md",
    "brand/tokens.json",
    ".ai/context/brand.json",
    "brand/assets/manifest.json",
)


def _relative_luminance(hex_colour: str) -> float:
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", hex_colour):
        raise ValueError(f"Invalid hex colour: {hex_colour}")
    channels = [int(hex_colour[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(foreground), _relative_luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def validate_project(root: Path) -> list[str]:
    errors = [f"Missing required file: {path}" for path in REQUIRED_FILES if not (root / path).is_file()]
    decisions = root / "DECISIONS.md"
    if decisions.is_file():
        for line in decisions.read_text(encoding="utf-8").splitlines():
            if line.startswith("| D-"):
                columns = [value.strip() for value in line.strip("|").split("|")]
                if len(columns) >= 3 and columns[2] not in ALLOWED_STATUSES:
                    errors.append(f"Invalid decision status in DECISIONS.md: {columns[2]}")
    for relative in ("brand/tokens.json", ".ai/context/brand.json", "brand/assets/manifest.json"):
        path = root / relative
        if path.is_file():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as error:
                errors.append(f"Invalid JSON: {relative}: {error.msg}")
    token_source = root / "brand/tokens.json"
    generated_tokens = root / "brand/generated/tokens.css"
    if token_source.is_file() and generated_tokens.is_file():
        try:
            tokens = json.loads(token_source.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
        else:
            if generated_tokens.read_text(encoding="utf-8") != render_css(tokens):
                errors.append("Generated token drift: brand/generated/tokens.css")
    return errors


def main() -> int:
    errors = validate_project(Path.cwd())
    if errors:
        print("\n".join(errors))
        return 1
    print("Brand validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
