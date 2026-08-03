from __future__ import annotations

import json
from pathlib import Path


def _flatten(tokens: dict, path: tuple[str, ...] = ()):
    for key in sorted(tokens):
        value = tokens[key]
        current_path = path + (key.replace("_", "-"),)
        if isinstance(value, dict):
            yield from _flatten(value, current_path)
        else:
            yield current_path, value


def render_css(tokens: dict) -> str:
    lines = [":root {"]
    for path, value in _flatten(tokens):
        rendered_value = str(value)
        if isinstance(value, str) and "typography-family" in "-".join(path) and " " in value:
            rendered_value = f"'{value}'"
        lines.append(f"  --brand-{'-'.join(path)}: {rendered_value};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> None:
    root = Path.cwd()
    source = root / "brand/tokens.json"
    destination = root / "brand/generated/tokens.css"
    tokens = json.loads(source.read_text(encoding="utf-8"))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_css(tokens), encoding="utf-8")


if __name__ == "__main__":
    main()
