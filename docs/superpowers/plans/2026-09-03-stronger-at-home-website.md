# Stronger at Home Physiotherapy Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and stage a calm, accessible five-page website that helps an adult patient understand Stronger at Home Physiotherapy and safely request an appointment.

**Architecture:** Serve standards-based pages, shared CSS and minimal JavaScript directly from the existing cPanel document root. Isolate the enquiry workflow in PHP 8.1+ classes behind a mail-transport interface, use PHPMailer 7.1.1 for authenticated SMTP, store no patient database, and deploy to staging before any production release.

**Tech Stack:** HTML5, CSS, vanilla JavaScript, Python 3.14 standard-library audits, PHP 8.1+, Composer 2, PHPMailer 7.1.1, cPanel staging and production document roots.

**Spec:** `docs/superpowers/specs/2026-09-03-stronger-at-home-website-design.md`

## Global Constraints

- Read the spec, `AGENTS.md`, `BRAND.md`, `brand/messaging.md`, `brand/identity.md`, `brand/clearance.md`, `brand/tokens.json` and `.ai/context/brand.json` before editing.
- Work in the existing isolated worktree on `codex/website-design-spec`; preserve unrelated user files and all read-only `sources/` content.
- Use `Stronger at Home Physiotherapy` in prose and reserve `Stronger@Home` for the approved raster wordmark.
- Use only the approved claim `20+ years of NHS experience`; omit HCPC, CSP, AGILE and ATOCP claims until separately verified.
- Do not invent referral suitability, exclusions, emergency advice, testimonials, reviews, treatment outcomes or additional service locations.
- Do not redraw, recolour, crop, trace, vectorise, remove the background from or generate a substitute for the approved logo.
- `Request an appointment` is an enquiry action; success messages must say that Melanie confirms availability directly.
- Do not create a CMS, analytics, advertising, online payments, automated calendar, patient accounts or a clinical database.
- Target WCAG 2.2 AA and responsive reflow from 320 CSS pixels upward.
- Production requires a final portrait, approved privacy wording, verified form delivery and Melanie Watsham's explicit approval.
- Use `/opt/homebrew/bin/python3` for existing tests because it has the pinned Pillow 12.3.0 dependency.
- PHP and Composer are absent locally. Before PHP work, request approval to install PHP 8.1+ and Composer 2; do not install dependencies silently.
- Before PHP work, use read-only cPanel inspection to confirm that staging supports PHP 8.1 or newer. Stop if it does not.
- Lock `phpmailer/phpmailer` at `7.1.1`; never implement SMTP protocol handling directly.
- Commit after each task, run `git diff --check` before every commit, and never push or deploy without an explicit checkpoint.

## File Structure

- `site/index.html` — reassurance-first homepage.
- `site/about/index.html` — Melanie's approach and approved experience.
- `site/how-i-can-help/index.html` — approved need-led service content.
- `site/appointments-and-fees/index.html` — visit details, area and fees.
- `site/contact/index.php` — contact page, CSRF token and form feedback.
- `site/privacy/index.html`, `site/accessibility/index.html`, `site/404.html` — supporting pages.
- `site/assets/css/brand-tokens.css`, `site/assets/css/site.css` — synced tokens and site styles.
- `site/assets/fonts/source-serif-4.ttf`, `site/assets/fonts/atkinson-hyperlegible-next.ttf` — exact licensed local brand fonts.
- `site/assets/js/site.js` — menu and progressive form enhancement only.
- `site/assets/images/stronger-at-home-logo.png` — exact approved 512-pixel logo copy.
- `site/assets/images/portrait-placeholder.svg` — development-only non-likeness placeholder.
- `site/api/enquiry.php` — POST entry point.
- `site/api/src/` — validation, message, rate-limit, transport and controller classes.
- `config/site.example.php` — environment-driven non-secret configuration contract.
- `composer.json`, `composer.lock` — PHP dependency definition and exact lock.
- `scripts/sync_site_brand_assets.py` — deterministic approved-asset sync.
- `scripts/validate_site.py` — structure, content and release-gate validation.
- `scripts/package_site.py` — deterministic secret-free staging package.
- `tests/test_site_asset_sync.py`, `tests/test_site_validation.py`, `tests/test_site_package.py` — Python site tests.
- `tests/php/` — dependency-free PHP test runner and domain tests.
- `docs/website-content-review.md`, `docs/website-staging-runbook.md` — approval and deployment records.

---

### Task 1: Establish the site shell and immutable asset sync

**Files:**
- Create: `scripts/sync_site_brand_assets.py`
- Create: `tests/test_site_asset_sync.py`
- Create: `tests/test_site_validation.py`
- Create: the five primary page files and shared CSS/JavaScript files listed above
- Generate: `site/assets/css/brand-tokens.css`
- Generate: `site/assets/images/stronger-at-home-logo.png`
- Generate: the two local font files under `site/assets/fonts/`

**Interfaces:**
- Consumes: `brand/generated/tokens.css` and `brand/assets/source/logo-primary-raster-v2-512.png`.
- Produces: `sync_site_brand_assets(project_root: Path, site_root: Path | None = None) -> None`; common landmarks and navigation URLs.

- [ ] **Step 1: Write the failing asset-sync test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from scripts.sync_site_brand_assets import sync_site_brand_assets

ROOT = Path(__file__).resolve().parents[1]

class SiteAssetSyncTests(unittest.TestCase):
    def test_sync_copies_approved_logo_bytes_and_generated_tokens(self):
        with TemporaryDirectory() as directory:
            target = Path(directory)
            sync_site_brand_assets(ROOT, target)
            self.assertEqual(
                (target / "assets/images/stronger-at-home-logo.png").read_bytes(),
                (ROOT / "brand/assets/source/logo-primary-raster-v2-512.png").read_bytes(),
            )
            self.assertEqual(
                (target / "assets/css/brand-tokens.css").read_bytes(),
                (ROOT / "brand/generated/tokens.css").read_bytes(),
            )
            for filename in ("source-serif-4.ttf", "atkinson-hyperlegible-next.ttf"):
                self.assertEqual(
                    (target / "assets/fonts" / filename).read_bytes(),
                    (ROOT / "brand/fonts" / filename).read_bytes(),
                )
```

- [ ] **Step 2: Run it and verify the missing-module failure**

Run: `/opt/homebrew/bin/python3 -m unittest tests.test_site_asset_sync -v`

Expected: ERROR because `scripts.sync_site_brand_assets` does not exist.

- [ ] **Step 3: Implement the deterministic copy**

```python
from pathlib import Path
import shutil

