# Stronger at Home Stage 1 Rebuild and Hybrid Logo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the missing Stage 1 brand-system sources in the refreshed repository and create a validated proposed hybrid logo from the user-owned care-and-progression artwork.

**Architecture:** Human-readable Markdown and machine-readable JSON remain authoritative. Semantic JSON tokens generate CSS deterministically; a dependency-free Python validator enforces source presence, statuses, contrast, generated drift, font provenance and artwork integrity. The hybrid logo is built as editable SVG with no embedded raster content and stays proposed until Melanie Watsham explicitly approves it.

**Tech Stack:** Markdown, JSON, SVG 1.1, CSS custom properties, Python 3 standard library, `unittest`, official Google Fonts assets, SHA-256 provenance and local browser review.

## Global Constraints

- Treat `sources/` as read-only reference material.
- Treat `/Users/mwatsham/Documents/Codex/2026-08-03/i/outputs` as read-only owned source artwork.
- The user confirmed full ownership of that artwork on 2026-08-03.
- Public name `Stronger at Home Physiotherapy` remains `proposed` until clearance is recorded.
- Endorsement is `by Melanie Watsham`.
- Core message is `Experienced care. Personal progress. At home.`
- Primary audience is patients and older adults; professional referrers are secondary.
- Service area is a 10–15 mile radius around Epsom, Surrey.
- Lead proof is 20+ years of NHS experience; HCPC, CSP, AGILE and ATOCP wording remains verification-gated.
- Approved palette is Deep Navy `#203E55`, Pale Sky `#E8F1F6`, Warm Cream `#F7F2E8` and Warm Sand `#C3A26E`.
- Approved typography is Source Serif 4 for display/wordmark text and Atkinson Hyperlegible Next for body/functional text.
- Proposed identity architecture is a horizontal hybrid lockup: owned hand/person/steps artwork inside a simple open-doorway house outline, attached to the wordmark.
- Do not approve or export the house symbol as a standalone badge in Stage 1.
- Do not use an image model to reproduce logo geometry.
- Do not add patient, referral, website, social, uniform, vehicle or signage templates.
- Do not add external Python or Node dependencies.
- Ask for action-time approval immediately before downloading font files into the refreshed repository.
- Final public artwork must remain `proposed` until the user confirms Melanie Watsham explicitly approved it.
- `AGENTS.md` is already staged by the user and is outside this plan. Preserve its index state. Use path-scoped commits with `git commit --only` followed by the exact paths listed in each task so it is never included accidentally.

## File Map

| File | Responsibility |
|---|---|
| `BRAND.md` | Brand-system entry point, status and adoption boundary |
| `DECISIONS.md` | Approved/proposed/rejected/deprecated decision ledger |
| `MEMORY.md` | Durable rationale, execution notes and blockers |
| `brand/strategy.md` | Purpose, positioning, audiences, personality and constraints |
| `brand/messaging.md` | Message hierarchy, claims boundary and voice |
| `brand/identity.md` | Hybrid architecture, palette, typography and imagery rules |
| `brand/clearance.md` | Dated name, credential, font and artwork provenance checks |
| `.ai/context/brand.json` | Machine-readable facts, statuses, prohibitions and approval owner |
| `brand/tokens.json` | Semantic design-token source |
| `brand/generated/tokens.css` | Deterministically generated CSS |
| `brand/fonts/*` | Approved local fonts, OFL licences and provenance |
| `brand/assets/reference/*` | Immutable project copies of the user-owned source evidence |
| `brand/assets/source/logo-primary-hybrid.svg` | Proposed editable primary hybrid logo |
| `brand/assets/review/logo-hybrid-preview.html` | Primary-logo visual approval composition |
| `brand/assets/manifest.json` | Artwork paths, hashes, roles and approval states |
| `scripts/generate_brand_tokens.py` | Token-to-CSS generator |
| `scripts/validate_brand.py` | Source, token, font, manifest and SVG validator |
| `tests/test_brand_validation.py` | Validator and governance tests |
| `tests/test_token_generation.py` | Deterministic token-generation tests |

