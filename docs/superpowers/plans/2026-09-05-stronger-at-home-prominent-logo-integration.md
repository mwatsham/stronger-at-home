# Stronger at Home Prominent Logo Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate the unchanged approved raster logo into a compact editorial site-wide header and make the approved three-part promise the homepage headline.

**Architecture:** Replace the repeated single-row header on all eight public pages with the same two-row semantic header: an identity row containing the approved logo and service-area strap, followed by the existing navigation and appointment action. Implement the composition in the shared stylesheet, preserve the existing mobile disclosure script, and update only the homepage opening copy. Keep the existing public-source fingerprint gate authoritative by updating hashes only after the complete reviewed source changes are present.

**Tech Stack:** Semantic HTML5, PHP 8.4 page template markup, CSS custom properties and media queries, existing vanilla JavaScript menu enhancement, Python `unittest`, project validation and packaging scripts, GitHub Actions and cPanel Git deployment.

**Spec:** `docs/superpowers/specs/2026-09-05-stronger-at-home-prominent-logo-integration-design.md`

## Global Constraints

- Keep `site/assets/images/stronger-at-home-logo.png` byte-for-byte identical to `brand/assets/source/logo-primary-raster-v2-512.png` and SHA-256 `d557a0e8fd05efc86fcca2b3f63d807ad33f29527062697705a8e05616c6db39`.
- Do not create SVG, transparent-background, monochrome, cropped, masked, filtered, recoloured or AI-redrawn logo derivatives.
- Display the approved logo at approximately 315 CSS pixels wide on desktop without changing its intrinsic `width="512" height="160"` attributes.
- Use `#F9F4F2` only as the deliberate site identity surface matching the logo raster background; retain the main Warm Cream `#F7F2E8` page background.
- The visible strap must be exactly `Home physiotherapy for adults` followed by `Epsom and surrounding areas`.
- The homepage `h1` must be exactly `Experienced care. Personal progress. At home.`.
- The sentence immediately following the homepage `h1` must be exactly `Personal physiotherapy visits for adults recovering strength, mobility, balance and confidence.`.
- Preserve `Request an appointment` as the only high-emphasis header action and preserve the existing `Call Melanie` hero action.
- Preserve the existing five primary navigation destinations and the JavaScript-enhanced mobile menu behaviour.
- Ordinary text, metadata and accessible names must spell out `Stronger at Home`; `Stronger@Home` remains confined to the approved raster artwork.
- Preserve the existing logo link label and image alternative text.
- Retain one `h1` per page, keyboard operation, visible focus, the skip link, minimum touch targets and 320 CSS pixel reflow.
- Do not change appointment handling, contact details, clinical claims, credentials or production hosting.
- Review locally and on staging; production deployment requires a separate explicit approval.
- Treat all existing unrelated working-tree changes as user-owned and do not stage them.

---

### Task 1: Site-wide compact editorial identity header

**Files:**
- Modify: `tests/test_site_validation.py`
- Modify: `site/index.html`
- Modify: `site/about/index.html`
- Modify: `site/how-i-can-help/index.html`
- Modify: `site/appointments-and-fees/index.html`
- Modify: `site/contact/index.php`
- Modify: `site/privacy/index.html`
- Modify: `site/accessibility/index.html`
- Modify: `site/404.html`
- Modify: `site/assets/css/site.css`
- Modify: `scripts/validate_site.py`

**Interfaces:**
- Consumes: the existing `#primary-navigation` ID and `.menu-button` contract used by `site/assets/js/site.js`.
- Produces: shared `.site-identity`, `.brand-home`, `.brand-strap` and `.site-navigation` markup on every public page; matching responsive CSS; unchanged logo bytes.

- [ ] **Step 1: Establish an isolated implementation worktree**

Use `superpowers:using-git-worktrees` before editing. Create the feature branch from the current `develop` revision with a `codex/` prefix. Confirm that the isolated worktree does not contain the root workspace's unrelated staged `AGENTS.md` or untracked utility files.

- [ ] **Step 2: Add the shared-header path set and failing structural test**

Add this tuple below `PUBLIC_PAGES` in `tests/test_site_validation.py`:

```python
BRANDED_PAGE_PATHS = (
    "site/index.html",
    "site/about/index.html",
    "site/how-i-can-help/index.html",
    "site/appointments-and-fees/index.html",
    "site/contact/index.php",
    "site/privacy/index.html",
    "site/accessibility/index.html",
    "site/404.html",
)
```

