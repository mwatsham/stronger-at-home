# Older-client accessibility implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Implement the first four recommended accessibility improvements locally, preserving privacy and the existing brand.

**Architecture:** Adapt the existing PHP-rendered contact form and shared CSS/JavaScript. Reuse current navigation, contact methods and validation; no new dependencies.

**Tech Stack:** HTML, CSS, JavaScript, PHP, Python unittest.

**Spec:** The user's approval to proceed with audit recommendations 1–4, recorded below.

## Proposed design and constraints

- Show “Call Melanie: 07843 497871” on existing call links and immediately above the enquiry form. Keep tel:+447843497871 destinations.
- Set body text to 1.125rem (normally 18px) and form guidance to at least 1rem. Retain relative sizing and current line spacing.
- Limit long biography/service prose to approximately 65 characters per line without constraining card grids or disrupting the portrait. Introduce “Help with breathing” alongside the respiratory service title; preserve approved clinical meaning.
- Move preferred contact method before email and phone fields. Keep both fields visible, explicitly explain which is needed, and synchronise required status and visible labels with the selected method. Keep server validation authoritative, including when JavaScript is unavailable.
- Keep existing email preference as the default, but expose it before requesting contact details. No automatic inference from partially entered details.
- Retain current handling of enquiry messages, sessions, security, recipients and PHP settings. Do not submit test enquiries or modify live/staging websites.
- Preserve the pending respiratory changes and all unrelated work.
- Refresh shared asset URL versions and approved source hashes so a later deployment will not serve stale styles/scripts.

## Approaches

Use small changes to existing components, rather than a redesign or new accessibility toolbar. This addresses the approved issues with fewer new controls and no additional dependencies. A persistent floating call button is deferred because it can obscure content at high zoom; existing call links plus a form-adjacent alternative are sufficient for this pass.

## Review focus

1. Switching email to phone and back updates required state without clearing entered values.
2. Server-rendered errors and contact preference remain understandable with JavaScript disabled.
3. Longer telephone labels do not overflow narrow screens.
4. Larger text and 400% zoom do not obscure navigation, portrait or form controls.
5. Privacy/error handling and enquiry recipients remain unchanged.

## Task 1: Contact accessibility

**Files:** site/contact/index.php, site/assets/js/site.js, existing telephone links in public HTML pages; relevant Python/PHP tests and a focused JavaScript behavior test.

**Interfaces:** Existing preferred-contact, email and phone IDs and preferred_contact POST field remain unchanged.

- [ ] Add failing tests for preference-before-contact-field order, phone alternative within the appointment target, and required-state switching without value loss.
- [ ] Run focused tests and verify they fail for the missing behavior.
- [ ] Update call-link display text and form ordering/guidance. Synchronise required labels and field constraints while preserving server validation and no-JavaScript usability.
- [ ] Run focused tests; expected all pass. Inspect local PHP-rendered contact form without sending enquiries.

## Task 2: Readability and verification

**Files:** site/assets/css/site.css, site/about/index.html, site/how-i-can-help/index.html, shared asset references in public pages, scripts/validate_site.py, applicable existing test expectations.

**Interfaces:** Use existing design tokens and responsive breakpoints; preserve all routes and respiratory section ID.

- [ ] Apply approved relative font sizes and scoped prose widths; retain responsive portrait and service cards.
- [ ] Add “Help with breathing” without new medical claims.
- [ ] Version modified shared assets and update only affected approved hashes.
- [ ] Run full Python suite, then PHP suite sequentially; development/staging site validation, brand validation, JavaScript syntax and diff checks. Expected: all pass.
- [ ] Inspect homepage, services, About and PHP-rendered contact locally at desktop and 320px widths, plus keyboard operation and zoom where tooling supports it. Record any untested conditions.
- [ ] Obtain independent final review, resolve important issues, and leave a local preview open. No push, merge or deployment.

## Approval status

Approved for implementation and testing on 7 November 2026. Implemented locally; no push or deployment.

## Verification record

- New contact ordering and requirement-switching tests failed before implementation and passed afterwards.
- 207 Python tests passed before final narrow-screen correction; final rerun recorded in the execution ledger.
- PHP tests, site validation in development/staging modes, brand validation, JavaScript syntax and whitespace checks passed.
- Local browser checks: home, About, services and contact at 320px viewport; all have scroll width equal to available client width (305px with scrollbar) after removing the old body minimum width.
- Desktop portrait/text layout checked at 1280px. Mobile menu opened using Enter. Phone selection changed the accessible required/optional labels correctly.
- Local preview blocks enquiry submissions and API execution. No emails sent.
- Limits: no full screen-reader audit, actual 400% browser-zoom test or end-to-end enquiry submission. 320px reflow was tested directly.
- Independent review: no important defects. Deferred minor test coverage: blank-field validity and initial server-error preservation are not covered by the new JavaScript DOM stub; existing server tests remain intact.