def sync_site_brand_assets(project_root: Path, site_root: Path | None = None) -> None:
    destination = site_root or project_root / "site"
    pairs = {
        project_root / "brand/generated/tokens.css": destination / "assets/css/brand-tokens.css",
        project_root / "brand/assets/source/logo-primary-raster-v2-512.png": destination / "assets/images/stronger-at-home-logo.png",
        project_root / "brand/fonts/source-serif-4.ttf": destination / "assets/fonts/source-serif-4.ttf",
        project_root / "brand/fonts/atkinson-hyperlegible-next.ttf": destination / "assets/fonts/atkinson-hyperlegible-next.ttf",
    }
    for source, target in pairs.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
```

- [ ] **Step 4: Run the sync and confirm the test passes**

Run: `/opt/homebrew/bin/python3 scripts/sync_site_brand_assets.py`

Run: `/opt/homebrew/bin/python3 -m unittest tests.test_site_asset_sync -v`

Expected: 1 test passes and the output logo is byte-identical to the approved source.

- [ ] **Step 5: Write failing common-shell tests**

```python
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = {
    "site/index.html": "/", "site/about/index.html": "/about/",
    "site/how-i-can-help/index.html": "/how-i-can-help/",
    "site/appointments-and-fees/index.html": "/appointments-and-fees/",
    "site/contact/index.php": "/contact/",
}

class LandmarkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.links, self.h1_count = [], [], 0
    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.tags.append(tag)
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        if tag == "h1":
            self.h1_count += 1

def test_every_primary_page_has_common_landmarks_and_one_h1(self):
    for relative_path in PUBLIC_PAGES:
        parser = LandmarkParser()
        parser.feed((ROOT / relative_path).read_text(encoding="utf-8"))
        self.assertTrue({"header", "nav", "main", "footer"}.issubset(parser.tags))
        self.assertEqual(parser.h1_count, 1, relative_path)

def test_every_page_links_all_primary_routes_and_appointment_action(self):
    expected = set(PUBLIC_PAGES.values()) | {"/contact/#appointment-request"}
    for relative_path in PUBLIC_PAGES:
        parser = LandmarkParser()
        parser.feed((ROOT / relative_path).read_text(encoding="utf-8"))
        self.assertTrue(expected.issubset(set(parser.links)), relative_path)
```

- [ ] **Step 6: Run the shell tests and verify missing-page failures**

Run: `/opt/homebrew/bin/python3 -m unittest tests.test_site_validation -v`

Expected: ERROR because the five pages do not exist.

- [ ] **Step 7: Create the semantic shell on every page**

```html
<a class="skip-link" href="#main-content">Skip to main content</a>
<header class="site-header">
  <a href="/" aria-label="Stronger at Home Physiotherapy, home">
    <img src="/assets/images/stronger-at-home-logo.png" alt="Stronger at Home Physiotherapy by Melanie Watsham" width="512" height="160">
  </a>
  <button class="menu-button" type="button" aria-expanded="false" aria-controls="primary-navigation">Menu</button>
  <nav id="primary-navigation" aria-label="Primary">
    <a href="/">Home</a><a href="/about/">About Melanie</a>
    <a href="/how-i-can-help/">How I can help</a>
    <a href="/appointments-and-fees/">Appointments &amp; fees</a>
    <a href="/contact/">Contact</a>
    <a class="button" href="/contact/#appointment-request">Request an appointment</a>
  </nav>
</header>
<main id="main-content"><h1>Physiotherapy to help you feel stronger at home</h1></main>
<footer>Melanie Watsham trading as Stronger at Home Physiotherapy</footer>
```

Each page also needs `lang="en-GB"`, viewport metadata, a unique title and
description, its canonical production URL, the two CSS files and deferred site
JavaScript.

Begin `site.css` with the local font faces and use the generated family tokens:

```css
@font-face { font-family:"Source Serif 4"; src:url("../fonts/source-serif-4.ttf") format("truetype"); font-display:swap; }
@font-face { font-family:"Atkinson Hyperlegible Next"; src:url("../fonts/atkinson-hyperlegible-next.ttf") format("truetype"); font-display:swap; }
body { font-family:var(--brand-typography-family-body); color:var(--brand-colour-text-primary); }
h1,h2,h3 { font-family:var(--brand-typography-family-display); }
```

- [ ] **Step 8: Add the labelled menu disclosure**

```javascript
const button = document.querySelector('.menu-button');
const navigation = document.querySelector('#primary-navigation');
if (button && navigation) {
  button.addEventListener('click', () => {
    const expanded = button.getAttribute('aria-expanded') === 'true';
    button.setAttribute('aria-expanded', String(!expanded));
    navigation.dataset.open = String(!expanded);
  });
}
```

- [ ] **Step 9: Run site and full project tests**

Run: `/opt/homebrew/bin/python3 -m unittest tests.test_site_validation tests.test_site_asset_sync -v`

Run: `/opt/homebrew/bin/python3 -m unittest discover -s tests -q`

Expected: all tests pass.

- [ ] **Step 10: Commit the foundation**

```bash
git add scripts/sync_site_brand_assets.py tests/test_site_asset_sync.py tests/test_site_validation.py site
git diff --cached --check
git commit -m "feat: establish website shell"
```

### Task 2: Build the approved calm-editorial homepage

**Files:**
- Modify: `tests/test_site_validation.py`, `site/index.html`, `site/assets/css/site.css`
- Create: `site/assets/images/portrait-placeholder.svg`

**Interfaces:**
- Consumes: the common shell and approved brand assets.
- Produces: seven ordered homepage sections and reusable calm-editorial layout components.

- [ ] **Step 1: Add failing hierarchy and portrait-gate tests**

```python
def test_homepage_uses_approved_patient_first_content_order(self):
    html = (ROOT / "site/index.html").read_text(encoding="utf-8")
    ids = ["introduction", "how-i-can-help", "benefits-at-home", "meet-melanie", "appointments", "area-and-fees", "request-an-appointment"]
    positions = [html.index(f'id="{section_id}"') for section_id in ids]
    self.assertEqual(positions, sorted(positions))
    self.assertIn("Physiotherapy to help you feel stronger at home", html)
    self.assertIn("20+ years of NHS experience", html)

def test_development_portrait_is_a_production_blocker(self):
    html = (ROOT / "site/index.html").read_text(encoding="utf-8")
    self.assertIn('data-production-blocker="portrait"', html)
    self.assertIn("Professional portrait to be supplied", html)
```

- [ ] **Step 2: Run the tests and verify missing-content failures**

Run: `/opt/homebrew/bin/python3 -m unittest tests.test_site_validation -v`

Expected: FAIL because the shell lacks the approved hierarchy.

- [ ] **Step 3: Implement the approved hero and seven sections**

```html
<section id="introduction" class="hero split">
  <div>
    <p class="eyebrow">Home physiotherapy in Epsom</p>
    <h1>Physiotherapy to help you feel stronger at home</h1>
    <p>Personal home visits for adults in Epsom and surrounding areas, supporting recovery, mobility, balance and confidence.</p>
    <a class="button" href="/contact/#appointment-request">Request an appointment</a>
    <a class="text-link" href="tel:+447843497871">Call Melanie</a>
    <p class="trust-point">20+ years of NHS experience</p>
  </div>
  <figure class="portrait-frame" data-production-blocker="portrait">
    <img src="/assets/images/portrait-placeholder.svg" alt="">
    <figcaption>Professional portrait to be supplied</figcaption>
  </figure>