Add these tests to `SiteValidationTests`:

```python
    def test_every_public_page_uses_the_approved_compact_editorial_header(self):
        for relative_path in BRANDED_PAGE_PATHS:
            with self.subTest(relative_path=relative_path):
                html = (ROOT / relative_path).read_text(encoding="utf-8")
                header = html.split('<header class="site-header">', 1)[1].split(
                    "</header>", 1
                )[0]

                self.assertEqual(header.count('class="site-identity"'), 1)
                self.assertEqual(header.count('class="brand-home"'), 1)
                self.assertEqual(header.count('class="brand-strap"'), 1)
                self.assertEqual(header.count('class="site-navigation"'), 1)
                self.assertEqual(header.count("Home physiotherapy for adults"), 1)
                self.assertEqual(header.count("Epsom and surrounding areas"), 1)
                self.assertEqual(
                    header.count(
                        'aria-label="Stronger at Home Physiotherapy, home"'
                    ),
                    1,
                )
                self.assertEqual(
                    header.count(
                        'alt="Stronger at Home Physiotherapy by Melanie Watsham"'
                    ),
                    1,
                )
                self.assertLess(
                    header.index('class="site-identity"'),
                    header.index('class="site-navigation"'),
                )
                self.assertLess(
                    header.index('class="menu-button"'),
                    header.index('id="primary-navigation"'),
                )

    def test_compact_editorial_header_styles_preserve_logo_scale_and_link_affordance(self):
        stylesheet = (ROOT / "site/assets/css/site.css").read_text(encoding="utf-8")

        self.assertIn("background: #F9F4F2;", stylesheet)
        self.assertIn("width: min(100%, 19.6875rem);", stylesheet)
        self.assertIn(".brand-strap", stylesheet)
        self.assertIn(".site-navigation", stylesheet)
        self.assertIn("#primary-navigation a:not(.button):hover", stylesheet)
        self.assertIn("#primary-navigation a:not(.button):focus-visible", stylesheet)
        self.assertIn('#primary-navigation a[aria-current="page"]', stylesheet)
        self.assertIn("text-decoration: underline;", stylesheet)

    def test_primary_navigation_marks_the_current_page(self):
        for relative_path, route in PUBLIC_PAGES.items():
            with self.subTest(relative_path=relative_path):
                html = (ROOT / relative_path).read_text(encoding="utf-8")
                header = html.split('<header class="site-header">', 1)[1].split(
                    "</header>", 1
                )[0]
                self.assertIn(f'aria-current="page" href="{route}"', header)
```

- [ ] **Step 3: Run the new tests and confirm the intended failure**

Run:

```bash
python -m unittest \
  tests.test_site_validation.SiteValidationTests.test_every_public_page_uses_the_approved_compact_editorial_header \
  tests.test_site_validation.SiteValidationTests.test_compact_editorial_header_styles_preserve_logo_scale_and_link_affordance \
  tests.test_site_validation.SiteValidationTests.test_primary_navigation_marks_the_current_page -v
```

Expected: all three tests fail because the new classes, 315-pixel logo width,
approved strap and current-page navigation state are absent.

- [ ] **Step 4: Replace the repeated header markup on all eight public pages**

In every page listed under **Files**, replace the current `<header class="site-header">…</header>` with this exact shared structure:

```html
  <header class="site-header">
    <div class="site-identity">
      <a class="brand-home" href="/" aria-label="Stronger at Home Physiotherapy, home">
        <img src="/assets/images/stronger-at-home-logo.png" alt="Stronger at Home Physiotherapy by Melanie Watsham" width="512" height="160">
      </a>
      <p class="brand-strap"><strong>Home physiotherapy for adults</strong><span>Epsom and surrounding areas</span></p>
    </div>
    <div class="site-navigation">
      <button class="menu-button" type="button" aria-expanded="false" aria-controls="primary-navigation">Menu</button>
      <nav id="primary-navigation" aria-label="Primary">
        <a href="/">Home</a><a href="/about/">About Melanie</a>
        <a href="/how-i-can-help/">How I can help</a>
        <a href="/appointments-and-fees/">Appointments &amp; fees</a>
        <a href="/contact/">Contact</a>
        <a class="button" href="/contact/#appointment-request">Request an appointment</a>
      </nav>
    </div>
  </header>
```

On the five primary pages, add `aria-current="page"` to the matching ordinary
navigation link. Use these exact route mappings:

```text
site/index.html                         -> href="/"
site/about/index.html                   -> href="/about/"
site/how-i-can-help/index.html           -> href="/how-i-can-help/"
site/appointments-and-fees/index.html   -> href="/appointments-and-fees/"
site/contact/index.php                  -> href="/contact/"
```

The Privacy, Accessibility and 404 pages do not mark a primary-navigation item
as current. Do not change the ordering, labels, URLs, accessible names or
intrinsic image dimensions.

- [ ] **Step 5: Replace the existing one-row header CSS with the compact editorial rules**

In `site/assets/css/site.css`, change the shared width rule so only `main` and `footer` are constrained:

```css
main,
footer {
  width: min(100% - 2.5rem, var(--brand-layout-content-max));
  margin-inline: auto;
}
```

Replace the existing `.site-header`, `.site-header img`, `#primary-navigation` and navigation-link rules with:

```css
.site-header {
  width: 100%;
  margin: 0;
  border-bottom: 2px solid var(--brand-colour-brand-warm-sand);
  background: #F9F4F2;
}

.site-identity,
.site-navigation {
  width: min(100% - 2.5rem, var(--brand-layout-content-max));
  margin-inline: auto;
}

.site-identity {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: clamp(1rem, 4vw, 3rem);
  padding-block: 0.75rem;
}

.brand-home {
  display: block;
  flex: 0 1 19.6875rem;
}

.site-header img {
  display: block;
  width: min(100%, 19.6875rem);
  height: auto;
}

.brand-strap {
  max-width: 19rem;
  margin: 0;
  padding-left: 1rem;
  border-left: 3px solid var(--brand-colour-accent-progress);
  text-align: right;
}

.brand-strap strong,
.brand-strap span {
  display: block;
}

.brand-strap strong {
  font-family: var(--brand-typography-family-display);
  font-size: 1.125rem;
  font-weight: var(--brand-typography-weight-semibold);
}

.brand-strap span { margin-top: 0.125rem; }

.site-navigation {
  display: flex;
  align-items: center;
  min-height: 3.5rem;
  border-top: 1px solid color-mix(in srgb, var(--brand-colour-brand-deep-navy) 18%, transparent);
}

#primary-navigation {
  display: flex;
  flex: 1 1 auto;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem 1rem;
}

#primary-navigation a:not(.button) {
  padding: 0.6rem 0;
  font-weight: var(--brand-typography-weight-semibold);
  text-decoration: none;
  text-underline-offset: 0.2em;
  text-decoration-thickness: 0.12em;
}

#primary-navigation a:not(.button):hover,
#primary-navigation a:not(.button):focus-visible,
#primary-navigation a[aria-current="page"] {
  text-decoration: underline;
}
```

Replace the existing header declarations inside `@media (max-width: 48rem)` with:

```css
  .site-identity {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }

  .brand-home { flex-basis: auto; }

  .brand-strap {
    max-width: 24rem;
    padding-top: 0.75rem;
    padding-left: 0;
    border-top: 2px solid var(--brand-colour-accent-progress);
    border-left: 0;
    text-align: center;
  }

  .site-navigation {
    flex-wrap: wrap;
    justify-content: flex-end;
    padding-block: 0.5rem;
  }

  .js .menu-button {
    display: block;
    margin-left: auto;
  }

  .js #primary-navigation { display: none; flex-basis: 100%; justify-content: flex-start; }

  .js #primary-navigation[data-open="true"] { display: flex; }
  #primary-navigation .button { width: 100%; }
```

Keep the existing `.menu-button` declaration and the existing high-contrast focus rule unchanged.

- [ ] **Step 6: Run the focused structural and interaction tests**

Run:

```bash
python -m unittest \
  tests.test_site_validation.SiteValidationTests.test_every_public_page_uses_the_approved_compact_editorial_header \
  tests.test_site_validation.SiteValidationTests.test_compact_editorial_header_styles_preserve_logo_scale_and_link_affordance \
  tests.test_site_validation.SiteValidationTests.test_primary_navigation_marks_the_current_page \
  tests.test_site_validation.SiteValidationTests.test_mobile_menu_is_a_javascript_enhancement_with_an_accurate_disclosure_control \
  tests.test_site_validation.SiteValidationTests.test_focus_indicator_uses_the_high_contrast_two_colour_treatment \
  tests.test_site_validation.SiteValidationTests.test_every_primary_page_has_common_landmarks_and_one_h1 -v
```

