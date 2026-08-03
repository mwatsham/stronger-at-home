# Supplied Logo Production Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current proposed primary symbol with a faithful, editable vector reconstruction of the approved supplied logo reference and present the exact result for Melanie Watsham's approval.

**Architecture:** The committed PNG remains immutable reference evidence. One transparent SVG is the editable production source, while the asset manifest records its real SHA-256 and proposed/approved state. Existing dependency-free validation checks the SVG and manifest; a local HTML composition provides reference-fidelity and small-size visual review.

**Tech Stack:** Markdown, JSON, SVG 1.1, HTML/CSS, Python 3 standard library, `unittest`, SHA-256 provenance and local image rendering.

## Global Constraints

- The authoritative visual reference is `docs/superpowers/specs/assets/stronger-at-home-supplied-logo-reference.png` with SHA-256 `6d066dbeff88023aece19346a1d0a9a1d3f4577f7846545e359ad59fab24f889`.
- Preserve the supplied open-bottom house, right-roof chimney, moving person, three ascending steps and outlined supporting hand.
- Preserve the supplied composition and character; regularise raster artefacts without redesigning the silhouette.
- Reconstruct deterministic vector geometry. Do not use an image-generation model for production logo geometry.
- Remove the reference glow, blur, shadow and off-white background.
- Use only Deep Navy `#203E55` for house, chimney, person, hand and wordmark, and Warm Sand `#C3A26E` for the three steps.
- Use Source Serif 4 for the wordmark and Atkinson Hyperlegible Next for the endorsement.
- Keep the primary source transparent with live business-name, descriptor and endorsement text.
- Keep a wordmark-led horizontal lockup; the symbol occupies approximately one quarter of the total width.
- Keep the public name proposed and HCPC, CSP, AGILE and ATOCP claims verification-gated.
- Keep the production artwork proposed until the user confirms `Melanie Watsham explicitly approved this exact artwork.`
- Do not approve or export the symbol as a standalone badge in Stage 1.
- Do not create variants before the reconstructed primary artwork is approved.
- Preserve `sources/` and the parent checkout's staged `AGENTS.md`.
- Use path-scoped commits so generated caches and unrelated changes are never included.

## File Map

| File | Responsibility |
|---|---|
| `brand/assets/reference/stronger-at-home-supplied-logo-reference.png` | Immutable brand-area copy of the approved supplied reference |
| `brand/assets/reference/README.md` | Reference origin, hash, rights gate and reconstruction role |
| `brand/assets/source/logo-primary-hybrid.svg` | Proposed editable primary lockup |
| `brand/assets/review/logo-hybrid-preview.html` | Reference-fidelity, background and size review |
| `brand/assets/manifest.json` | Production artwork path, real hash and approval state |
| `scripts/validate_brand.py` | Exact primary metadata and asset-governance validation |
| `tests/test_brand_validation.py` | Behavioural validator coverage through temporary projects |
| `DECISIONS.md` | Deprecated previous geometry and proposed supplied-reference direction |
| `MEMORY.md` | Rationale and visual-review history |
| `brand/identity.md` | Current proposed symbol construction and usage boundary |
| `brand/clearance.md` | Exact-image usage-rights gate |

---

### Task 1: Register the supplied reference and governance transition

**Files:**
- Create: `brand/assets/reference/stronger-at-home-supplied-logo-reference.png`
- Modify: `brand/assets/reference/README.md`
- Modify: `DECISIONS.md`
- Modify: `MEMORY.md`
- Modify: `brand/identity.md`
- Modify: `brand/clearance.md`

**Interfaces:**
- Consumes: committed design reference and specification.
- Produces: immutable brand-area reference with verified hash, plus authoritative proposed/deprecated decision boundaries used by Task 2.

- [ ] **Step 1: Verify the committed design reference before copying**

Run:

```bash
shasum -a 256 docs/superpowers/specs/assets/stronger-at-home-supplied-logo-reference.png
```

Expected exact output prefix:

```text
6d066dbeff88023aece19346a1d0a9a1d3f4577f7846545e359ad59fab24f889
```

- [ ] **Step 2: Copy the immutable reference and verify byte identity**

Run:

```bash
cp docs/superpowers/specs/assets/stronger-at-home-supplied-logo-reference.png brand/assets/reference/stronger-at-home-supplied-logo-reference.png
cmp -s docs/superpowers/specs/assets/stronger-at-home-supplied-logo-reference.png brand/assets/reference/stronger-at-home-supplied-logo-reference.png
shasum -a 256 brand/assets/reference/stronger-at-home-supplied-logo-reference.png
```

