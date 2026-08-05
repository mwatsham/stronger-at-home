# Stronger@Home Wordmark Revision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create, review, and govern new raster-only primary logo lockups that style the approved trading name as `Stronger@Home` while preserving the existing approved PNGs as immutable history.

**Architecture:** Extend the deterministic Pillow generator to write versioned candidate PNGs beside the currently approved files, then add manifest validation and a dedicated comparison page. Pause for Melanie Watsham's exact-artwork approval before promoting the candidate paths to primary roles and updating the authoritative brand records.

**Tech Stack:** Python 3, Pillow 12.3.0, `unittest`, JSON, Markdown, static HTML, Git.

## Global Constraints

- Formal trading name: **Stronger at Home Physiotherapy**.
- Styled wordmark: **Stronger@Home** with **Physiotherapy** clearly visible.
- Official identity: **Melanie Watsham trading as Stronger at Home Physiotherapy**.
- Preferred domain: **stronger-at-home.co.uk**, subject to registration and control verification.
- Preserve `docs/superpowers/specs/assets/home-physiotherapy-logo-approved-concept-v2.png` byte-for-byte at SHA-256 `41267865711ca55f9225df8370c50bca823f68ca966b8fc216852e65a36d0ef1`.
- Preserve `brand/assets/source/logo-primary-raster-2048.png` and `brand/assets/source/logo-primary-raster-512.png` byte-for-byte as the previously approved artwork.
- Create no SVG, transparent, monochrome, traced, redrawn, recoloured, background-removed, or AI-regenerated derivative.
- Candidate outputs must be opaque RGB PNGs at exactly 2048 × 640 and 512 × 160 pixels.
- Reuse the existing crop, symbol position, fonts, colours, sizes, background, descriptor, and endorsement without visual alteration.
- Treat `@` as display styling only; formal, accessible, spoken, metadata, and legal uses spell out `Stronger at Home Physiotherapy`.
- Do not mark candidate artwork approved until Melanie Watsham approves both exact output files.
- Do not treat artwork approval, domain availability, or a Companies House search as trademark clearance.
- Public use remains blocked until every applicable entry in `brand/clearance.md` is resolved.
- Do not install or upgrade dependencies; use the existing `Pillow==12.3.0` environment.
- Preserve the user's existing `AGENTS.md` index and working-tree changes; never include them in a task commit.

---

## File structure

- Modify `scripts/generate_raster_logo.py`: retain historical reproduction and add deterministic candidate rendering to versioned paths.
- Modify `tests/test_raster_logo_generation.py`: prove exact naming constants, deterministic candidate generation, and non-mutation of the approved PNGs.
- Modify `scripts/validate_brand.py`: validate candidate roles before approval and versioned primary paths after approval.
- Modify `tests/test_brand_validation.py`: cover candidate paths, statuses, review metadata, dimensions, and promotion rules.
- Modify `brand/assets/manifest.json`: record candidate files, then promote them only after exact-artwork approval.
- Create `brand/assets/source/logo-primary-raster-v2-2048.png`: 2048 × 640 candidate and eventual primary artwork.
- Create `brand/assets/source/logo-primary-raster-v2-512.png`: 512 × 160 candidate and eventual primary artwork.
- Create `brand/assets/review/logo-raster-v2-preview.html`: compare the previously approved and candidate lockups at both sizes.
- Modify `BRAND.md`: record the approved naming architecture and the current artwork/public-use boundary.
- Modify `brand/identity.md`: document the styled wordmark, formal spelling, versioned artwork, and approval status.
- Modify `brand/messaging.md`: establish normal prose, spoken, accessibility, and endorsement usage.
- Modify `brand/clearance.md`: record the supplied-v2 usage-rights confirmation and retain unresolved name/domain/credential/contact gates.
- Modify `DECISIONS.md`: add the approved naming architecture and exact-artwork revision decision without rewriting historical decisions.
- Modify `MEMORY.md`: record the durable naming and artwork decisions after exact-artwork approval.
- Modify `.ai/context/brand.json`: expose the formal trading name, styled wordmark, sole-trader disclosure, domain status, and current primary asset paths.

---

### Task 1: Generate versioned `Stronger@Home` candidates without touching approved files