</section>
```

Follow with need-led cards, benefits of at-home care, Melanie's short
introduction, 60/45-minute appointment cards, area-and-fee guidance and the
final request action. Do not use the exploratory mockup's unapproved
first-person quotation.

- [ ] **Step 4: Add the responsive layout primitives**

```css
.section { padding: clamp(3rem, 7vw, 6rem) max(1.25rem, calc((100% - 72rem) / 2)); }
.split { display:grid; grid-template-columns:minmax(0,1.12fr) minmax(16rem,.88fr); gap:clamp(2rem,5vw,4.5rem); align-items:center; }
.card-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1rem; }
.button { min-height:44px; display:inline-flex; align-items:center; justify-content:center; border-radius:999px; }
@media (max-width:48rem) { .split,.card-grid { grid-template-columns:1fr; } }
@media (prefers-reduced-motion:reduce) { *,*::before,*::after { scroll-behavior:auto!important; transition-duration:.01ms!important; } }
```

- [ ] **Step 5: Run tests and brand validation**

Run: `/opt/homebrew/bin/python3 -m unittest tests.test_site_validation -v`

Run: `/opt/homebrew/bin/python3 scripts/validate_brand.py`

Expected: all homepage tests pass; brand validation prints `Brand validation passed`.

- [ ] **Step 6: Commit the homepage**

```bash
git add site/index.html site/assets/css/site.css site/assets/images/portrait-placeholder.svg tests/test_site_validation.py
git diff --cached --check
git commit -m "feat: build patient-first homepage"
```

### Task 3: Complete the informational pages

**Files:**
- Modify: `tests/test_site_validation.py`, the About, How I Can Help, and Appointments & Fees pages, and `site/assets/css/site.css`

**Interfaces:**
- Consumes: common shell and calm-editorial components.
- Produces: three complete pages containing only approved service facts.

- [ ] **Step 1: Add failing approved-fact and prohibition tests**

```python
def test_inner_pages_contain_approved_facts(self):
    about = (ROOT / "site/about/index.html").read_text(encoding="utf-8")
    help_page = (ROOT / "site/how-i-can-help/index.html").read_text(encoding="utf-8")
    appointments = (ROOT / "site/appointments-and-fees/index.html").read_text(encoding="utf-8")
    self.assertIn("20+ years of NHS experience", about)
    for phrase in ("Recovery after surgery", "Following a hospital admission", "Rehabilitation following a fall", "Falls prevention", "Mobility and balance"):
        self.assertIn(phrase, help_page)
    for phrase in ("60 minutes", "45 minutes", "approximately 10 miles of Epsom", "subject to availability", "cash or bank transfer"):
        self.assertIn(phrase, appointments)

def test_pages_omit_gated_claims(self):
    combined = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in PUBLIC_PAGES)
    for text in ("HCPC registered", "CSP member", "AGILE member", "ATOCP member", "guaranteed", "walk-in clinic"):
        self.assertNotIn(text.lower(), combined.lower())
```

- [ ] **Step 2: Run the tests and verify missing-fact failures**

Run: `/opt/homebrew/bin/python3 -m unittest tests.test_site_validation -v`

Expected: FAIL because the page shells lack the approved facts.

- [ ] **Step 3: Implement the exact content boundaries**

```html
<!-- about -->
<h1>About Melanie</h1>
<p>Melanie brings more than 20 years of NHS experience to home physiotherapy visits.</p>

<!-- appointments and fees -->
<h1>Appointments and fees</h1>
<p>Initial assessments last 60 minutes. Follow-up appointments last 45 minutes.</p>
<p>Appointments are arranged flexibly, subject to availability.</p>
<p>Home visits are available within approximately 10 miles of Epsom and surrounding areas. Availability is confirmed using your address.</p>
<p>Fees are quoted individually because travel requirements vary by location. Please provide your postcode or address when enquiring. A fixed price will be confirmed and agreed before the appointment is booked.</p>
<p>Payment can be made by cash or bank transfer.</p>
```

The How I Can Help page uses the five tested need-led headings. Do not add
payment timing, bank details, diagnoses, credentials or referral eligibility.

- [ ] **Step 4: Run all Python tests**

Run: `/opt/homebrew/bin/python3 -m unittest discover -s tests -q`

Expected: all tests pass.

- [ ] **Step 5: Commit the content pages**

```bash
git add site/about site/how-i-can-help site/appointments-and-fees site/assets/css/site.css tests/test_site_validation.py
git diff --cached --check
git commit -m "feat: add approved website content"
```

### Task 4: Add the appointment-request form

**Files:**
- Modify: `tests/test_site_validation.py`, `site/contact/index.php`, `site/assets/css/site.css`, `site/assets/js/site.js`

**Interfaces:**
- Produces: `POST /api/enquiry.php` fields `name`, `email`, `phone`, `preferred_contact`, `postcode`, `message`, `privacy_acknowledged`, `website`, `csrf_token`.

- [ ] **Step 1: Add a failing form-contract test**

```python
class FormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms, self.controls = [], {}
    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "form":
            self.forms.append(attributes)
        if tag in {"input", "select", "textarea"} and attributes.get("name"):
            self.controls[attributes["name"]] = attributes

def test_contact_form_collects_only_approved_fields(self):
    parser = FormParser()
    parser.feed((ROOT / "site/contact/index.php").read_text(encoding="utf-8"))
    self.assertEqual(parser.forms[0]["method"].lower(), "post")
    self.assertEqual(parser.forms[0]["action"], "/api/enquiry.php")
    self.assertEqual(set(parser.controls), {"name", "email", "phone", "preferred_contact", "postcode", "message", "privacy_acknowledged", "website", "csrf_token"})
    self.assertNotIn("date_of_birth", parser.controls)
    self.assertNotIn("medical_history", parser.controls)