Expected: `cmp` exits `0`; the copied file has the same exact hash.

- [ ] **Step 3: Record provenance without inventing rights clearance**

Append this entry to `brand/assets/reference/README.md`:

```markdown
## Supplied production-cleanup reference

- Project path: `brand/assets/reference/stronger-at-home-supplied-logo-reference.png`
- Design-spec path: `docs/superpowers/specs/assets/stronger-at-home-supplied-logo-reference.png`
- Supplied by the project sponsor: 2026-08-03
- Dimensions: 1254 × 1254 pixels
- SHA-256: `6d066dbeff88023aece19346a1d0a9a1d3f4577f7846545e359ad59fab24f889`
- Role: immutable visual reconstruction reference; not production artwork
- Rights: explicit ownership/usage-rights confirmation for this exact image remains required before public use
```

- [ ] **Step 4: Update the decision ledger and durable rationale**

Change D-11 from `proposed` to `deprecated`. Add:

```markdown
| D-13 | Filled-hand/open-doorway primary geometry. | deprecated | Project sponsor | 2026-08-03 |
| D-14 | Faithful production cleanup of the supplied house, moving person, steps and outlined hand reference. | proposed | Project sponsor | 2026-08-03 |
```

In `MEMORY.md`, record that the sponsor rejected the first reconstructed hybrid logo and selected the new supplied PNG as the authoritative visual reference. In `brand/identity.md`, describe D-14 as the only current proposed primary artwork direction. In `brand/clearance.md`, add an unresolved rights row for the exact supplied-image hash without changing name or credential clearance.

- [ ] **Step 5: Verify documentation and reference integrity**

Run:

```bash
shasum -a 256 brand/assets/reference/stronger-at-home-supplied-logo-reference.png
python3 scripts/validate_brand.py
git diff --check
```

Expected: reference hash matches; existing brand validator passes because production SVG and manifest are unchanged during Task 1; diff check exits `0`.

- [ ] **Step 6: Commit only Task 1 paths**

```bash
git add brand/assets/reference/stronger-at-home-supplied-logo-reference.png brand/assets/reference/README.md DECISIONS.md MEMORY.md brand/identity.md brand/clearance.md
git commit --only brand/assets/reference/stronger-at-home-supplied-logo-reference.png brand/assets/reference/README.md DECISIONS.md MEMORY.md brand/identity.md brand/clearance.md -m "docs: register supplied logo reference"
```

---

### Task 2: Reconstruct and validate the proposed primary logo

**Files:**
- Modify: `brand/assets/source/logo-primary-hybrid.svg`
- Modify: `brand/assets/review/logo-hybrid-preview.html`
- Modify: `brand/assets/manifest.json`
- Modify: `scripts/validate_brand.py`
- Modify: `tests/test_brand_validation.py`

**Interfaces:**
- Consumes: immutable reference from Task 1, local approved fonts and `validate_project(root: Path) -> list[str]`.
- Produces: a proposed `1160 × 340` primary SVG, an exact manifest hash, and behavioural validation for the new accessibility description and governance state.

- [ ] **Step 1: Update the existing exact-description behaviour test**

Update `VALID_HYBRID_SVG` with the new exact description. Replace `test_accessible_description_must_match_exactly` with:

```python
def test_accessible_description_must_match_exactly(self):
    svg = VALID_HYBRID_SVG.replace(
        "An open-bottom home above a supporting outlined hand, with a moving person and three ascending steps, beside the Stronger at Home Physiotherapy wordmark.",
        "The old supporting-hand description.",
    )
    with TemporaryDirectory() as directory:
        root = Path(directory)
        write_asset_project(root, svg_text=svg)
        errors = validate_project(root)
    self.assertIn(
        "Hybrid logo description must equal: An open-bottom home above a supporting outlined hand, with a moving person and three ascending steps, beside the Stronger at Home Physiotherapy wordmark.",
        errors,
    )
```

Update the valid fixture to use this exact metadata:

```xml
<title>Stronger at Home Physiotherapy by Melanie Watsham</title>
<desc>An open-bottom home above a supporting outlined hand, with a moving person and three ascending steps, beside the Stronger at Home Physiotherapy wordmark.</desc>
```

Replace the previous description literal with the new exact description in `test_missing_accessible_title_and_description_are_rejected`. Keep the existing `test_valid_proposed_hybrid_asset_has_no_asset_validation_errors` unchanged; it already exercises the valid fixture through `validate_project`.

- [ ] **Step 2: Run focused tests and confirm the intended RED**

Run:

