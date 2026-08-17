# Sole-Trader Name Adoption Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Approve `Stronger at Home Physiotherapy` for sole-trader physiotherapy use while recording that UKIPO registration is deferred and residual legal risk is accepted.

**Architecture:** Make one atomic governance update across the tested JSON context and its human-readable brand sources. Preserve the preliminary UKIPO evidence as history, distinguish commercial approval from legal clearance, and leave artwork, deployment, contacts and credential evidence unchanged.

**Tech Stack:** Markdown, JSON, Python `unittest`, existing dependency-free brand validator

## Global Constraints

- The legal identity remains `Melanie Watsham trading as Stronger at Home Physiotherapy`.
- The physiotherapy descriptor is accepted as sufficient practical differentiation for the current business.
- UKIPO registration is deferred; this is not legal clearance or a registered trade mark.
- Do not use the registered trade mark symbol, `®`.
- Preserve all current logo files and artwork rules without modification.
- Do not deploy website content or publish unverified credential claims.
- Do not modify `AGENTS.md` or any file under `sources/`.
- Do not install dependencies, push or deploy.

---

### Task 1: Adopt the name under the sole-trader risk decision

**Files:**
- Modify: `tests/test_brand_validation.py`
- Modify: `.ai/context/brand.json`
- Modify: `BRAND.md`
- Modify: `DECISIONS.md`
- Modify: `MEMORY.md`
- Modify: `brand/clearance.md`
- Modify: `brand/strategy.md`
- Modify: `brand/messaging.md`
- Modify: `brand/identity.md`
- Modify: `brand/trademark-screening.md`

**Interfaces:**
- Consumes: the approved design in `docs/superpowers/specs/2026-08-17-sole-trader-name-adoption-design.md` and the UKIPO evidence in `brand/trademark-screening.md`.
- Produces: a consistent `brand_name_status` of `approved for sole-trader physiotherapy use`, a dated risk-acceptance record, and guidance that permits name use without claiming registration.

- [ ] **Step 1: Change the context test first**

Update `test_brand_context_uses_formal_and_display_names` to require:

```python
self.assertEqual(
    context["brand_name_status"],
    "approved for sole-trader physiotherapy use",
)
self.assertEqual(
    context["name_clearance"],
    {
        "status": "commercial risk accepted; UKIPO registration deferred",
        "screened_on": "2026-08-06",
        "accepted_on": "2026-08-17",
        "exact_live_matches": [],
        "material_similar_marks": [
            "UK00003586606",
            "UK00003957710",
        ],
        "basis": (
            "physiotherapy focus accepted as sufficient practical "
            "differentiation"
        ),
        "review_trigger": (
            "objection, material expansion beyond physiotherapy, licensing, "
            "ownership change, or decision to seek registration"
        ),
    },
)
self.assertNotIn("public use before clearance", context["prohibitions"])
self.assertIn(
    "use of registered trade mark symbol without registration",
    context["prohibitions"],
)
```

- [ ] **Step 2: Run the focused test and verify that it fails**

Run:

```bash
python3 -m unittest tests.test_brand_validation.BrandValidationTests.test_brand_context_uses_formal_and_display_names -v
```

Expected: `FAIL` because `.ai/context/brand.json` still records the public name as proposed and requires attorney review.

- [ ] **Step 3: Update the machine-readable brand decision**

In `.ai/context/brand.json`, set `brand_name_status` and `name_clearance` to the exact values asserted in Step 1. Replace the prohibition `public use before clearance` with `use of registered trade mark symbol without registration`. Preserve all other JSON values exactly.

- [ ] **Step 4: Update the authoritative human-readable records**

Make these exact governance changes:

- `BRAND.md`: state that the public name is approved for sole-trader physiotherapy use; state that UKIPO registration is deferred with residual risk accepted; remove trade-mark review as a launch blocker; retain the website-content and credential-claim boundaries.
- `DECISIONS.md`: add D-27, approved by the project sponsor on 2026-08-17, recording the physiotherapy-differentiation assumption, sole-trader adoption, deferred UKIPO registration and prohibition on `®`.
- `MEMORY.md`: add a dated 2026-08-17 entry recording the sponsor's risk decision and review triggers without rewriting the 2026-08-06 search evidence.
- `brand/clearance.md`: change the name row to `approved for sole-trader physiotherapy use; UKIPO registration deferred`; permit public name use; prohibit claiming registration or using `®`; retain the residual-risk and review-trigger wording.
- `brand/strategy.md`: replace proposed-name wording with the approved sole-trader-use boundary.
- `brand/messaging.md`: permit public use of the name, require the formal sole-trader identity on official paperwork, prohibit `®`, and retain credential and website-content restrictions.
- `brand/identity.md`: remove trade-mark review as an artwork-use prerequisite while preserving the exact raster-only artwork restrictions and separate website/credential gates.
- `brand/trademark-screening.md`: preserve all screening results and add a dated commercial-decision section explaining that the name is being adopted without legal clearance or registration.

- [ ] **Step 5: Run the focused test and verify that it passes**

Run:

```bash
python3 -m unittest tests.test_brand_validation.BrandValidationTests.test_brand_context_uses_formal_and_display_names -v
```

Expected: `OK` with one passing test.

- [ ] **Step 6: Run full validation**

Run:

```bash
python3 -m unittest discover -s tests -q
python3 scripts/validate_brand.py
git diff --check -- .ai/context/brand.json BRAND.md DECISIONS.md MEMORY.md brand/clearance.md brand/strategy.md brand/messaging.md brand/identity.md brand/trademark-screening.md tests/test_brand_validation.py
```

Expected: 56 tests pass, `Brand validation passed`, and `git diff --check` exits with no output.

- [ ] **Step 7: Review scope and commit**

Confirm that no logo, deployment, contact, credential-evidence, `AGENTS.md` or `sources/` file is in the intended commit. Then run:

```bash
git add .ai/context/brand.json BRAND.md DECISIONS.md MEMORY.md brand/clearance.md brand/strategy.md brand/messaging.md brand/identity.md brand/trademark-screening.md tests/test_brand_validation.py
git commit --only .ai/context/brand.json BRAND.md DECISIONS.md MEMORY.md brand/clearance.md brand/strategy.md brand/messaging.md brand/identity.md brand/trademark-screening.md tests/test_brand_validation.py -m "docs: adopt name for sole-trader use"
```

- [ ] **Step 8: Verify the committed state**

Run:

```bash
python3 -m unittest discover -s tests -q
python3 scripts/validate_brand.py
git show --stat --oneline --summary HEAD
git status --short
```

Expected: 56 tests pass, brand validation passes, the commit contains only the ten listed files, and the pre-existing `AGENTS.md` state remains outside the commit.