**Files:**
- Modify: `scripts/generate_raster_logo.py`
- Modify: `tests/test_raster_logo_generation.py`
- Create: `brand/assets/source/logo-primary-raster-v2-2048.png`
- Create: `brand/assets/source/logo-primary-raster-v2-512.png`

**Interfaces:**
- Consumes: immutable v2 symbol, pinned fonts, crop and layout constants already defined in `scripts.generate_raster_logo`.
- Produces: `generate_candidate(root: Path) -> tuple[Path, Path]`, `CANDIDATE_WORDMARK_LINES`, `CANDIDATE_MASTER_OUTPUT`, and `CANDIDATE_SMALL_OUTPUT`.

- [ ] **Step 1: Write failing generator tests**

Add the imports at module level, then add the following methods inside
`RasterLogoGenerationTests` in `tests/test_raster_logo_generation.py`:

```python
from scripts.generate_raster_logo import (
    APPROVED_MASTER_OUTPUT,
    APPROVED_SMALL_OUTPUT,
    CANDIDATE_MASTER_OUTPUT,
    CANDIDATE_SMALL_OUTPUT,
    CANDIDATE_WORDMARK_LINES,
    MASTER_SIZE,
    SMALL_SIZE,
    SOURCE_SHA256,
    generate,
    generate_candidate,
)

    def test_candidate_uses_approved_display_wording(self):
        self.assertEqual(
            CANDIDATE_WORDMARK_LINES,
            ("Stronger@Home", "Physiotherapy", "by Melanie Watsham"),
        )

    def test_generate_candidate_writes_versioned_opaque_pngs(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._copy_inputs(root)
            master_path, small_path = generate_candidate(root)
            self.assertEqual(master_path, root / CANDIDATE_MASTER_OUTPUT)
            self.assertEqual(small_path, root / CANDIDATE_SMALL_OUTPUT)
            with Image.open(master_path) as master:
                self.assertEqual((master.size, master.mode, master.format), (MASTER_SIZE, "RGB", "PNG"))
            with Image.open(small_path) as small:
                self.assertEqual((small.size, small.mode, small.format), (SMALL_SIZE, "RGB", "PNG"))

    def test_generate_candidate_does_not_modify_approved_outputs(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._copy_inputs(root)
            approved_paths = (root / APPROVED_MASTER_OUTPUT, root / APPROVED_SMALL_OUTPUT)
            approved_paths[0].parent.mkdir(parents=True, exist_ok=True)
            approved_paths[0].write_bytes(b"approved master evidence")
            approved_paths[1].write_bytes(b"approved small evidence")
            before = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in approved_paths)
            generate_candidate(root)
            after = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in approved_paths)
            self.assertEqual(after, before)

    def test_generate_candidate_is_byte_deterministic(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._copy_inputs(root)
            first = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in generate_candidate(root))
            second = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in generate_candidate(root))
            self.assertEqual(second, first)
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run:

```bash
python3 -m unittest tests.test_raster_logo_generation -v
```

Expected: import errors for the new candidate constants and `generate_candidate`.

- [ ] **Step 3: Add the minimal candidate generator**

In `scripts/generate_raster_logo.py`, preserve `generate()` for historical reproduction and add:

```python
APPROVED_MASTER_OUTPUT = Path("brand/assets/source/logo-primary-raster-2048.png")
APPROVED_SMALL_OUTPUT = Path("brand/assets/source/logo-primary-raster-512.png")
CANDIDATE_MASTER_OUTPUT = Path("brand/assets/source/logo-primary-raster-v2-2048.png")
CANDIDATE_SMALL_OUTPUT = Path("brand/assets/source/logo-primary-raster-v2-512.png")
APPROVED_WORDMARK_LINES = (
    "Stronger at Home",
    "Physiotherapy",
    "by Melanie Watsham",
)
CANDIDATE_WORDMARK_LINES = (
    "Stronger@Home",
    "Physiotherapy",
    "by Melanie Watsham",
)