```

- [ ] **Step 2: Run it and verify the missing-form failure**

Run: `/opt/homebrew/bin/python3 -m unittest tests.test_site_validation.SiteValidationTests.test_contact_form_collects_only_approved_fields -v`

Expected: FAIL because no form exists.

- [ ] **Step 3: Implement labelled fields and safe guidance**

```html
<form id="appointment-request" method="post" action="/api/enquiry.php" novalidate>
  <p>Use this form to request an appointment. Melanie will contact you directly to confirm availability.</p>
  <p class="notice">Please do not include detailed or urgent medical information.</p>
  <label for="name">Name</label><input id="name" name="name" autocomplete="name" required maxlength="100">
  <label for="email">Email address</label><input id="email" name="email" type="email" autocomplete="email" maxlength="254">
  <label for="phone">Phone number</label><input id="phone" name="phone" type="tel" autocomplete="tel" maxlength="30">
  <label for="preferred-contact">Preferred contact method</label>
  <select id="preferred-contact" name="preferred_contact" required><option value="email">Email</option><option value="phone">Phone</option></select>
  <label for="postcode">Postcode</label><input id="postcode" name="postcode" autocomplete="postal-code" required maxlength="10">
  <label for="message">Short enquiry</label><textarea id="message" name="message" required minlength="10" maxlength="1000"></textarea>
  <label><input name="privacy_acknowledged" type="checkbox" value="1" required> I have read the <a href="/privacy/">privacy notice</a>.</label>
  <div class="honeypot" aria-hidden="true"><label for="website">Leave this field blank</label><input id="website" name="website" tabindex="-1" autocomplete="off"></div>
  <input name="csrf_token" type="hidden" value="<?= htmlspecialchars($csrfToken, ENT_QUOTES, 'UTF-8') ?>">
  <button type="submit">Send appointment request</button>
</form>
```

Add a live region for one-use status/errors. Preserve only safely escaped
name, email, phone, preferred contact and postcode; never preserve the message.

- [ ] **Step 4: Add progressive invalid-state focus support**

```javascript
const form = document.querySelector('#appointment-request');
if (form) {
  form.addEventListener('invalid', event => event.target.setAttribute('aria-invalid', 'true'), true);
  form.addEventListener('input', event => event.target.removeAttribute('aria-invalid'));
}
```

- [ ] **Step 5: Run all Python tests and commit**

Run: `/opt/homebrew/bin/python3 -m unittest discover -s tests -q`

Expected: all tests pass.

```bash
git add site/contact/index.php site/assets/css/site.css site/assets/js/site.js tests/test_site_validation.py
git diff --cached --check
git commit -m "feat: add appointment request form"
```

### Task 5: Validate enquiries and format safe messages

**Files:**
- Create: `composer.json`, `composer.lock`
- Modify: `.gitignore`
- Create: `site/api/src/ValidationResult.php`, `site/api/src/EnquiryValidator.php`, `site/api/src/EnquiryMessage.php`
- Create: `tests/php/bootstrap.php`, `tests/php/EnquiryValidatorTest.php`, `tests/php/EnquiryMessageTest.php`

**Interfaces:**
- Consumes: exact form fields from Task 4.
- Produces: `EnquiryValidator::validate(array $input): ValidationResult`; `ValidationResult::isValid(): bool`; `EnquiryMessage::from(array $data): EnquiryMessage` with readonly subject, text body, HTML body, reply-to email and reply-to name.

- [ ] **Step 1: Complete the approved runtime preflight**

Run: `php -v` and `composer --version`.

Expected current result: both commands are missing. Request approval and
install PHP 8.1+ and Composer 2. Use read-only cPanel inspection to verify the
staging domain's PHP version. Stop with the exact version if it is below 8.1.

- [ ] **Step 2: Add and lock the mail dependency**

```json
{
  "name": "stronger-at-home/website",
  "type": "project",
  "require": {
    "php": ">=8.1",
    "phpmailer/phpmailer": "7.1.1"
  },
  "autoload": {
    "psr-4": {"StrongerAtHome\\Enquiry\\": "site/api/src/"}
  },
  "config": {"sort-packages": true}
}
```

Run: `composer update --no-interaction`

Expected: `composer.lock` resolves PHPMailer exactly to 7.1.1. Add `/vendor/`
and `/config/site.php` to `.gitignore`; do not commit them.

- [ ] **Step 3: Write failing validator tests**

Create the shared runner first:

```php
<?php // tests/php/bootstrap.php
declare(strict_types=1);
require dirname(__DIR__, 2) . '/vendor/autoload.php';

function assert_true(bool $condition, string $label): void {
    if (!$condition) { fwrite(STDERR, "FAIL: {$label}\n"); exit(1); }
}
function assert_same(mixed $expected, mixed $actual, string $label): void {
    if ($expected !== $actual) {
        fwrite(STDERR, "FAIL: {$label}\nExpected: " . var_export($expected, true) . "\nActual: " . var_export($actual, true) . "\n");
        exit(1);
    }
}
```

```php
<?php
require __DIR__ . '/bootstrap.php';
use StrongerAtHome\Enquiry\EnquiryValidator;

$valid = [
    'name'=>'Alex Morgan', 'email'=>'alex@example.com', 'phone'=>'',
    'preferred_contact'=>'email', 'postcode'=>'KT17 4LZ',
    'message'=>'I would like to discuss a home assessment.',
    'privacy_acknowledged'=>'1',
];
$result = (new EnquiryValidator())->validate($valid);
assert_true($result->isValid(), 'valid enquiry is accepted');
assert_same('KT17 4LZ', $result->data['postcode'], 'postcode is normalised');

$missingEmail = $valid;
$missingEmail['email'] = '';
$result = (new EnquiryValidator())->validate($missingEmail);
assert_same('Please provide an email address.', $result->errors['email'], 'preferred email is required');

$tooLong = $valid;
$tooLong['message'] = str_repeat('x', 1001);
assert_true(isset((new EnquiryValidator())->validate($tooLong)->errors['message']), 'message is bounded');

$headerInjection = $valid;
$headerInjection['name'] = "Alex\r\nBcc: attacker@example.com";
assert_true(isset((new EnquiryValidator())->validate($headerInjection)->errors['name']), 'header controls are rejected');
```

- [ ] **Step 4: Run and verify the missing-class failure**

Run: `php tests/php/EnquiryValidatorTest.php`

Expected: FAIL because `EnquiryValidator` and `ValidationResult` do not exist.

- [ ] **Step 5: Implement normalisation and validation**

```php
<?php
namespace StrongerAtHome\Enquiry;

final readonly class ValidationResult
{
    public function __construct(public array $data, public array $errors) {}
    public function isValid(): bool { return $this->errors === []; }
}

