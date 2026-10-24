# Warm Editorial Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refine hierarchy, spacing and appointment navigation without changing the approved identity or enquiry backend.
**Architecture:** Existing shared CSS and static HTML/PHP, with a narrowly scoped JS selector adjustment if needed. One integrated task keeps coupled layout and regression tests together.
**Tech Stack:** HTML, CSS, vanilla JS, PHP, Python unittest and Playwright.
**Spec:** docs/superpowers/specs/2026-10-24-warm-editorial-design.md

## Global Constraints
- Preserve exact raster logo, portrait, palette, typefaces and verified service copy.
- Preserve form fields, validation, CSRF, privacy wording and submission behaviour; no real submissions.
- No dependencies, framework rebuild, new images or font assets.
- Local implementation only; no merge, push or deployment.
- Preserve unrelated staged AGENTS.md and untracked user files; sources/ is read-only.

## Review Focus
- Anchor links retain visible heading context and JS still targets the actual form.
- Narrow screens and tablet navigation avoid overflow with 44px controls.
- Keyboard focus and no-JS navigation remain usable.
- 200% zoom allows content reflow without clipping.
- Approval-hash changes are limited to deliberately changed public files, not assets or backend.

### Task 1: Editorial layout and appointment journey
**Files:** Modify site/assets/css/site.css, site/contact/index.php, site/assets/js/site.js if needed; existing information HTML only for necessary presentation consistency. Add tests/editorial_layout.cjs and focused tests in tests/test_site_validation.py or a separate tests/test_editorial_layout.py. Update the existing approval manifest only for intentional public changes.
**Interfaces:** Consume current .site-identity, .hero, .page-intro, .contact-form-section and form markup; preserve public /contact/#appointment-request URL and enquiry POST contract.
- [x] Run baseline Python suite and PHP suite using repository test instructions.
- [x] Add failing regression assertions: fragment target contains heading and actual form, JS resolves actual form, and responsive hero CTA/reassurance fit at 1280×720; no overflow at 320/375/768/1024/1280.
- [x] Run focused tests and record expected failures.
- [x] Tighten header/hero spacing, refine inner headings and section rhythm, centre contact shell and move fragment target to enclosing section with appropriate scroll margin. Keep readable type and prominent logo.
- [x] Run targeted regression tests including keyboard/no-JS/200% reflow and verify desktop/mobile screenshots.
- [x] Update intentional approval hashes and run full Python/PHP suites plus existing header tests.
- [x] Self-review diff and commit only task-owned files. Report commands, results and screenshot paths.