Expected: PASS.

- [ ] **Step 7: Prove that the approved logo bytes did not change**

Run:

```bash
shasum -a 256 \
  site/assets/images/stronger-at-home-logo.png \
  brand/assets/source/logo-primary-raster-v2-512.png
```

Expected: both lines begin with `d557a0e8fd05efc86fcca2b3f63d807ad33f29527062697705a8e05616c6db39`.

- [ ] **Step 8: Refresh only the changed public-source approval hashes**

Run:

```bash
shasum -a 256 \
  site/404.html \
  site/about/index.html \
  site/accessibility/index.html \
  site/appointments-and-fees/index.html \
  site/assets/css/site.css \
  site/contact/index.php \
  site/how-i-can-help/index.html \
  site/index.html \
  site/privacy/index.html
```

Copy each printed digest into the matching existing key in
`APPROVED_PUBLIC_SOURCE_SHA256` inside `scripts/validate_site.py`. Leave every
unchanged entry, `EXPECTED_LOGO_SHA256`, public path and directory boundary
untouched.

- [ ] **Step 9: Run the complete Python site validation suite**

Run:

```bash
python -m unittest tests.test_site_validation tests.test_site_asset_sync -v
python scripts/validate_site.py --mode development
python scripts/validate_site.py --mode staging
```

Expected: all tests pass and both validator commands report no errors.

- [ ] **Step 10: Commit the site-wide identity header**

Stage only the files listed in this task, verify the staged paths and commit:

```bash
git add \
  tests/test_site_validation.py \
  site/index.html \
  site/about/index.html \
  site/how-i-can-help/index.html \
  site/appointments-and-fees/index.html \
  site/contact/index.php \
  site/privacy/index.html \
  site/accessibility/index.html \
  site/404.html \
  site/assets/css/site.css \
  scripts/validate_site.py
git diff --cached --check
git diff --cached --name-only
git commit -m "feat: integrate prominent site identity header"
```

Expected staged paths: exactly the eleven files listed above.

---

### Task 2: Promise-led homepage opening

**Files:**
- Modify: `tests/test_site_validation.py`
- Modify: `site/index.html`
- Modify: `scripts/validate_site.py`

**Interfaces:**
- Consumes: the existing homepage `#introduction` section, `.hero-copy`, `.eyebrow`, `.lead`, `.action-group` and `.trust-point` styles.
- Produces: exact approved homepage `h1` and explanatory sentence while preserving the existing actions, trust point, section order and portrait.

- [ ] **Step 1: Change the homepage content-order test to the approved promise**

In `test_homepage_uses_approved_patient_first_content_order`, replace:

```python
        self.assertIn("Physiotherapy to help you feel stronger at home", html)
```

with:

```python
        self.assertIn("Experienced care. Personal progress. At home.", html)
```

Add this focused test beneath it:

```python
    def test_homepage_uses_the_approved_promise_led_opening(self):
        html = (ROOT / "site/index.html").read_text(encoding="utf-8")
        introduction = html.split('<section id="introduction"', 1)[1].split(
            '<section id="how-i-can-help"', 1
        )[0]

        heading = "Experienced care. Personal progress. At home."
        explanation = (
            "Personal physiotherapy visits for adults recovering strength, "
            "mobility, balance and confidence."
        )
        self.assertEqual(introduction.count(f"<h1>{heading}</h1>"), 1)
        self.assertEqual(introduction.count(f'<p class="lead">{explanation}</p>'), 1)
        self.assertLess(introduction.index(heading), introduction.index(explanation))
        self.assertNotIn("Physiotherapy to help you feel stronger at home", introduction)
        self.assertIn("Request an appointment", introduction)
        self.assertIn("Call Melanie", introduction)
        self.assertIn("20+ years of NHS experience", introduction)
```

- [ ] **Step 2: Run the promise-led test and confirm it fails**

Run:

```bash
python -m unittest \
  tests.test_site_validation.SiteValidationTests.test_homepage_uses_the_approved_promise_led_opening -v
```

Expected: FAIL because the homepage still contains the previous heading and lead.

- [ ] **Step 3: Replace only the homepage heading and lead**

In `site/index.html`, change the opening copy inside `.hero-copy` to:

```html
        <p class="eyebrow">Home physiotherapy in Epsom</p>
        <h1>Experienced care. Personal progress. At home.</h1>
        <p class="lead">Personal physiotherapy visits for adults recovering strength, mobility, balance and confidence.</p>
```

