# GoatCounter Analytics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare disabled, privacy-minimised traffic-source and accepted-enquiry tracking with offline tests.

**Architecture:** A focused local JavaScript adapter owns eligibility, sanitisation, manual provider loading and counting. Public pages reference the adapter, which exits before network activity while disabled. The existing one-use PHP success flash supplies the conversion signal without changing enquiry delivery.

**Tech Stack:** Vanilla JavaScript, Node test runner, existing PHP enquiry flow and Python site validation.

**Spec:** `docs/superpowers/specs/2026-11-26-goatcounter-analytics-design.md`

## Global Constraints

- Tracking disabled by default; no GoatCounter requests in tests or previews.
- Both live sites, PHP, private data and remote account settings remain unchanged.
- No pushes, deployments or real enquiry submissions.
- Preserve pending external-link edits; do not modify synced `sources/`.
- Production eligibility requires exact hostname `stronger-at-home.co.uk` and HTTPS.

## Review Focus

1. Provider defaults reintroducing arbitrary campaign/query values despite sanitised paths: inspect actual outbound payload construction and test poison inputs.
2. Forged success URLs or honeypot redirects: test that only server flash success counts.
3. Delayed script completion and repeated initialisation: prove one event maximum and no form interruption.
4. Lookalike hosts, private routes and framed pages: prove zero provider loading.
5. Provider errors, blocked scripts and browser-back restoration: no retries that duplicate conversions or interfere with enquiries.

### Task 1: Disabled analytics adapter

**Files:** Create `site/assets/js/analytics.js`, `tests/js/analytics.test.js`.

**Interfaces:** Export `buildPageview(location, referrer)` returning a safe payload or null, and `startAnalytics(window, document, enabled)` returning without action when disabled or ineligible. Browser entry passes literal `false`. Payloads contain static `path`, `title`, sanitised `referrer` and boolean `event` only; provider-specific extra fields must be explicitly audited.

- [ ] Write Node tests for default-off zero script insertion, HTTPS/exact-host gating, public route allowlist, private/unknown/frame exclusion, query/fragment removal and unsafe referrer rejection. Cover exact campaign pairs from the spec and reject all other values. A poisoned URL containing patient-like names and email addresses must contribute no such strings to any recorded request.
- [ ] Run `node --test tests/js/analytics.test.js`. Expected: failure because the adapter does not exist.
- [ ] Inspect the official provider script's payload construction read-only. Implement manual loading with `no_onload` and `no_events`, explicitly safe data and non-blocking error handling. Avoid raw automatic campaign extraction. Allow only `/`, `/about/`, `/how-i-can-help/`, `/appointments-and-fees/`, `/contact/`, `/privacy/`, `/accessibility/`; static titles match those page purposes.
- [ ] Add success-event tests using a fake `data-form-status` element: only `data-flash-kind=success` on `/contact/` counts; failures, missing markers and `?sent=1` do not. Repeated initialisation, delayed callbacks and restore events cannot duplicate it. Watch new tests fail before adding conversion logic.
- [ ] Run `node --test tests/js/analytics.test.js`. Expected: all pass without network activity. Inspect the diff for field reads or storage not authorised by the spec.

### Task 2: Integrate disabled public-page references and verify

**Files:** Modify the seven public page files identified by Task 1, `scripts/validate_site.py`; create `tests/test_analytics_integration.py` and `docs/analytics-goatcounter-activation.md`.

**Interfaces:** Uses the browser entry from Task 1; no changes to `EnquiryController` success semantics or mail transport. The integration test verifies the actual checked-in default is false, not merely a mocked setting.

- [ ] Add failing integration tests: each eligible page references the local adapter once; admin, API and design previews do not; no direct provider script/pixel/preconnect exists; CSP remains unchanged. Assert conversion still depends on the consumed server flash and honeypot response has no success flash. Run `python -m unittest discover -s tests -p 'test_analytics_integration.py' -v`; expected new assertions fail before integration.
- [ ] Add deferred local adapter references, update only affected validator hashes and approved local-file entries. Do not add remote CSP permissions or activation settings. Retain existing external-link changes.
- [ ] Write activation checklist: explicit owner approval, private dashboard recheck, retention and reduced collection decisions, privacy notice review, narrow CSP/provider allowlist changes, staged offline verification and explicitly approved production smoke test. Include limitations of source labels and conversion attribution, rollback by disabling the adapter, and draft privacy wording marked inactive.
- [ ] Run `node --test tests/js/*.test.js`; expected all pass. Run every `tests/php/*Test.php` with the local test fixtures; expected all pass without SMTP delivery.
- [ ] Run full Python suite using pinned Pillow: `PYTHONPATH=/private/tmp/sah-credentials-test-deps /opt/anaconda3/bin/python -m unittest discover -s tests -q`; expected all pass. Run site validation in development and staging modes, brand validation and `git diff --check`; expected all pass.
- [ ] Inspect local preview with provider requests blocked, then verify actual disabled mode has zero GoatCounter requests. Do not submit an enquiry or navigate authenticated live sites for this test.
- [ ] Request one independent final review of the analytics diff and privacy boundaries; fix important findings with failing-then-passing tests. Leave changes local and uncommitted for user review; no automatic release step.

## Plan self-review

Spec requirements map to the two tasks; all five review risks have explicit tests or payload inspection. Activation and account changes are deliberately excluded. Local tests establish sanitisation and event gating, not real dashboard receipt or email delivery. Existing feature work remains intact.

## Execution outcome — 26 November 2026

Both tasks implemented locally; leaflet QR triple included following owner approval. Final verification: 238 Python tests, 21 JavaScript tests, all PHP scripts and site/brand validators passed. Independent review fixes covered by RED→GREEN tests. Browser check confirmed local adapter with no inserted provider elements; browser request interception was not available, so no-network evidence uses offline transport tests. One minor deferred case is the provider image fallback; it is listed for pre-activation testing. Existing packaging assertions updated for the single added public file. No commits, pushes, live changes or activation. See docs/analytics-goatcounter-activation.md for the release gates and measurement limitations.