---

### Task 1: Rebuild authoritative brand sources and validation foundation

**Files:**
- Create: `BRAND.md`
- Create: `DECISIONS.md`
- Create: `MEMORY.md`
- Create: `brand/strategy.md`
- Create: `brand/messaging.md`
- Create: `brand/identity.md`
- Create: `brand/clearance.md`
- Create: `.ai/context/brand.json`
- Create: `scripts/__init__.py`
- Create: `scripts/validate_brand.py`
- Create: `tests/__init__.py`
- Create: `tests/test_brand_validation.py`

**Interfaces:**
- Consumes: `docs/superpowers/specs/2026-08-03-stronger-at-home-hybrid-logo-exploration-design.md` and approved decisions preserved in this plan's Global Constraints.
- Produces: `contrast_ratio(foreground: str, background: str) -> float`, `validate_project(root: Path) -> list[str]`, and a CLI exit code of `0` for no errors or `1` for errors.

- [ ] **Step 1: Create package markers and failing validator tests**

Create empty `scripts/__init__.py` and `tests/__init__.py`. Add these tests:

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.validate_brand import contrast_ratio, validate_project


class BrandValidationTests(unittest.TestCase):
    def test_approved_primary_pairs_exceed_wcag_aa(self):
        self.assertGreaterEqual(contrast_ratio("#203E55", "#E8F1F6"), 4.5)
        self.assertGreaterEqual(contrast_ratio("#F7F2E8", "#203E55"), 4.5)

    def test_missing_sources_are_reported(self):
        with TemporaryDirectory() as directory:
            errors = validate_project(Path(directory))
        self.assertIn("Missing required file: BRAND.md", errors)
        self.assertIn("Missing required file: brand/tokens.json", errors)

    def test_invalid_decision_status_is_reported(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "DECISIONS.md").write_text("| D-1 | Test | final | Owner | 2026-08-03 |", encoding="utf-8")
            errors = validate_project(root)
        self.assertIn("Invalid decision status in DECISIONS.md: final", errors)
```

- [ ] **Step 2: Run the test and confirm the intended import failure**

Run: `python3 -m unittest tests.test_brand_validation -v`

Expected: `ModuleNotFoundError: No module named 'scripts.validate_brand'`.

- [ ] **Step 3: Implement the validation foundation**

Create `scripts/validate_brand.py` with:

```python
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

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
```

- [ ] **Step 4: Create the authoritative human-readable sources**

Use these exact status boundaries:

```markdown
# Stronger at Home Physiotherapy

Status: approved strategy; proposed public name and proposed hybrid artwork
Approval owner: Melanie Watsham