final class EnquiryValidator
{
    public function validate(array $input): ValidationResult
    {
        $data = [
            'name' => trim((string)($input['name'] ?? '')),
            'email' => trim((string)($input['email'] ?? '')),
            'phone' => trim((string)($input['phone'] ?? '')),
            'preferred_contact' => (string)($input['preferred_contact'] ?? ''),
            'postcode' => strtoupper(preg_replace('/\s+/', ' ', trim((string)($input['postcode'] ?? '')))),
            'message' => trim((string)($input['message'] ?? '')),
            'privacy_acknowledged' => (string)($input['privacy_acknowledged'] ?? ''),
        ];
        $errors = [];
        if (strlen($data['name']) < 2 || strlen($data['name']) > 100 || preg_match('/[\r\n]/', $data['name'])) $errors['name'] = 'Please enter your name.';
        if (!in_array($data['preferred_contact'], ['email', 'phone'], true)) $errors['preferred_contact'] = 'Please choose email or phone.';
        if ($data['email'] !== '' && !filter_var($data['email'], FILTER_VALIDATE_EMAIL)) $errors['email'] = 'Please enter a valid email address.';
        if ($data['preferred_contact'] === 'email' && $data['email'] === '') $errors['email'] = 'Please provide an email address.';
        if ($data['phone'] !== '' && !preg_match('/^[+0-9() .-]{7,30}$/', $data['phone'])) $errors['phone'] = 'Please enter a valid phone number.';
        if ($data['preferred_contact'] === 'phone' && !preg_match('/^[+0-9() .-]{7,30}$/', $data['phone'])) $errors['phone'] = 'Please provide a phone number.';
        if (!preg_match('/^[A-Z0-9 ]{5,8}$/', $data['postcode'])) $errors['postcode'] = 'Please enter a UK postcode.';
        if (strlen($data['message']) < 10 || strlen($data['message']) > 1000) $errors['message'] = 'Please enter a short enquiry between 10 and 1000 characters.';
        if ($data['privacy_acknowledged'] !== '1') $errors['privacy_acknowledged'] = 'Please confirm that you have read the privacy notice.';
        return new ValidationResult($data, $errors);
    }
}
```

- [ ] **Step 6: Write failing safe-message tests**

```php
<?php
require __DIR__ . '/bootstrap.php';
use StrongerAtHome\Enquiry\EnquiryMessage;

$message = EnquiryMessage::from([
    'name'=>'Alex <script>alert(1)</script>', 'email'=>'alex@example.com',
    'phone'=>'07123 456789', 'preferred_contact'=>'email',
    'postcode'=>'KT17 4LZ', 'message'=>"Please call me.\nThank you.",
]);
assert_same('New website appointment request', $message->subject, 'subject has no personal data');
assert_true(!str_contains($message->htmlBody, '<script>'), 'HTML escapes input');
assert_true(str_contains($message->textBody, 'KT17 4LZ'), 'text body includes postcode');
assert_same('alex@example.com', $message->replyToEmail, 'valid email is reply-to');
```

- [ ] **Step 7: Verify failure, implement, and rerun both PHP tests**

Run: `php tests/php/EnquiryMessageTest.php`

Expected before implementation: FAIL because `EnquiryMessage` does not exist.

Implement the value with this construction pattern:

```php
<?php
namespace StrongerAtHome\Enquiry;

final readonly class EnquiryMessage
{
    public function __construct(
        public string $subject,
        public string $textBody,
        public string $htmlBody,
        public string $replyToEmail,
        public string $replyToName,
    ) {}

    public static function from(array $data): self
    {
        $labels = [
            'Name'=>$data['name'], 'Email'=>$data['email'], 'Phone'=>$data['phone'],
            'Preferred contact'=>$data['preferred_contact'],
            'Postcode'=>$data['postcode'], 'Enquiry'=>$data['message'],
        ];
        $text = implode("\n", array_map(
            static fn(string $label, string $value): string => $label . ': ' . $value,
            array_keys($labels), array_values($labels)
        ));
        $rows = implode('', array_map(
            static fn(string $label, string $value): string => '<tr><th scope="row">' . self::escape($label) . '</th><td>' . nl2br(self::escape($value)) . '</td></tr>',
            array_keys($labels), array_values($labels)
        ));
        return new self(
            'New website appointment request', $text,
            '<table>' . $rows . '</table>', $data['email'], $data['name']
        );
    }

    private static function escape(string $value): string
    {
        return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    }
}
```

Run: `php tests/php/EnquiryValidatorTest.php && php tests/php/EnquiryMessageTest.php`

Expected: both scripts exit 0.

- [ ] **Step 8: Commit the enquiry domain**

```bash
git add .gitignore composer.json composer.lock site/api/src tests/php
git diff --cached --check
git commit -m "feat: validate appointment enquiries"
```

### Task 6: Add rate limiting, SMTP and HTTP orchestration

**Files:**
- Create: `site/api/src/MailTransport.php`, `PhpMailerTransport.php`, `RateLimit.php`, `FileRateLimiter.php`, `Response.php`, `EnquiryController.php`
- Create: `site/api/enquiry.php`, `config/site.example.php`
- Create: `tests/php/FileRateLimiterTest.php`, `tests/php/EnquiryControllerTest.php`
- Modify: `site/contact/index.php`

**Interfaces:**
- Produces: `MailTransport::send(EnquiryMessage $message): void`; `RateLimit::allow(string $clientAddress, int $now): bool`; `EnquiryController::handle(array $server, array $post, array $session): Response`.

- [ ] **Step 1: Write failing rate-limit tests**

```php
<?php
require __DIR__ . '/bootstrap.php';
use StrongerAtHome\Enquiry\FileRateLimiter;

$directory = sys_get_temp_dir() . '/sah-rate-' . bin2hex(random_bytes(6));
$limiter = new FileRateLimiter($directory, 'test-hmac-key', 2, 3600);
assert_true($limiter->allow('192.0.2.10', 1000), 'first allowed');
assert_true($limiter->allow('192.0.2.10', 1001), 'second allowed');
assert_true(!$limiter->allow('192.0.2.10', 1002), 'third blocked');
assert_true($limiter->allow('192.0.2.10', 4601), 'expired window resets');
```

- [ ] **Step 2: Verify failure and implement the limiter**

Run: `php tests/php/FileRateLimiterTest.php`

Expected: FAIL because `FileRateLimiter` does not exist.

Implement the bounded counter:

```php
final class FileRateLimiter implements RateLimit
{
    public function __construct(
        private string $directory, private string $secret,
        private int $maximum, private int $windowSeconds
    ) {}

    public function allow(string $clientAddress, int $now): bool
    {
        if (!is_dir($this->directory)) mkdir($this->directory, 0700, true);
        $key = hash_hmac('sha256', $clientAddress, $this->secret);
        $handle = fopen($this->directory . '/' . $key . '.json', 'c+');
        if ($handle === false || !flock($handle, LOCK_EX)) return false;
        $raw = stream_get_contents($handle);
        $state = $raw ? json_decode($raw, true) : null;
        if (!is_array($state) || !isset($state['window_started'], $state['count']) || $now - (int)$state['window_started'] >= $this->windowSeconds) {
            $state = ['window_started'=>$now, 'count'=>0];
        }
        if ((int)$state['count'] >= $this->maximum) { flock($handle, LOCK_UN); fclose($handle); return false; }
        $state['count']++;
        rewind($handle); ftruncate($handle, 0); fwrite($handle, json_encode($state)); fflush($handle);
        flock($handle, LOCK_UN); fclose($handle);
        return true;
    }
}
```

Never store the raw address or enquiry content. Add a private cleanup method
that scans at most 20 counter files on one in every 100 allowed requests and
deletes only files older than twice the configured window.

- [ ] **Step 3: Write failing controller tests with an in-memory transport**

```php
<?php
require __DIR__ . '/bootstrap.php';
use StrongerAtHome\Enquiry\{EnquiryController, EnquiryMessage, EnquiryValidator, MailTransport, RateLimit};