def _render_master(root: Path, wordmark_lines: tuple[str, str, str]) -> Image.Image:
    _require_pinned_pillow()
    source = _verified_source(root)
    symbol = source.crop(CROP_BOX)
    symbol.thumbnail(SYMBOL_FIT, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", MASTER_SIZE, BACKGROUND)
    canvas.paste(symbol, SYMBOL_POSITION)
    draw = ImageDraw.Draw(canvas)
    fonts = (
        ImageFont.truetype(root / SOURCE_SERIF, 112),
        ImageFont.truetype(root / SOURCE_SERIF, 82),
        ImageFont.truetype(root / ATKINSON, 44),
    )
    positions = ((640, 130), (640, 270), (640, 390))
    for text, font, position in zip(wordmark_lines, fonts, positions, strict=True):
        draw.text(position, text, font=font, fill=DEEP_NAVY, anchor="lt")
    return canvas

def render_master(root: Path) -> Image.Image:
    return _render_master(root, APPROVED_WORDMARK_LINES)

def render_candidate_master(root: Path) -> Image.Image:
    return _render_master(root, CANDIDATE_WORDMARK_LINES)

def generate_candidate(root: Path) -> tuple[Path, Path]:
    master = render_candidate_master(root)
    small = master.resize(SMALL_SIZE, Image.Resampling.LANCZOS)
    master_path = root / CANDIDATE_MASTER_OUTPUT
    small_path = root / CANDIDATE_SMALL_OUTPUT
    _save_png(master, master_path)
    _save_png(small, small_path)
    return master_path, small_path
```

Set `MASTER_OUTPUT = APPROVED_MASTER_OUTPUT` and `SMALL_OUTPUT = APPROVED_SMALL_OUTPUT` so existing historical tests and reproduction remain stable. Change `main()` to call `generate_candidate(Path.cwd())`, ensuring the command-line script writes only the versioned revision.

- [ ] **Step 4: Run generator tests and create the candidate files**

Run:

```bash
python3 -m unittest tests.test_raster_logo_generation -v
python3 scripts/generate_raster_logo.py
shasum -a 256 brand/assets/source/logo-primary-raster-v2-2048.png brand/assets/source/logo-primary-raster-v2-512.png
```

Expected: all generator tests pass; the script prints only the two `v2` output paths; both SHA-256 values are lowercase 64-character hashes.

- [ ] **Step 5: Confirm the approved files remain byte-identical**

Run:

```bash
shasum -a 256 brand/assets/source/logo-primary-raster-2048.png brand/assets/source/logo-primary-raster-512.png
```

Expected:

```text
108c7bf9175868c4dffe15be6b2e4433346093d1f9d692752851a4b9d9bd5864  brand/assets/source/logo-primary-raster-2048.png
153f964143d1fadae66595871c6bbef5d3a336260bf28f6229043eaf91a23afd  brand/assets/source/logo-primary-raster-512.png
```

- [ ] **Step 6: Commit the generator and candidate assets**

```bash
git add scripts/generate_raster_logo.py tests/test_raster_logo_generation.py brand/assets/source/logo-primary-raster-v2-2048.png brand/assets/source/logo-primary-raster-v2-512.png
git diff --cached --check
git commit -m "feat: generate Stronger@Home raster candidates"
```

### Task 2: Govern candidate assets separately from approved primaries

**Files:**
- Modify: `scripts/validate_brand.py`
- Modify: `tests/test_brand_validation.py`
- Modify: `brand/assets/manifest.json`

**Interfaces:**
- Consumes: the two candidate PNG paths from Task 1 and their computed SHA-256 values.
- Produces: candidate roles `candidate_raster_logo_2048` and `candidate_raster_logo_512`, both with `status: proposed` and null review metadata.

- [ ] **Step 1: Add failing candidate-governance tests**

Extend `RASTER_ASSETS` in `tests/test_brand_validation.py` with:

```python
"candidate_raster_logo_2048": {
    "id": "logo_primary_raster_v2_2048",
    "filename": "logo-primary-raster-v2-2048.png",
    "size": (2048, 640),
},
"candidate_raster_logo_512": {
    "id": "logo_primary_raster_v2_512",
    "filename": "logo-primary-raster-v2-512.png",
    "size": (512, 160),
},
```

Add these methods inside `BrandValidationTests`:

```python
    def test_candidate_roles_require_versioned_paths(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_raster_asset(root, role="candidate_raster_logo_2048")
            manifest_path = root / "brand/assets/manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            candidate = next(asset for asset in manifest["assets"] if asset["role"] == "candidate_raster_logo_2048")
            candidate["path"] = "brand/assets/source/logo-primary-raster-2048.png"
            _write_manifest(root, manifest["assets"])
            errors = validate_project(root)
        self.assertIn(
            "Asset role candidate_raster_logo_2048 must use canonical path: brand/assets/source/logo-primary-raster-v2-2048.png",
            errors,
        )

    def test_candidate_roles_must_remain_proposed_before_review(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_raster_asset(
                root,
                role="candidate_raster_logo_512",
                status="approved",
                reviewed_by="Melanie Watsham",
                reviewed_on="2026-08-05",
            )
            errors = validate_project(root)
        self.assertIn(
            "Candidate asset logo_primary_raster_v2_512 must remain proposed before promotion",
            errors,
        )
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run:

```bash
python3 -m unittest tests.test_brand_validation -v
```

Expected: failures because the validator does not yet recognise candidate roles or canonical candidate paths.

- [ ] **Step 3: Add candidate validation**

In `scripts/validate_brand.py`, add:

```python
CANDIDATE_RASTER_SIZES = {
    "candidate_raster_logo_2048": (2048, 640),
    "candidate_raster_logo_512": (512, 160),
}
RASTER_SIZES = PRIMARY_RASTER_SIZES | CANDIDATE_RASTER_SIZES
CANDIDATE_LOGO_ROLES = set(CANDIDATE_RASTER_SIZES)
PRIMARY_LOGO_ROLES = set(PRIMARY_RASTER_SIZES) | CANDIDATE_LOGO_ROLES | {"primary_hybrid_logo"}
```

Add the candidate paths to `REQUIRED_ASSET_PATHS`:

```python
"candidate_raster_logo_2048": "brand/assets/source/logo-primary-raster-v2-2048.png",
"candidate_raster_logo_512": "brand/assets/source/logo-primary-raster-v2-512.png",
```

Change `_validate_raster_logo()` to read its size from `RASTER_SIZES`, and change the raster-role branch in `_validate_asset_manifest()` to use `if role in RASTER_SIZES`. Before the generic approved/proposed metadata checks, add:

```python
if role in CANDIDATE_LOGO_ROLES and status != "proposed":
    errors.append(
        f"Candidate asset {asset_id or '<unknown>'} must remain proposed before promotion"
    )
```

- [ ] **Step 4: Add candidate entries to the manifest**

Run this first and retain the first column from each line:

```bash
shasum -a 256 brand/assets/source/logo-primary-raster-v2-2048.png brand/assets/source/logo-primary-raster-v2-512.png
```

Append two entries to `brand/assets/manifest.json`. The first entry uses ID
`logo_primary_raster_v2_2048`, role `candidate_raster_logo_2048`, path
`brand/assets/source/logo-primary-raster-v2-2048.png`, status `proposed`, the
computed 2048-pixel SHA-256, and null `reviewed_by` and `reviewed_on`. The
second uses ID `logo_primary_raster_v2_512`, role
`candidate_raster_logo_512`, path
`brand/assets/source/logo-primary-raster-v2-512.png`, status `proposed`, the
computed 512-pixel SHA-256, and null review fields. Copy each hash exactly;
do not recompute or modify either PNG while editing the manifest.

- [ ] **Step 5: Run validation tests**

Run:

```bash
python3 -m unittest tests.test_brand_validation -v
python3 scripts/validate_brand.py
```

Expected: all tests pass and the validator prints `Brand validation passed`.

- [ ] **Step 6: Commit candidate governance**

```bash
git add scripts/validate_brand.py tests/test_brand_validation.py brand/assets/manifest.json
git diff --cached --check
git commit -m "test: govern Stronger@Home logo candidates"
```

### Task 3: Build the exact-artwork comparison and stop for review

**Files:**
- Create: `brand/assets/review/logo-raster-v2-preview.html`

**Interfaces:**
- Consumes: old approved PNGs and new candidate PNGs at both exact sizes.
- Produces: a local comparison page that clearly distinguishes historical approval from the unapproved candidate.

- [ ] **Step 1: Create the comparison page**

Create `brand/assets/review/logo-raster-v2-preview.html` using the existing preview's fonts and palette. Include these four image elements:

```html
<h2>Previously approved — 2048 × 640</h2>
<img class="lockup" src="../source/logo-primary-raster-2048.png" alt="Previously approved Stronger at Home Physiotherapy by Melanie Watsham logo">
<h2>Candidate — 2048 × 640</h2>
<img class="lockup" src="../source/logo-primary-raster-v2-2048.png" alt="Candidate Stronger at Home Physiotherapy by Melanie Watsham logo, styled as Stronger at Home">
<h2>Previously approved — 512 × 160</h2>
<img class="lockup small" src="../source/logo-primary-raster-512.png" alt="Previously approved Stronger at Home Physiotherapy by Melanie Watsham logo">
<h2>Candidate — 512 × 160</h2>
<img class="lockup small" src="../source/logo-primary-raster-v2-512.png" alt="Candidate Stronger at Home Physiotherapy by Melanie Watsham logo, styled as Stronger at Home">
```

The visible candidate section must state:

```text
CANDIDATE ARTWORK — NOT YET APPROVED OR CLEARED FOR PUBLIC USE
Review only the change from “Stronger at Home” to “Stronger@Home”. The supplied symbol pixels, descriptor, endorsement, colours, sizes and pale background are unchanged.
```

- [ ] **Step 2: Inspect the page and exact PNGs**

Open `brand/assets/review/logo-raster-v2-preview.html` in the in-app browser and inspect both sizes. Confirm visually:

- the `@` is unambiguous and does not collide with adjacent letters;
- the complete first line remains balanced against `Physiotherapy`;
- symbol and wordmark separation is unchanged;
- nothing is clipped at either size;
- the 512-pixel candidate remains legible; and
- the old and new symbol regions are pixel-identical.

- [ ] **Step 3: Verify symbol-region equality programmatically**

Run:

```bash
python3 -c 'from PIL import Image,ImageChops; from pathlib import Path; r=Path("brand/assets/source"); old=Image.open(r/"logo-primary-raster-2048.png"); new=Image.open(r/"logo-primary-raster-v2-2048.png"); assert ImageChops.difference(old.crop((0,0,620,640)),new.crop((0,0,620,640))).getbbox() is None; print("2048 symbol region unchanged")'
python3 -c 'from PIL import Image,ImageChops; from pathlib import Path; r=Path("brand/assets/source"); old=Image.open(r/"logo-primary-raster-512.png"); new=Image.open(r/"logo-primary-raster-v2-512.png"); assert ImageChops.difference(old.crop((0,0,155,160)),new.crop((0,0,155,160))).getbbox() is None; print("512 symbol region unchanged")'
```

Expected: both commands print that the symbol region is unchanged.

- [ ] **Step 4: Commit the review page**

```bash
git add brand/assets/review/logo-raster-v2-preview.html
git diff --cached --check
git commit -m "docs: present Stronger@Home logo candidates"
```

- [ ] **Step 5: Pause for exact-artwork approval**

Show the candidate 2048-pixel and 512-pixel artwork to Melanie Watsham. Ask one explicit question: **“Do you approve both exact `Stronger@Home` PNG files without changes?”** Do not begin Task 4 until the answer is an explicit approval.

### Task 4: Promote the exact approved revision to primary status

**Files:**
- Modify: `scripts/validate_brand.py`
- Modify: `tests/test_brand_validation.py`
- Modify: `brand/assets/manifest.json`
- Modify: `brand/assets/review/logo-raster-v2-preview.html`

**Interfaces:**
- Consumes: explicit approval of both exact candidate files by Melanie Watsham and the ISO approval date.
- Produces: v2 paths as the only current primary raster roles; old paths retained as deprecated historical records.

- [ ] **Step 1: Write failing promotion tests**

Import `REQUIRED_ASSET_PATHS` from `scripts.validate_brand`, then add this
method inside `BrandValidationTests`. Retain the existing tests that require
`reviewed_by: Melanie Watsham` and a valid ISO review date for approved primary
assets.

```python
    def test_current_primary_roles_use_v2_paths(self):
        self.assertEqual(
            REQUIRED_ASSET_PATHS["primary_raster_logo_2048"],
            "brand/assets/source/logo-primary-raster-v2-2048.png",
        )
        self.assertEqual(
            REQUIRED_ASSET_PATHS["primary_raster_logo_512"],
            "brand/assets/source/logo-primary-raster-v2-512.png",
        )
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run:

```bash
python3 -m unittest tests.test_brand_validation -v
```

Expected: the new path assertions fail because the old files are still canonical primary paths.

- [ ] **Step 3: Promote paths and roles**

In `scripts/validate_brand.py`, replace the candidate constants with this
promoted structure:

```python
PRIMARY_RASTER_SIZES = {
    "primary_raster_logo_2048": (2048, 640),
    "primary_raster_logo_512": (512, 160),
}
HISTORICAL_RASTER_SIZES = {
    "historical_raster_logo_2048": (2048, 640),
    "historical_raster_logo_512": (512, 160),
}
RASTER_SIZES = PRIMARY_RASTER_SIZES | HISTORICAL_RASTER_SIZES
HISTORICAL_RASTER_ROLES = set(HISTORICAL_RASTER_SIZES)
PRIMARY_LOGO_ROLES = set(PRIMARY_RASTER_SIZES) | {"primary_hybrid_logo"}
REQUIRED_ASSET_PATHS = {
    "primary_hybrid_logo": "brand/assets/source/logo-primary-hybrid.svg",
    "primary_raster_logo_2048": "brand/assets/source/logo-primary-raster-v2-2048.png",
    "primary_raster_logo_512": "brand/assets/source/logo-primary-raster-v2-512.png",
    "historical_raster_logo_2048": "brand/assets/source/logo-primary-raster-2048.png",
    "historical_raster_logo_512": "brand/assets/source/logo-primary-raster-512.png",
}
```

Delete `CANDIDATE_RASTER_SIZES`, `CANDIDATE_LOGO_ROLES`, and the
candidate-only status error. Add this historical rule inside the manifest
entry loop:

```python
if role in HISTORICAL_RASTER_ROLES and status != "deprecated":
    errors.append(
        f"Historical raster asset {asset_id or '<unknown>'} must be deprecated"
    )
```

Update `RASTER_ASSETS` in `tests/test_brand_validation.py` so the `v2`
filenames use the two `primary_raster_logo_*` roles and the original filenames
use the two `historical_raster_logo_*` roles. Replace the candidate-status
test with a historical-status test expecting the error above. In
`write_raster_asset()`, set each non-target historical fixture to deprecated:

```python
entry_status = status if is_target else (
    "deprecated" if current_role in HISTORICAL_RASTER_SIZES else "proposed"
)
```

Use `entry_status` for that manifest entry's `status`. Import
`HISTORICAL_RASTER_SIZES` from `scripts.validate_brand` at module level.

In `brand/assets/manifest.json`:

- change the old entries' roles to `historical_raster_logo_2048` and `historical_raster_logo_512`;
- change their status to `deprecated` while preserving their original SHA-256 and 2026-08-04 review metadata as historical evidence;
- change the v2 entries' roles to `primary_raster_logo_2048` and `primary_raster_logo_512`;
- change their status to `approved`; and
- set `reviewed_by` to `Melanie Watsham` and `reviewed_on` to the actual ISO approval date.

- [ ] **Step 4: Update the review record**

In `brand/assets/review/logo-raster-v2-preview.html`, change the candidate status to:

```text
EXACT STRONGER@HOME ARTWORK APPROVED — NOT CLEARED FOR PUBLIC USE
```

Record Melanie Watsham and the actual ISO approval date. Retain the older pair as historical comparison and do not imply that public-use clearance is complete.

- [ ] **Step 5: Run tests and validation**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_brand.py
```

Expected: the complete suite passes and the validator prints `Brand validation passed`.

- [ ] **Step 6: Commit the approved promotion**

```bash
git add scripts/validate_brand.py tests/test_brand_validation.py brand/assets/manifest.json brand/assets/review/logo-raster-v2-preview.html
git diff --cached --check
git commit -m "feat: approve Stronger@Home primary raster logo"
```

### Task 5: Adopt the naming architecture across the brand records

**Files:**
- Modify: `BRAND.md`
- Modify: `brand/identity.md`
- Modify: `brand/messaging.md`
- Modify: `brand/clearance.md`
- Modify: `DECISIONS.md`
- Modify: `MEMORY.md`
- Modify: `.ai/context/brand.json`

**Interfaces:**
- Consumes: approved naming specification, exact-artwork approval record, v2 primary asset paths, and the user's supplied-v2 usage-rights confirmation.
- Produces: one consistent formal name, display wordmark, sole-trader disclosure, domain state, clearance state, and current-asset record.

- [ ] **Step 1: Update the authoritative brand records**

Apply these exact semantic values consistently:

```json
{
  "brand_name": "Stronger at Home Physiotherapy",
  "brand_name_status": "proposed",
  "display_wordmark": "Stronger@Home",
  "service_descriptor": "Physiotherapy",
  "endorsement": "by Melanie Watsham",
  "business_structure": "sole trader",
  "official_identity": "Melanie Watsham trading as Stronger at Home Physiotherapy",
  "preferred_domain": "stronger-at-home.co.uk",
  "preferred_domain_status": "unregistered when checked 2026-08-04; registration and control unverified"
}
```

In Markdown prose:

- spell the formal name as `Stronger at Home Physiotherapy`;
- reserve `Stronger@Home` for the display wordmark;
- state that accessible text, search metadata, ordinary prose, and spoken usage spell out `at`;
- identify Melanie Watsham as the sole trader on official paperwork;
- keep the public name `proposed` until trademark clearance is recorded;
- record the project sponsor's 2026-08-04 v2 supplied-image usage-rights confirmation against SHA-256 `41267865711ca55f9225df8370c50bca823f68ca966b8fc216852e65a36d0ef1`;
- keep the older supplied PNG hash unresolved unless separate rights evidence exists for that exact file; and
- keep domain registration, credentials, contact details, and trademark clearance unresolved.

- [ ] **Step 2: Add decision-ledger entries**

Append entries using the next available IDs without renumbering history:

```text
Approved naming architecture: formal trading name “Stronger at Home Physiotherapy”; styled wordmark “Stronger@Home” with “Physiotherapy”; sole-trader identity “Melanie Watsham trading as Stronger at Home Physiotherapy”; preferred domain “stronger-at-home.co.uk”.
Approved exact v2 raster wordmark files, with the approver and actual approval date from Task 4.
```

Keep D-05 proposed until trademark/name clearance is complete.

- [ ] **Step 3: Add validation coverage for the structured context**

Add this method inside `BrandValidationTests` in
`tests/test_brand_validation.py`:

```python
    def test_brand_context_uses_formal_and_display_names(self):
        context = json.loads(
            (PROJECT_ROOT / ".ai/context/brand.json").read_text(encoding="utf-8")
        )
        self.assertEqual(context["brand_name"], "Stronger at Home Physiotherapy")
        self.assertEqual(context["display_wordmark"], "Stronger@Home")
        self.assertEqual(context["business_structure"], "sole trader")
        self.assertEqual(
            context["official_identity"],
            "Melanie Watsham trading as Stronger at Home Physiotherapy",
        )
```

Define `PROJECT_ROOT = Path(__file__).resolve().parents[1]` once near the test module's imports.

- [ ] **Step 4: Run all checks and inspect the final diff**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_brand.py
git diff --check
git status --short
```

Expected: every test passes, brand validation passes, no whitespace errors appear, and only the files listed in this task plus the user's pre-existing `AGENTS.md` changes are shown.

- [ ] **Step 5: Commit the adopted naming records**

```bash
git add BRAND.md brand/identity.md brand/messaging.md brand/clearance.md DECISIONS.md MEMORY.md .ai/context/brand.json tests/test_brand_validation.py
git diff --cached --check
git commit --only -m "docs: adopt Stronger@Home naming architecture" -- BRAND.md brand/identity.md brand/messaging.md brand/clearance.md DECISIONS.md MEMORY.md .ai/context/brand.json tests/test_brand_validation.py
```

- [ ] **Step 6: Report the remaining launch gates**

Report these as unresolved unless dated evidence in `brand/clearance.md` says otherwise:

1. official UKIPO exact and confusing-similarity trademark search in relevant service classes;
2. registration and verified control of `stronger-at-home.co.uk`;
3. HCPC, CSP, AGILE, and ATOCP wording verification;
4. approved public contact details; and
5. any usage-rights evidence still unresolved for other supplied artwork.

Do not push or deploy. Offer those as separate, permission-gated next actions.