Keep the existing action group, telephone link, trust point and portrait markup unchanged.

- [ ] **Step 4: Run the homepage content tests**

Run:

```bash
python -m unittest \
  tests.test_site_validation.SiteValidationTests.test_homepage_uses_approved_patient_first_content_order \
  tests.test_site_validation.SiteValidationTests.test_homepage_uses_the_approved_promise_led_opening \
  tests.test_site_validation.SiteValidationTests.test_homepage_intro_uses_appointment_request_as_primary_action \
  tests.test_site_validation.SiteValidationTests.test_homepage_claim_boundary_preserves_approved_facts_without_invented_claims \
  tests.test_site_validation.SiteValidationTests.test_homepage_uses_the_approved_web_portrait -v
```

Expected: PASS.

- [ ] **Step 5: Refresh the homepage public-source approval hash**

Run:

```bash
shasum -a 256 site/index.html
```

Replace only the value for `site/index.html` in
`APPROVED_PUBLIC_SOURCE_SHA256` with the printed digest.

- [ ] **Step 6: Run the full public-content guard**

Run:

```bash
python -m unittest tests.test_site_validation -v
python scripts/validate_site.py --mode development
python scripts/validate_site.py --mode staging
```

Expected: all tests pass and both validators report no errors.

- [ ] **Step 7: Commit the promise-led homepage copy**

```bash
git add tests/test_site_validation.py site/index.html scripts/validate_site.py
git diff --cached --check
git diff --cached --name-only
git commit -m "feat: lead homepage with approved brand promise"
```

Expected staged paths: exactly the three files listed above.

---

### Task 3: Responsive, accessibility and visual verification

**Files:**
- Modify only if a verified defect is found: `site/assets/css/site.css`
- Modify only when the stylesheet changes: `scripts/validate_site.py`
- Create during review but do not commit: `output/review/logo-integration/`

**Interfaces:**
- Consumes: the finished shared header, homepage opening, existing menu script and existing local PHP preview workflow.
- Produces: evidence that the implementation reflows, remains keyboard-operable, keeps the approved logo unchanged and matches the approved B3 composition.

- [ ] **Step 1: Run the complete local quality gate before browser review**

Run:

```bash
for test_file in tests/php/*Test.php; do php "$test_file" || exit 1; done
for php_file in $(find site tests/php config -type f -name '*.php' | sort); do php -l "$php_file" || exit 1; done
python -m unittest discover -s tests -q
python scripts/validate_site.py --mode development
python scripts/validate_site.py --mode staging
python scripts/validate_brand.py
node --check site/assets/js/site.js
python scripts/package_site.py --environment staging --destination output/site-package
git diff --exit-code -- brand/generated/tokens.css site/assets/css/brand-tokens.css
```

Expected: every command succeeds, validators report no errors, and token files show no generated drift.

- [ ] **Step 2: Start a local PHP preview and create the review directory**

Run the existing local preview workflow with `site/` as the document root on an available loopback port. Create `output/review/logo-integration/` for screenshots. Keep the preview bound to `127.0.0.1`; do not expose it to the network.

- [ ] **Step 3: Review required widths and horizontal reflow**

For `/`, `/about/`, `/how-i-can-help/`, `/appointments-and-fees/`,
`/contact/`, `/privacy/`, `/accessibility/` and `/404.html`, inspect 320, 360,
768, 1024 and 1280 CSS pixel widths.

At each route and width, verify:

- `document.documentElement.scrollWidth <= document.documentElement.clientWidth`;
- the logo is uncropped and keeps its 512:160 intrinsic ratio;
- the logo tile edge is not visible against the `#F9F4F2` identity band;
- the strap remains readable and subordinate to the logo;
- navigation and appointment action do not overlap;
- headings, content and footer do not clip.

Save full-page homepage captures at all five widths, plus each remaining route at
360 and 1280 CSS pixels, under `output/review/logo-integration/` using the route
and viewport in each filename.

- [ ] **Step 4: Review keyboard and 200-percent zoom behaviour**

At 360 CSS pixels:

1. Tab from the skip link to the logo and Menu button.
2. Activate Menu with Enter and confirm `aria-expanded="true"` and visible navigation.
3. Continue through every navigation link and the appointment action.
4. Close the menu with Space and confirm focus remains on the Menu button.
5. Confirm the two-colour focus indicator remains visible on the identity surface.