final class FakeMailTransport implements MailTransport {
    public array $sent = [];
    public bool $fail = false;
    public function send(EnquiryMessage $message): void {
        if ($this->fail) throw new RuntimeException('simulated failure');
        $this->sent[] = $message;
    }
}

final class FakeRateLimit implements RateLimit {
    public function __construct(private bool $allowed) {}
    public function allow(string $clientAddress, int $now): bool { return $this->allowed; }
}

$server = ['REQUEST_METHOD'=>'POST','HTTP_ORIGIN'=>'https://staging.stronger-at-home.co.uk','REMOTE_ADDR'=>'192.0.2.10'];
$post = ['name'=>'Alex Morgan','email'=>'alex@example.com','phone'=>'','preferred_contact'=>'email','postcode'=>'KT17 4LZ','message'=>'Please contact me about an assessment.','privacy_acknowledged'=>'1','website'=>'','csrf_token'=>'known-token'];
$transport = new FakeMailTransport();
$controller = new EnquiryController(
    new EnquiryValidator(), $transport, new FakeRateLimit(true),
    'https://staging.stronger-at-home.co.uk'
);
$response = $controller->handle($server, $post, ['csrf_token'=>'known-token']);
assert_same(303, $response->status, 'success redirects');
assert_same('/contact/?sent=1', $response->headers['Location'], 'success target');
assert_same(1, count($transport->sent), 'one message sent');
```

Add cases for GET=405, disallowed origin=403, invalid CSRF=403, non-empty
honeypot=silent 303 with no send, invalid fields=303 to
`/contact/?error=validation`, rate limit=303 to `/contact/?error=rate` and mail
failure=303 to `/contact/?error=delivery`.

- [ ] **Step 4: Run and verify missing-controller failures**

Run: `php tests/php/EnquiryControllerTest.php`

Expected: FAIL because the controller interfaces do not exist.

- [ ] **Step 5: Implement controller values and authenticated transport**

```php
interface MailTransport { public function send(EnquiryMessage $message): void; }

interface RateLimit { public function allow(string $clientAddress, int $now): bool; }

final readonly class Response {
    public function __construct(
        public int $status,
        public array $headers = [],
        public array $flash = [],
    ) {}
}
```

`EnquiryController` accepts `EnquiryValidator`, `MailTransport`, `RateLimit`
and the allowed origin in its constructor and enforces the exact branches
tested in Step 3.

```php
final class EnquiryController
{
    public function __construct(
        private EnquiryValidator $validator,
        private MailTransport $transport,
        private RateLimit $rateLimit,
        private string $allowedOrigin,
    ) {}

    public function handle(array $server, array $post, array $session): Response
    {
    if (($server['REQUEST_METHOD'] ?? '') !== 'POST') return new Response(405, ['Allow'=>'POST']);
    if (!hash_equals($this->allowedOrigin, (string)($server['HTTP_ORIGIN'] ?? ''))) return new Response(403);
    if (trim((string)($post['website'] ?? '')) !== '') return new Response(303, ['Location'=>'/contact/?sent=1']);
    if (!hash_equals((string)($session['csrf_token'] ?? ''), (string)($post['csrf_token'] ?? ''))) return new Response(403);
    if (!$this->rateLimit->allow((string)($server['REMOTE_ADDR'] ?? ''), time())) {
        return new Response(303, ['Location'=>'/contact/?error=rate'], ['kind'=>'rate']);
    }
    $result = $this->validator->validate($post);
    $keys = array_flip(['name','email','phone','preferred_contact','postcode']);
    $safeValues = array_intersect_key($result->data, $keys);
    if (!$result->isValid()) {
        return new Response(303, ['Location'=>'/contact/?error=validation'], ['kind'=>'validation','errors'=>$result->errors,'values'=>$safeValues]);
    }
    try { $this->transport->send(EnquiryMessage::from($result->data)); }
    catch (\Throwable) { return new Response(303, ['Location'=>'/contact/?error=delivery'], ['kind'=>'delivery','values'=>$safeValues]); }
    return new Response(303, ['Location'=>'/contact/?sent=1'], ['kind'=>'success']);
    }
}
```

`PhpMailerTransport` uses deployment-configured authenticated TLS SMTP, a
sender on the Stronger at Home domain, recipient
`melanie@stronger-at-home.co.uk`, and validated reply-to only. Disable SMTP
debug output and convert provider errors to a generic delivery exception.

```php
final class PhpMailerTransport implements MailTransport
{
    public function __construct(private array $config) {}

    public function send(EnquiryMessage $message): void
    {
    $mailer = new \PHPMailer\PHPMailer\PHPMailer(true);
    $mailer->isSMTP();
    $mailer->Host = $this->config['smtp_host'];
    $mailer->SMTPAuth = true;
    $mailer->Username = $this->config['smtp_username'];
    $mailer->Password = $this->config['smtp_password'];
    $mailer->SMTPSecure = $this->config['smtp_encryption'];
    $mailer->Port = $this->config['smtp_port'];
    $mailer->CharSet = 'UTF-8';
    $mailer->SMTPDebug = 0;
    $mailer->setFrom($this->config['sender'], 'Stronger at Home Physiotherapy');
    $mailer->addAddress($this->config['recipient']);
    if ($message->replyToEmail !== '') $mailer->addReplyTo($message->replyToEmail, $message->replyToName);
    $mailer->Subject = $message->subject;
    $mailer->Body = $message->htmlBody;
    $mailer->AltBody = $message->textBody;
    $mailer->isHTML(true);
    $mailer->send();
    }
}
```

- [ ] **Step 6: Add the non-secret configuration contract and entry point**

```php
<?php
return [
    'environment'=>getenv('APP_ENV') ?: 'staging',
    'allowed_origin'=>getenv('ALLOWED_ORIGIN') ?: 'https://staging.stronger-at-home.co.uk',
    'recipient'=>getenv('ENQUIRY_RECIPIENT') ?: '',
    'sender'=>getenv('ENQUIRY_SENDER') ?: '',
    'smtp_host'=>getenv('SMTP_HOST') ?: '',
    'smtp_port'=>(int)(getenv('SMTP_PORT') ?: 587),
    'smtp_username'=>getenv('SMTP_USERNAME') ?: '',
    'smtp_password'=>getenv('SMTP_PASSWORD') ?: '',
    'smtp_encryption'=>getenv('SMTP_ENCRYPTION') ?: 'tls',
    'rate_limit_secret'=>getenv('RATE_LIMIT_SECRET') ?: '',
    'rate_limit_directory'=>getenv('RATE_LIMIT_DIRECTORY') ?: '',
];
```

The real external config must reject an empty sender, recipient, SMTP
credential, rate-limit secret or directory. `enquiry.php` starts a Secure, HttpOnly,
SameSite=Lax session; constructs dependencies; stores one-use safe flash data;
clears CSRF after an accepted POST; sends the tested response; and never logs
or echoes contact details or message content.

```php
<?php
declare(strict_types=1);
use StrongerAtHome\Enquiry\{EnquiryController, EnquiryValidator, FileRateLimiter, PhpMailerTransport};