Experienced care. Personal progress. At home.
```

`DECISIONS.md` must include:

```markdown
| ID | Decision | Status | Approved by | Date |
|---|---|---|---|---|
| D-01 | Patient-first positioning with referrers secondary. | approved | Project sponsor | 2026-08-02 |
| D-02 | Experienced care. Personal progress. At home. | approved | Project sponsor | 2026-08-02 |
| D-03 | Deep Navy, Pale Sky, Warm Cream and Warm Sand palette. | approved | Project sponsor | 2026-08-02 |
| D-04 | Source Serif 4 and Atkinson Hyperlegible Next typography. | approved | Project sponsor | 2026-08-02 |
| D-05 | Stronger at Home Physiotherapy public name. | proposed | Project sponsor | 2026-08-02 |
| D-10 | Wordmark-only architecture. | deprecated | Project sponsor | 2026-08-03 |
| D-11 | Hybrid house-and-care architecture for exploration. | proposed | Project sponsor | 2026-08-03 |
| D-12 | Final public artwork approval belongs to Melanie Watsham. | approved | Project sponsor | 2026-08-02 |
```

`brand/strategy.md`, `brand/messaging.md` and `brand/identity.md` must encode every Global Constraint without publishing gated credentials. `brand/clearance.md` must keep name, credentials and public contact fields unresolved. `MEMORY.md` must record the refreshed-repository rebuild and link the approved hybrid spec.

- [ ] **Step 5: Create the machine-readable context**

Create `.ai/context/brand.json` with these top-level keys and values:

```json
{
  "schema_version": "1.0",
  "brand_name": "Stronger at Home Physiotherapy",
  "brand_name_status": "proposed",
  "endorsement": "by Melanie Watsham",
  "audiences": {"primary": ["patients", "older adults"], "secondary": ["professional referrers"]},
  "services": {"focus": ["older-adult rehabilitation", "post-operative rehabilitation"], "radius": "10–15 miles around Epsom, Surrey"},
  "claims": {"approved": ["20+ years of NHS experience"], "verification_gated": ["HCPC", "CSP", "AGILE", "ATOCP"]},
  "personality": ["warm", "practical", "clinically credible"],
  "voice": ["reassuring", "hopeful", "empowering"],
  "identity_architecture": {"status": "proposed", "type": "hybrid", "standalone_symbol_allowed": false},
  "prohibitions": ["unverified claims", "guaranteed outcomes", "public use before clearance", "standalone symbol in Stage 1"],
  "approval_owner": "Melanie Watsham"
}
```

Use `ATOCP` as the credential spelling in both Markdown and JSON.

- [ ] **Step 6: Run focused tests**

Run: `python3 -m unittest tests.test_brand_validation -v`

Expected: three tests pass. Running `python3 scripts/validate_brand.py` exits `1` only for the intentionally absent token and asset files.

- [ ] **Step 7: Commit only Task 1 paths**

```bash
git add BRAND.md DECISIONS.md MEMORY.md brand/strategy.md brand/messaging.md brand/identity.md brand/clearance.md .ai/context/brand.json scripts/__init__.py scripts/validate_brand.py tests/__init__.py tests/test_brand_validation.py
git commit --only BRAND.md DECISIONS.md MEMORY.md brand/strategy.md brand/messaging.md brand/identity.md brand/clearance.md .ai/context/brand.json scripts/__init__.py scripts/validate_brand.py tests/__init__.py tests/test_brand_validation.py -m "feat: rebuild brand source foundation"
```

---

### Task 2: Restore semantic tokens and deterministic generation

**Files:**
- Create: `brand/tokens.json`
- Create: `scripts/generate_brand_tokens.py`
- Create: `brand/generated/tokens.css`
- Create: `tests/test_token_generation.py`
- Modify: `scripts/validate_brand.py`

**Interfaces:**
- Consumes: semantic JSON object from `brand/tokens.json`.
- Produces: `render_css(tokens: dict) -> str` and byte-for-byte generated CSS used by drift validation.

- [ ] **Step 1: Write failing token-generation tests**

```python
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.generate_brand_tokens import render_css
from scripts.validate_brand import validate_project


class TokenGenerationTests(unittest.TestCase):
    def test_render_css_is_deterministic_and_quotes_font_names(self):
        tokens = {
            "colour": {"brand": {"navy": "#203E55"}},
            "typography": {"family": {"body": "Atkinson Hyperlegible Next"}},
        }
        rendered = render_css(tokens)
        self.assertEqual(rendered, render_css(tokens))
        self.assertIn("--brand-colour-brand-navy: #203E55;", rendered)
        self.assertIn("--brand-typography-family-body: 'Atkinson Hyperlegible Next';", rendered)
        self.assertTrue(rendered.endswith("\n"))

    def test_generated_drift_is_reported(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "brand/generated").mkdir(parents=True)
            (root / "brand/tokens.json").write_text('{"colour":{"brand":{"navy":"#203E55"}}}', encoding="utf-8")
            (root / "brand/generated/tokens.css").write_text("stale", encoding="utf-8")
            errors = validate_project(root)
        self.assertIn("Generated token drift: brand/generated/tokens.css", errors)