```bash
python3 -m unittest tests.test_brand_validation -v
```

Expected: `test_accessible_description_must_match_exactly` fails because `scripts/validate_brand.py` still reports the previous required description.

- [ ] **Step 3: Update exact validator metadata**

Set these constants in `scripts/validate_brand.py`:

```python
REQUIRED_LOGO_TITLE = "Stronger at Home Physiotherapy by Melanie Watsham"
REQUIRED_LOGO_DESCRIPTION = (
    "An open-bottom home above a supporting outlined hand, with a moving person "
    "and three ascending steps, beside the Stronger at Home Physiotherapy wordmark."
)
```

Keep equality checks, permitted-colour checks, embedded-image rejection, live-text validation, manifest hash enforcement and Melanie-specific approval validation unchanged.

- [ ] **Step 4: Replace the primary SVG with deterministic vector geometry**

Keep `viewBox="0 0 1160 340"`, transparent background, local font faces and live text. Use these exact structural groups:

```xml
<g id="supplied-reference-symbol" transform="translate(12 4)">
  <path id="open-home" d="M42 226 V116 L146 30 L250 116 V226"
        fill="none" stroke="#203E55" stroke-width="10"
        stroke-linecap="round" stroke-linejoin="round" />
  <path id="chimney" d="M198 73 V51 H219 V91"
        fill="none" stroke="#203E55" stroke-width="10"
        stroke-linecap="round" stroke-linejoin="round" />
  <g id="moving-person">
    <circle cx="112" cy="108" r="12" fill="#203E55" />
    <g fill="none" stroke="#203E55" stroke-width="16"
       stroke-linecap="round" stroke-linejoin="round">
      <path d="M108 137 L132 164" />
      <path d="M108 141 L89 165 M121 149 L151 157" />
      <path d="M132 164 L118 205" />
      <path d="M132 164 L169 181 L164 212" />
    </g>
  </g>
  <g id="progression-steps" fill="#C3A26E">
    <rect x="88" y="213" width="46" height="12" rx="6" />
    <rect x="145" y="178" width="46" height="12" rx="6" />
    <rect x="202" y="143" width="42" height="12" rx="6" />
  </g>
  <path id="supporting-hand" d="M38 281 C61 247 89 237 120 244 C151 252 176 251 201 239 C215 232 225 240 213 251 C200 262 181 267 161 265 C182 274 203 274 222 264 L263 232 C273 224 283 234 274 243 L241 273 L281 244 C292 237 301 249 291 258 L253 286 L298 261 C309 255 317 268 306 276 L266 305 C231 330 186 335 142 324 L91 309 L42 309 Z"
        fill="none" stroke="#203E55" stroke-width="9"
        stroke-linecap="round" stroke-linejoin="round" />
</g>
```

Apply all of the following exact attributes:

- House and chimney: `fill="none"`, `stroke="#203E55"`, `stroke-width="10"`, rounded caps/joins.
- Supporting hand: `fill="none"`, `stroke="#203E55"`, `stroke-width="9"`, rounded caps/joins.
- Person: navy circle plus rounded navy body/limb paths, visually matching the supplied pose; use `stroke-width="16"` and no facial or clinical detail.
- Steps: exactly three Warm Sand rounded rectangles ascending left-to-right at `(88, 213)`, `(145, 178)` and `(202, 143)`, each `46 × 12` except the highest at `42 × 12`, radius `6`.
- Wordmark: `Stronger at Home` at `x=330 y=132`, `Physiotherapy` at `x=332 y=207`, endorsement at `x=334 y=258`.
- Do not include `<image>`, filters, masks, gradients, glow, shadow, blur or a background rectangle.

The person paths require optical tracing against the committed PNG. Limit the trace to a circle and four rounded paths for torso/arms/legs; do not add anatomy or detail not present in the reference.

- [ ] **Step 5: Build the reference-fidelity review composition**

Update `logo-hybrid-preview.html` to include:

1. The immutable PNG reference beside the production SVG at comparable symbol sizes.
2. The exact production SVG on Pale Sky, Warm Cream and a Warm Cream holding surface over Deep Navy.
3. Explicit `1160px`, `580px` and `348px` widths with `max-width: 100%`.
4. A symbol close-up.
5. A checklist: house/chimney, pose, three-step direction, outlined hand, flat colour, no glow.
6. `PROPOSED — NOT FOR PUBLIC USE`.

Use `<img>` references to the exact production SVG and immutable PNG; do not duplicate logo geometry inside HTML.

- [ ] **Step 6: Record the real production hash**

Run:

```bash
shasum -a 256 brand/assets/source/logo-primary-hybrid.svg
```

Update only the `logo_primary_hybrid` manifest entry. Keep `id` as `logo_primary_hybrid`, `role` as `primary_hybrid_logo`, `path` as `brand/assets/source/logo-primary-hybrid.svg`, `status` as `proposed`, and both review fields as JSON null. Set `sha256` directly to the observed lowercase 64-character command result; never save a provisional hash.

- [ ] **Step 7: Run focused and full verification**

Run:

```bash
python3 -m unittest tests.test_brand_validation -v
python3 -m unittest discover -s tests -v
python3 scripts/generate_brand_tokens.py
python3 scripts/validate_brand.py
git diff --check
```

Expected: all tests pass; generator exits `0`; validator prints `Brand validation passed`; diff check exits `0`.

- [ ] **Step 8: Render a local optical-review image**

Run:

```bash
mkdir -p /tmp/stronger-at-home-supplied-cleanup-review
qlmanage -t -s 1800 -o /tmp/stronger-at-home-supplied-cleanup-review brand/assets/source/logo-primary-hybrid.svg
```

Inspect the resulting PNG with the local image viewer. Confirm no clipping, smooth hand contour, clear person pose, three readable steps, wordmark-first hierarchy and legible endorsement. This inspection does not approve the artwork.

- [ ] **Step 9: Commit only Task 2 paths**

```bash
git add brand/assets/source/logo-primary-hybrid.svg brand/assets/review/logo-hybrid-preview.html brand/assets/manifest.json scripts/validate_brand.py tests/test_brand_validation.py
git commit --only brand/assets/source/logo-primary-hybrid.svg brand/assets/review/logo-hybrid-preview.html brand/assets/manifest.json scripts/validate_brand.py tests/test_brand_validation.py -m "feat: reconstruct supplied primary logo"
```

---

### Task 3: Complete visual review and record the exact approval outcome

**Files:**
- Modify after explicit approval: `brand/assets/manifest.json`
- Modify after explicit approval: `DECISIONS.md`
- Modify after explicit approval: `MEMORY.md`
- Modify after explicit approval: `brand/identity.md`

**Interfaces:**
- Consumes: proposed production SVG, immutable PNG reference, review composition and explicit Melanie Watsham approval conveyed by the user.
- Produces: approved exact primary artwork metadata or a documented revision request while the asset remains proposed.

- [ ] **Step 1: Inspect reference fidelity and production quality**

Compare the supplied PNG and production symbol for:

- Open-bottom house and right-roof chimney proportions.
- Moving-person pose and direction.
- Count, order and ascent of the three steps.
- Supporting-hand silhouette, palm direction and finger count.
- Relative spacing between house and hand.
- Absence of glow, blur, background and teal.
- Deep Navy/Warm Sand accuracy.
- Wordmark balance and endorsement legibility at `348px`.

- [ ] **Step 2: Present the exact review composition**

Show `brand/assets/review/logo-hybrid-preview.html` and the rendered primary PNG. Ask for exactly one outcome:

- `Melanie Watsham explicitly approved this exact artwork.`
- `Changes are requested; keep the artwork proposed.`

Sponsor-only approval must not change the manifest state.

- [ ] **Step 3: If changes are requested, revise only the proposed primary**

Modify only the source SVG, review HTML, manifest hash, validator constants/tests if accessible text changes, and the documented revision rationale. Re-run Task 2 Steps 7–8 and repeat the approval gate. Do not create variants during this loop.

- [ ] **Step 4: If Melanie approved it, record exact approval metadata**

Set:

```json
"status": "approved",
"reviewed_by": "Melanie Watsham",
"reviewed_on": "2026-08-03"
```

Add:

```markdown
| D-15 | Exact supplied-reference primary hybrid artwork. | approved | Melanie Watsham | 2026-08-03 |
```

Record that the public name and standalone symbol remain unapproved.

- [ ] **Step 5: Re-run verification and commit approval metadata**

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_brand.py
git diff --check
git add brand/assets/manifest.json DECISIONS.md MEMORY.md brand/identity.md
git commit --only brand/assets/manifest.json DECISIONS.md MEMORY.md brand/identity.md -m "docs: record supplied logo approval"
```

Expected: all commands exit `0`; SVG geometry is unchanged from the exact artwork Melanie reviewed.

- [ ] **Step 6: Resume the Stage 1 downstream boundary**

Only after Task 3 approval may the existing Stage 1 plan continue with controlled compact, monochrome and reversed hybrid variants. Each variant starts proposed and requires its own explicit Melanie approval.