require dirname(__DIR__, 2) . '/vendor/autoload.php';
$configPath = getenv('STRONGER_HOME_CONFIG') ?: dirname(__DIR__, 2) . '/config/site.php';
$config = require $configPath;
session_set_cookie_params(['secure'=>true, 'httponly'=>true, 'samesite'=>'Lax']);
session_start();
$controller = new EnquiryController(
    new EnquiryValidator(), new PhpMailerTransport($config),
    new FileRateLimiter($config['rate_limit_directory'], $config['rate_limit_secret'], 5, 3600),
    $config['allowed_origin'],
);
$response = $controller->handle($_SERVER, $_POST, $_SESSION);
if ($response->flash !== []) $_SESSION['form_flash'] = $response->flash;
unset($_SESSION['csrf_token']);
http_response_code($response->status);
foreach ($response->headers as $name => $value) header($name . ': ' . $value);
exit;
```

- [ ] **Step 7: Render one-use form state safely**

In `contact/index.php`, create a 32-byte random CSRF token when absent, read and
clear `form_flash`, and escape every displayed value. Preserve only name,
email, phone, preferred contact and postcode after failure; never the message.

- [ ] **Step 8: Run all PHP and Python tests**

Run: `composer install --no-interaction --prefer-dist`

Run: `for test_file in tests/php/*Test.php; do php "$test_file" || exit 1; done`

Run: `/opt/homebrew/bin/python3 -m unittest discover -s tests -q`

Expected: all commands exit 0.

- [ ] **Step 9: Commit the secure flow**

```bash
git add config/site.example.php site/api site/contact/index.php tests/php
git diff --cached --check
git commit -m "feat: deliver appointment enquiries securely"
```

### Task 7: Add supporting pages, metadata and release gates

**Files:**
- Create: `site/privacy/index.html`, `site/accessibility/index.html`, `site/404.html`, `site/robots.txt`, `site/robots-staging.txt`, `site/sitemap.xml`, `site/.htaccess`
- Create: `scripts/validate_site.py`
- Modify: `tests/test_site_validation.py` and all page footers/metadata

**Interfaces:**
- Consumes: complete public pages and production-blocker markers.
- Produces: `validate_site(root: Path, mode: str) -> list[str]`, where mode is `development`, `staging` or `production`.

- [ ] **Step 1: Write failing structure and release-gate tests**

```python
from scripts.validate_site import validate_site

def test_development_site_has_no_structural_errors(self):
    self.assertEqual(validate_site(ROOT, "development"), [])

def test_production_rejects_unresolved_publication_gates(self):
    errors = validate_site(ROOT, "production")
    self.assertIn("Production blocker remains: portrait", errors)
    self.assertIn("Production blocker remains: privacy-approval", errors)

def test_staging_is_not_indexable(self):
    text = (ROOT / "site/robots-staging.txt").read_text(encoding="utf-8")
    self.assertEqual(text, "User-agent: *\nDisallow: /\n")
```

- [ ] **Step 2: Run and verify the missing-validator failure**

Run: `/opt/homebrew/bin/python3 -m unittest tests.test_site_validation -v`

Expected: ERROR because `scripts.validate_site` and supporting files do not exist.

- [ ] **Step 3: Implement the supporting pages and crawl files**

The privacy draft identifies `Melanie Watsham trading as Stronger at Home
Physiotherapy`, lists the approved address and email, explains the enquiry
fields and purposes, states that the form is not for detailed or urgent
medical information, describes the strictly necessary session and rate-limit
data, and carries `data-production-blocker="privacy-approval"` until Melanie
approves its retention criteria.

The accessibility page states the WCAG 2.2 AA target and a route for reporting
problems without claiming perfect compliance. Use these crawl files:

```text
# site/robots.txt
User-agent: *
Allow: /
Sitemap: https://stronger-at-home.co.uk/sitemap.xml
```

```text
# site/robots-staging.txt
User-agent: *
Disallow: /
```

The sitemap contains the five primary pages plus `/privacy/` and
`/accessibility/` on the canonical production host.

Add page-specific Open Graph values and this approved-fact-only JSON-LD on the
homepage:

```html
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"LocalBusiness","name":"Stronger at Home Physiotherapy","url":"https://stronger-at-home.co.uk/","telephone":"+447843497871","email":"melanie@stronger-at-home.co.uk","address":{"@type":"PostalAddress","streetAddress":"11 Mospey Crescent","addressLocality":"Epsom","addressRegion":"Surrey","postalCode":"KT17 4LZ","addressCountry":"GB"},"areaServed":"Approximately 10 miles around Epsom, Surrey"}
</script>
```

- [ ] **Step 4: Add canonical redirects and security headers**

```apache
Options -Indexes
ErrorDocument 404 /404.html
RewriteEngine On
RewriteCond %{HTTPS} !=on
RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [R=301,L]
RewriteCond %{HTTP_HOST} ^www\.stronger-at-home\.co\.uk$ [NC]
RewriteRule ^ https://stronger-at-home.co.uk%{REQUEST_URI} [R=301,L]
Header always set X-Content-Type-Options "nosniff"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set Permissions-Policy "camera=(), microphone=(), geolocation=()"
Header always set Content-Security-Policy "default-src 'self'; img-src 'self'; style-src 'self'; script-src 'self'; form-action 'self'; base-uri 'self'; frame-ancestors 'none'"
```

The first rule uses each virtual host's configured `SERVER_NAME`, so staging
upgrades to HTTPS without redirecting to production. The second rule applies
only to the production `www` host.

- [ ] **Step 5: Implement the site validator**

`validate_site()` checks local links, one H1 per page, unique titles and
descriptions, canonical URLs, image dimensions/alt text, form labels, approved
contacts, prohibited claims, exact logo bytes, sitemap routes and staging
no-index. It also requires `og:title`, `og:description`, `og:url` and
`og:type=website` on every primary page, plus LocalBusiness JSON-LD containing
only the approved formal name, URL, phone, email, address and service area. In
production mode every `data-production-blocker` is an error. In
development/staging, allow only `portrait`, `privacy-approval`, `credentials`
and `referral-suitability` blockers.

- [ ] **Step 6: Run both validators and confirm the intentional production failure**

Run: `/opt/homebrew/bin/python3 -m unittest tests.test_site_validation -v`

Run: `/opt/homebrew/bin/python3 scripts/validate_site.py --mode development`

Run: `/opt/homebrew/bin/python3 scripts/validate_brand.py`

Run: `/opt/homebrew/bin/python3 scripts/validate_site.py --mode production`

Expected: tests, development validation and brand validation pass. Production
validation exits non-zero and names only the portrait and privacy-approval
blockers.

- [ ] **Step 7: Commit supporting pages and gates**

```bash
git add site scripts/validate_site.py tests/test_site_validation.py
git diff --cached --check
git commit -m "feat: add website release safeguards"
```

### Task 8: Package, review and prepare reversible staging deployment

**Files:**
- Create: `scripts/package_site.py`, `tests/test_site_package.py`
- Create: `docs/website-content-review.md`, `docs/website-staging-runbook.md`
- Modify: `BRAND.md`, `MEMORY.md`, `DECISIONS.md`

**Interfaces:**
- Consumes: validated `site/`, Composer production dependencies and external configuration.
- Produces: `package_site(project_root: Path, destination: Path, environment: str) -> Path`; a deterministic staging ZIP with `public/` as the document root and sibling `vendor/`, never secrets, tests or Git metadata.

- [ ] **Step 1: Write the failing package-boundary test**

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import unittest
from scripts.package_site import package_site

ROOT = Path(__file__).resolve().parents[1]

class SitePackageTests(unittest.TestCase):
    def test_staging_package_excludes_secrets_and_uses_noindex_robots(self):
        with TemporaryDirectory() as directory:
            archive = package_site(ROOT, Path(directory), "staging")
            with ZipFile(archive) as package:
                names = set(package.namelist())
                self.assertIn("public/robots.txt", names)
                self.assertIn("public/api/enquiry.php", names)
                self.assertNotIn("config/site.php", names)
                self.assertFalse(any(name.startswith("tests/") for name in names))
                self.assertEqual(package.read("public/robots.txt"), b"User-agent: *\nDisallow: /\n")
```

- [ ] **Step 2: Run and verify the missing-packager failure**

Run: `/opt/homebrew/bin/python3 -m unittest tests.test_site_package -v`

Expected: ERROR because `scripts.package_site` does not exist.

- [ ] **Step 3: Implement deterministic safe packaging**

Copy `site/` into a temporary tree at `public/`, replace `public/robots.txt`
with `robots-staging.txt` for staging, and place Composer production
dependencies in the sibling `vendor/` directory. This keeps the entry point's
`dirname(__DIR__, 2) . '/vendor/autoload.php'` path valid locally and after
deployment. Normalise ZIP timestamps and sort paths. Reject `.git`, `.env`,
`site.php`, `tests`, `__pycache__`, `.DS_Store` and all symlinks.

- [ ] **Step 4: Write the content-review checklist**

List every page, approved fact, omitted credential/referral area, portrait and
privacy gates, sole-trader identity, contact details and exact booking-success
meaning. Add unchecked boxes and separate sign-off lines for the project
sponsor and Melanie Watsham.

- [ ] **Step 5: Write the reversible staging runbook**

Require, in order: fresh Python/PHP tests; both development validators; cPanel
backup of the exact staging document root; confirmed target and PHP version;
external config with a test recipient; documented cPanel-only deployment;
no-index verification; mobile/desktop/keyboard/zoom/reduced-motion checks;
valid, invalid, spam, rate-limit and simulated-mail-failure tests; one
controlled end-to-end test to the safe staging recipient; and rollback on any
failed smoke check. State that the runbook does not authorise production.

- [ ] **Step 6: Run automated verification and build the staging archive**

Run: `composer install --no-dev --no-interaction --prefer-dist`

Run: `for test_file in tests/php/*Test.php; do php "$test_file" || exit 1; done`

Run: `/opt/homebrew/bin/python3 -m unittest discover -s tests -q`

Run: `/opt/homebrew/bin/python3 scripts/validate_site.py --mode development`

Run: `/opt/homebrew/bin/python3 scripts/validate_brand.py`

Run: `/opt/homebrew/bin/python3 scripts/package_site.py --environment staging --destination output/site-package`

Expected: all checks pass and one secret-free staging ZIP is created.

- [ ] **Step 7: Perform visual and accessibility review**

Serve the site locally with PHP and inspect it using browser control at
390×844, 768×1024 and 1440×1000. Capture all five primary pages. Verify
keyboard-only navigation, visible focus, menu disclosure, field errors, 200%
zoom/reflow, reduced motion, no horizontal overflow and no placeholder
presented as final. Record results in `docs/website-content-review.md`, fix
failures and rerun relevant checks.

- [ ] **Step 8: Commit the staging-ready workflow**

```bash
git add scripts/package_site.py tests/test_site_package.py docs/website-content-review.md docs/website-staging-runbook.md BRAND.md MEMORY.md DECISIONS.md
git diff --cached --check
git commit -m "docs: prepare website staging review"
```

- [ ] **Step 9: Stop for explicit staging-deployment approval**

Report the archive path and SHA-256, test counts, validator output, remaining
publication blockers, screenshots and exact cPanel staging document root. Ask
the user to approve or decline the external staging mutation. Do not deploy
merely because the plan or design was approved.

- [ ] **Step 10: Deploy to staging only after approval**

Use the cPanel integration's documented guarded workflow to back up the
staging document root, deploy the archive and external staging configuration,
then perform the runbook's HTTPS, no-index, navigation, asset,
security-header and form smoke tests. Do not change DNS, mailbox configuration
or the production document root.

Record only non-secret evidence:

```bash
git add docs/website-staging-runbook.md MEMORY.md
git diff --cached --check
git commit -m "docs: record website staging verification"
```

## Final verification before integration

Run fresh from the completed branch:

```bash
for test_file in tests/php/*Test.php; do php "$test_file" || exit 1; done
/opt/homebrew/bin/python3 -m unittest discover -s tests -q
/opt/homebrew/bin/python3 scripts/validate_site.py --mode development
/opt/homebrew/bin/python3 scripts/validate_brand.py
git diff --check
git status --short
```

Expected: all PHP and Python tests pass, both development validators pass, no
unexpected files are modified, and production remains blocked until the final
portrait and approved privacy wording replace their explicit gates.