At 200-percent browser zoom, repeat the homepage and contact-page overflow check,
open the mobile navigation, and confirm the appointment action remains reachable.

Expected: every interaction succeeds without pointer input, clipping or hidden
essential content.

- [ ] **Step 5: Inspect the approved visual hierarchy**

At 1280 CSS pixels, confirm in order:

1. The logo is the dominant header element but remains smaller than the hero promise.
2. The strap reads as supporting identity information, not a second headline.
3. Ordinary navigation links are quieter than `Request an appointment`.
4. The homepage promise reads as three short thoughts without an awkward orphan.
5. Melanie's portrait remains balanced with the copy.
6. The hero actions and `20+ years of NHS experience` remain visible.

If any check fails, stop this task and use `superpowers:systematic-debugging` to
identify the layout cause before editing. After any CSS correction, recompute
only the `site/assets/css/site.css` public-source hash, rerun Steps 1–5 and commit
the verified correction as `fix: refine responsive identity header`.

- [ ] **Step 6: Verify the working tree contains no unintended public changes**

Run:

```bash
git status --short
git diff --check
git diff --name-only develop...HEAD
shasum -a 256 \
  site/assets/images/stronger-at-home-logo.png \
  brand/assets/source/logo-primary-raster-v2-512.png
```

Expected: only planned implementation, test, validator, spec and plan files are
listed; both logo hashes remain the approved `d557a0e8fd05efc86fcca2b3f63d807ad33f29527062697705a8e05616c6db39`.

---

### Task 4: Review, integration and staging release

**Files:**
- Include in the branch: `docs/superpowers/specs/2026-09-05-stronger-at-home-prominent-logo-integration-design.md`
- Include in the branch: `docs/superpowers/plans/2026-09-05-stronger-at-home-prominent-logo-integration.md`
- Do not modify: `.github/workflows/release-production.yml`

**Interfaces:**
- Consumes: a fully passing feature branch and the existing GitHub Actions release flow.
- Produces: reviewed changes merged into `develop`, an automatically prepared `deploy-staging` revision and a staging-only sponsor review checkpoint.

- [ ] **Step 1: Commit the approved design and implementation plan if they are not already on the feature branch**

Copy the two documents from the project workspace into the isolated feature
worktree if required, then stage only those paths:

```bash
git add \
  docs/superpowers/specs/2026-09-05-stronger-at-home-prominent-logo-integration-design.md \
  docs/superpowers/plans/2026-09-05-stronger-at-home-prominent-logo-integration.md
git diff --cached --check
git commit -m "docs: record approved logo integration design"
```

- [ ] **Step 2: Request a code review**

Use `superpowers:requesting-code-review`. The reviewer must compare the branch
against the approved spec and specifically verify:

- identical header markup across all eight public pages;
- no logo-byte or asset-manifest change;
- exact strap and homepage wording;
- preserved mobile menu and focus behaviour;
- narrow-screen reflow and restrained navigation hierarchy;
- no production workflow or deployment change.

Resolve every material finding using `superpowers:receiving-code-review`, rerun
the complete quality gate and commit each verified fix.

- [ ] **Step 3: Finish the development branch**

Use `superpowers:finishing-a-development-branch`. Push the feature branch and
open a pull request targeting `develop`. Include the approved spec, verification
commands, logo SHA-256 evidence and local screenshot summary in the pull request
description.

Wait for the pull-request CI quality gate to pass. Present the pull request and
review result to the project sponsor before merging because a merge to `develop`
starts the staging release workflow.

- [ ] **Step 4: Merge to develop only after explicit sponsor approval**

After approval, merge the pull request into `develop`. Confirm that both the CI
workflow and `Prepare staging release branch` workflow pass and that the latter
updates `deploy-staging` from the exact merged `develop` revision.

- [ ] **Step 5: Verify staging without touching production**

Use the existing cPanel Git deployment workflow to confirm the current
`deploy-staging` revision is deployed to `staging.stronger-at-home.co.uk`. If
cPanel does not update automatically, use the `cpanel-integration` skill for the
narrow repository update/deployment operation documented in
`docs/website-staging-runbook.md`.

On staging, repeat the homepage checks at 360, 768 and 1280 CSS pixels; verify
the mobile menu, appointment link, logo bytes, HTTPS, staging `noindex` response
and absence of console errors.

Stop at the staging review checkpoint. Do not merge to `main`, run the
production release workflow or mutate the production cPanel document root.