```

- [ ] **Step 2: Confirm the new module is absent**

Run: `python3 -m unittest tests.test_token_generation -v`

Expected: import error for `scripts.generate_brand_tokens`.

- [ ] **Step 3: Create exact semantic tokens**

Create `brand/tokens.json`:

```json
{
  "schema_version": "1.0",
  "colour": {
    "brand": {"deep_navy": "#203E55", "pale_sky": "#E8F1F6", "warm_cream": "#F7F2E8", "warm_sand": "#C3A26E"},
    "text": {"primary": "#203E55", "inverse": "#F7F2E8"},
    "background": {"soft": "#E8F1F6", "warm": "#F7F2E8", "strong": "#203E55"},
    "accent": {"progress": "#C3A26E"}
  },
  "typography": {
    "family": {"display": "Source Serif 4", "body": "Atkinson Hyperlegible Next"},
    "weight": {"regular": 400, "semibold": 600},
    "line_height": {"tight": 1.1, "body": 1.5}
  },
  "spacing": {"xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "40px"},
  "layout": {"content_max": "72rem", "logo_clearspace": "1em"}
}
```

- [ ] **Step 4: Implement deterministic CSS rendering**

`render_css` must recursively flatten keys in sorted order, convert underscores to hyphens, quote strings containing spaces when the path includes `typography-family`, and return one trailing newline. The CLI reads `brand/tokens.json` and writes `brand/generated/tokens.css`.

- [ ] **Step 5: Add generated-drift validation**

Import `render_css` with a package import and a direct-script fallback. When both token source and generated CSS exist, append exactly `Generated token drift: brand/generated/tokens.css` on mismatch.

- [ ] **Step 6: Generate and verify**

Run:

```bash
python3 scripts/generate_brand_tokens.py
python3 -m unittest tests.test_brand_validation tests.test_token_generation -v
python3 scripts/validate_brand.py
```

Expected: all tests pass; validator exits `1` only because the asset manifest is absent. Font files are checked only when present until Task 3 adds them.

- [ ] **Step 7: Commit only Task 2 paths**

```bash
git add brand/tokens.json brand/generated/tokens.css scripts/generate_brand_tokens.py scripts/validate_brand.py tests/test_token_generation.py
git commit --only brand/tokens.json brand/generated/tokens.css scripts/generate_brand_tokens.py scripts/validate_brand.py tests/test_token_generation.py -m "feat: restore deterministic brand tokens"
```

---

### Task 3: Restore official font assets and provenance

**Files:**
- Create: `brand/fonts/README.md`
- Create after approval: `brand/fonts/source-serif-4.ttf`
- Create after approval: `brand/fonts/atkinson-hyperlegible-next.ttf`
- Create after approval: `brand/fonts/OFL-source-serif.txt`
- Create after approval: `brand/fonts/OFL-atkinson.txt`
- Modify: `brand/clearance.md`
- Modify: `scripts/validate_brand.py`
- Modify: `tests/test_brand_validation.py`

**Interfaces:**
- Consumes: fresh action-time approval and official Google Fonts repository URLs.
- Produces: paired local font/licence files, recorded SHA-256 hashes and validator enforcement.

- [ ] **Step 1: Add failing paired-licence tests**

Test the exact mapping:

```python
FONT_LICENCE_PAIRS = {
    "brand/fonts/source-serif-4.ttf": "brand/fonts/OFL-source-serif.txt",
    "brand/fonts/atkinson-hyperlegible-next.ttf": "brand/fonts/OFL-atkinson.txt",
}
```

For Source Serif 4 without its licence, expect `Missing font licence: brand/fonts/OFL-source-serif.txt`. For Atkinson Hyperlegible Next without its licence, expect `Missing font licence: brand/fonts/OFL-atkinson.txt`.

- [ ] **Step 2: Implement the mapping and pass the focused tests**

Run: `python3 -m unittest tests.test_brand_validation -v`

Expected: all validation tests pass without requiring font downloads in temporary projects.

- [ ] **Step 3: Ask for action-time download approval**

State that four official assets will be copied only into `brand/fonts/`, not installed system-wide, and used only for editable artwork and review.

- [ ] **Step 4: After approval, download exact official assets**

```bash
mkdir -p brand/fonts
curl -L 'https://raw.githubusercontent.com/google/fonts/main/ofl/sourceserif4/SourceSerif4%5Bopsz%2Cwght%5D.ttf' -o brand/fonts/source-serif-4.ttf
curl -L 'https://raw.githubusercontent.com/google/fonts/main/ofl/sourceserif4/OFL.txt' -o brand/fonts/OFL-source-serif.txt
curl -L 'https://raw.githubusercontent.com/google/fonts/main/ofl/atkinsonhyperlegiblenext/AtkinsonHyperlegibleNext%5Bwght%5D.ttf' -o brand/fonts/atkinson-hyperlegible-next.ttf
curl -L 'https://raw.githubusercontent.com/google/fonts/main/ofl/atkinsonhyperlegiblenext/OFL.txt' -o brand/fonts/OFL-atkinson.txt
shasum -a 256 brand/fonts/*
```

- [ ] **Step 5: Record provenance**

Record URLs, actual download date, exact hashes, licence names and intended brand use in `brand/fonts/README.md`. Add a successful font-provenance entry to `brand/clearance.md` without clearing the public name or credentials.

- [ ] **Step 6: Verify and commit only Task 3 paths**

Run all tests and the validator. Expected validator failure remains only the absent artwork manifest.

```bash
git add brand/fonts brand/clearance.md scripts/validate_brand.py tests/test_brand_validation.py
git commit --only brand/fonts brand/clearance.md scripts/validate_brand.py tests/test_brand_validation.py -m "chore: restore approved font sources"
```

---

### Task 4: Build the proposed owned hybrid primary logo

**Files:**
- Create: `brand/assets/reference/home-physiotherapy-logo.svg`
- Create: `brand/assets/reference/home-physiotherapy-logo-monochrome.svg`
- Create: `brand/assets/reference/README.md`
- Create: `brand/assets/source/logo-primary-hybrid.svg`
- Create: `brand/assets/review/logo-hybrid-preview.html`
- Create: `brand/assets/manifest.json`
- Modify: `scripts/validate_brand.py`
- Modify: `tests/test_brand_validation.py`

**Interfaces:**
- Consumes: user-owned source files, local fonts and semantic colours.
- Produces: one proposed editable hybrid primary SVG and a manifest entry with `id`, `role`, `path`, `status`, `sha256`, `reviewed_by` and `reviewed_on`.

- [ ] **Step 1: Copy immutable provenance references and record hashes**

Copy the two owned SVGs from `/Users/mwatsham/Documents/Codex/2026-08-03/i/outputs/` into `brand/assets/reference/`. Record source paths, ownership confirmation date `2026-08-03`, copy date and SHA-256 hashes in `brand/assets/reference/README.md`. Do not edit either reference copy.

- [ ] **Step 2: Add failing hybrid-logo tests**

Add tests asserting:

```python
self.assertNotIn("<image", svg_text)
self.assertIn("Stronger at Home", svg_text)
self.assertIn("Physiotherapy", svg_text)
self.assertIn("by Melanie Watsham", svg_text)
self.assertIn("#203E55", svg_text)
self.assertIn("#C3A26E", svg_text)
self.assertEqual(asset["status"], "proposed")
self.assertIsNone(asset["reviewed_by"])
self.assertIsNone(asset["reviewed_on"])
```

Also assert that every manifest path exists and its lowercase SHA-256 matches file bytes.

- [ ] **Step 3: Confirm the failures**

Run: `python3 -m unittest tests.test_brand_validation -v`

Expected: failures for missing `logo-primary-hybrid.svg` and `brand/assets/manifest.json`.

- [ ] **Step 4: Build the editable primary SVG**

Use a transparent `1160 × 340` viewBox. Embed local font faces using relative `../../fonts/` URLs. Build these layers in order:

1. Deep Navy open-doorway house outline at left.
2. Deep Navy hand path faithfully copied from the owned SVG vector path and scaled inside the house.
3. A vector-only moving person reconstructed from a circle and rounded body/limb paths; do not embed the owned PNG.
4. Three Warm Sand rounded progression steps, with the lowest aligned to the doorway.
5. Two Source Serif 4 wordmark lines and one Atkinson Hyperlegible Next endorsement line at right.

The SVG must contain:

```xml
<title>Stronger at Home Physiotherapy by Melanie Watsham</title>
<desc>A supporting hand and progressing person within an open-doorway home, beside the Stronger at Home Physiotherapy wordmark.</desc>
```

Use only `#203E55` and `#C3A26E`. Preserve live text. The house outline must have no chimney, windows, cross or enclosing badge.

- [ ] **Step 5: Create the review composition**

`logo-hybrid-preview.html` must show the exact primary SVG on Pale Sky, Warm Cream and Deep Navy fields at full, half and small-header sizes. On Deep Navy, retain a Warm Cream holding surface. Include a close-up symbol view, the supporting line and `PROPOSED — NOT FOR PUBLIC USE`.

- [ ] **Step 6: Create the proposed manifest with the actual hash**

Run `shasum -a 256 brand/assets/source/logo-primary-hybrid.svg`. Create `brand/assets/manifest.json` with `schema_version` set to `1.0` and one asset whose id is `logo_primary_hybrid`, role is `primary_hybrid_logo`, path is `brand/assets/source/logo-primary-hybrid.svg`, status is `proposed`, hash is the observed 64-character lowercase command result, and both review fields are JSON null values. Use `apply_patch` only after the real hash is known; never save or commit a provisional hash.

- [ ] **Step 7: Implement SVG and manifest validation**

Use `hashlib.sha256(path.read_bytes()).hexdigest()` and `xml.etree.ElementTree`. Reject embedded `{http://www.w3.org/2000/svg}image` elements, missing title/description, missing required text, disallowed colours, hash mismatches and approved assets without review metadata.

- [ ] **Step 8: Run automated validation**

Run:

```bash
python3 -m unittest tests.test_brand_validation tests.test_token_generation -v
python3 scripts/generate_brand_tokens.py
python3 scripts/validate_brand.py
```

Expected: all tests pass and CLI prints `Brand validation passed` while the logo remains proposed.

- [ ] **Step 9: Commit the proposed artwork only**

```bash
git add brand/assets scripts/validate_brand.py tests/test_brand_validation.py
git commit --only brand/assets scripts/validate_brand.py tests/test_brand_validation.py -m "feat: add proposed hybrid logo"
```

---

### Task 5: Complete visual review and record Melanie's approval outcome

**Files:**
- Modify after explicit approval: `brand/assets/manifest.json`
- Modify after explicit approval: `DECISIONS.md`
- Modify after explicit approval: `MEMORY.md`
- Modify after explicit approval: `brand/identity.md`

**Interfaces:**
- Consumes: proposed primary logo and explicit Melanie Watsham approval conveyed by the user.
- Produces: approved primary asset metadata or a documented revision request while status remains proposed.

- [ ] **Step 1: Open and inspect the complete review composition**

Inspect line breaks, symbol/wordmark balance, house recognition, person/hand/step clarity, doorway alignment, small-size legibility, background contrast and endorsement prominence.

- [ ] **Step 2: Present the preview and ask for the exact approval owner**

Ask the user to confirm one of two outcomes:

- `Melanie Watsham explicitly approved this exact artwork.`
- `Changes are requested; keep the artwork proposed.`

Sponsor-only approval must not change the asset status.

- [ ] **Step 3: If changes are requested, revise only the primary source**

Recompute the hash, update the manifest hash, rerun Task 4 Step 8 and repeat visual review. Do not create variants during this loop.

- [ ] **Step 4: If Melanie approved it, record the exact outcome**

Set `status` to `approved`, `reviewed_by` to `Melanie Watsham` and `reviewed_on` to the actual ISO date. Add a decision row for the approved exact artwork and record that the standalone symbol remains unapproved.

- [ ] **Step 5: Re-run validation and commit approval metadata**

```bash
python3 -m unittest tests.test_brand_validation tests.test_token_generation -v
python3 scripts/validate_brand.py
git add brand/assets/manifest.json DECISIONS.md MEMORY.md brand/identity.md
git commit --only brand/assets/manifest.json DECISIONS.md MEMORY.md brand/identity.md -m "docs: record approved hybrid logo"
```

Expected: tests and validator pass; the commit must not change SVG geometry unless that exact geometry was the reviewed version.

---

### Task 6: Create controlled variants after primary approval

**Files:**
- Create: `brand/assets/source/logo-compact-hybrid.svg`
- Create: `brand/assets/source/logo-mono-hybrid.svg`
- Create: `brand/assets/source/logo-reversed-hybrid.svg`
- Modify: `brand/assets/review/logo-hybrid-preview.html`
- Modify: `brand/assets/manifest.json`
- Modify: `tests/test_brand_validation.py`

**Interfaces:**
- Consumes: an approved `logo_primary_hybrid` manifest entry.
- Produces: proposed compact, monochrome and reversed variants that retain both symbol and business-name text.

- [ ] **Step 1: Add a failing approval-dependency test**

Assert that any variant entry is invalid unless `logo_primary_hybrid.status == "approved"`. Assert that no variant has role `standalone_symbol`.

- [ ] **Step 2: Build the three variants**

- Compact: keep the full house symbol, `Stronger at Home`, `Physiotherapy` and a legible endorsement; tighten spacing without using the symbol alone.
- Monochrome: use only Deep Navy on transparent or light backgrounds.
- Reversed: use Warm Cream lettering and house/figure/hand with Warm Sand steps on Deep Navy.

Every SVG must have a unique title and description, no embedded raster element and live text.

- [ ] **Step 3: Register variants as proposed with exact hashes**

Each entry must have null review metadata. Do not inherit the primary approval automatically.

- [ ] **Step 4: Extend the review composition and validate**

Show all variants at representative and small sizes. Run all tests and project validation.

- [ ] **Step 5: Present variants for explicit Melanie approval**

Only after the user confirms Melanie approved each exact variant may its manifest status and review metadata change to approved.

- [ ] **Step 6: Commit variants and any separately confirmed approval metadata**

```bash
git add brand/assets tests/test_brand_validation.py
git commit --only brand/assets tests/test_brand_validation.py -m "feat: add controlled hybrid logo variants"
```

---

### Task 7: Run final Stage 1 validation and handoff

**Files:**
- Modify: `BRAND.md`
- Modify: `MEMORY.md`
- Modify: `brand/clearance.md`
- Create: `brand/HANDOFF.md`

**Interfaces:**
- Consumes: validated sources and actual approval states.
- Produces: a concise Stage 1 handoff with exact approved/proposed boundaries and next-stage blockers.

- [ ] **Step 1: Add a final policy regression test**

Assert that the public name can remain proposed while approved artwork exists, but `BRAND.md` must still say Stage 1 is internal and public use is blocked by name clearance.

- [ ] **Step 2: Run the complete verification suite**

```bash
python3 -m unittest discover -s tests -v
python3 scripts/generate_brand_tokens.py
git diff --exit-code -- brand/generated/tokens.css
python3 scripts/validate_brand.py
git diff --check
```

Expected: every command exits `0`.

- [ ] **Step 3: Write the handoff**

`brand/HANDOFF.md` must list:

- Approved strategy, message, palette and typography.
- Actual approval status of primary and variant artwork.
- Proposed public name and unresolved clearance.
- Verification-gated credentials and contact details.
- Exact authoritative file paths.
- Stage 2 boundary: print materials only after name, copy, contact and artwork approvals are complete.

- [ ] **Step 4: Update entry points and commit only final documentation**

```bash
git add BRAND.md MEMORY.md brand/clearance.md brand/HANDOFF.md tests/test_brand_validation.py
git commit --only BRAND.md MEMORY.md brand/clearance.md brand/HANDOFF.md tests/test_brand_validation.py -m "docs: complete stage 1 brand handoff"
```

- [ ] **Step 5: Verify repository scope**

Run `git status --short` and confirm any remaining staged `AGENTS.md` change is still user-owned and absent from every plan commit. Report final commit hashes, test totals, validator output and all unresolved external gates.
