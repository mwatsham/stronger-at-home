# Feedback Manager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give Melanie a private feedback editor and visitors an accessible quote carousel, verified in an isolated local preview.

**Architecture:** Add a small PHP feedback subsystem alongside the existing enquiry code, with private environment-specific JSON persistence. Static home pages fetch published quotes; a server-rendered admin area manages drafts and publication.

**Tech Stack:** Existing PHP 8.3-compatible code, plain JavaScript, CSS, PHP test scripts and Python release tests; no new runtime dependency.

**Spec:** `docs/superpowers/specs/2026-11-10-feedback-manager-design.md`.

## Global Constraints

- Melanie is the sole administrator; no public registration or default live password.
- Eight-second autoplay; manual Previous/Next stops rotation until Play; hover/focus pause; reduced motion disables autoplay.
- Production and staging stay unchanged. No push, merge, hosting mutation or deployment.
- Store credentials and feedback outside the public root and deployment trees; separate local, staging and production configuration.
- Preserve enquiry code, PHP settings, staging protection, review links and existing content-removal checks.

## Review Focus

1. Concurrent edits must not lose another saved revision (task 1).
2. Missing/corrupt/unwritable storage must fail safely, never reset silently (task 1).
3. Forged actions, expired sessions and repeated failed logins must not publish content (task 2).
4. Draft/consent/private configuration must never appear in public JSON or archives (tasks 1 and 4).
5. Focus, reduced-motion changes and manual navigation must not unexpectedly restart rotation (task 3).

## Task 1: Private feedback model and public feed

**Files:** Create `site/feedback/lib/FeedbackStore.php`, `site/feedback/lib/bootstrap.php`, `site/feedback/feed.php`, `config/feedback.example.php`, `tests/php/FeedbackStoreTest.php`.

**Interfaces:** FeedbackStore constructor accepts an absolute private directory. `read(): array` returns revision and records; `save(array $records, int $expectedRevision): int` atomically validates and persists a new revision under an exclusive lock. `published(): array` returns only published quote text, attribution and order. Config is selected by `STRONGER_HOME_FEEDBACK_CONFIG`, outside the public root.

- [ ] Write failing tests for CRUD persistence, revision conflict, corrupt data, missing/unwritable storage, permission gating and published-only projection.
- [ ] Run `php tests/php/FeedbackStoreTest.php`; confirm failure before implementation.
- [ ] Implement bounded plain-text fields (quote 1–600 characters, attribution 1–100), generated IDs, explicit draft/published state, consent flag, deterministic order and 100-record limit. Reject malformed types, traversal and symlink storage.
- [ ] Implement feed GET-only JSON with no-store caching, no session creation, generic errors and no private fields.
- [ ] Run the store tests; confirm all pass. Commit this task only.

## Task 2: Melanie-only administration

**Files:** Create `site/feedback/lib/FeedbackAuth.php`, `site/feedback/admin/index.php`, `site/assets/css/feedback-admin.css`, `scripts/setup_feedback.php`, `tests/php/FeedbackAuthTest.php`, `tests/test_feedback_http.py`.

**Interfaces:** Auth consumes private config containing username fixed to `melanie`, password hash, allowed origin and private storage directory. Exposes `login(string $username, string $password): bool`, `requireAuthenticated(): void`, `csrfToken(): string`, `verifyCsrf(string $token): bool` and `logout(): void`. Admin consumes task 1 store.

- [ ] Write failing tests for wrong users/passwords, CSRF, session rotation, logout, idle expiry (30 minutes), absolute expiry (8 hours), throttling (5 failures per 15 minutes), and unauthenticated mutations.
- [ ] Run PHP authentication tests and HTTP integration tests to establish failures.
- [ ] Implement secure isolated sessions, generic authentication errors, persistent bounded throttling, CSRF on every POST including login/logout, no-store/noindex headers and POST/redirect/GET.
- [ ] Implement add/edit/list/preview/order, publish with consent confirmation, unpublish and confirmed delete. Draft edited published quotes; use revision checks; escape every rendered value.
- [ ] Implement CLI-only password setup using hidden interactive input or protected stdin; never print/store plaintext passwords or commit private config. Document operator-only password recovery.
- [ ] Run HTTP tests for each action, XSS payloads, malformed input, stale revisions and failed storage. Confirm pass, then commit.

## Task 3: Accessible public carousel

**Files:** Create `site/assets/js/feedback-carousel.js`, `site/assets/css/feedback-carousel.css`, `tests/js/feedback-carousel.test.js`; modify `site/index.html` and `design-previews/seamless-photo/index.html`.

**Interfaces:** Fetch `/feedback/feed.php`; accept published records with text, attribution and order. Use textContent, not innerHTML. Keep state for user pause, manual stop, focus, hover, document visibility and reduced motion.

- [ ] Write failing timer/state tests: eight-second rotation, wraparound, Previous/Next stops, Play restarts, Pause stops, hover/focus pauses, hidden tab pauses, reduced motion disables, zero/one quote states.
- [ ] Run `node --test tests/js/feedback-carousel.test.js`; confirm failures.
- [ ] Implement clearly labelled direct-feedback section beside existing review links, large buttons, quote count, accessible labels and polite announcements only for manual changes. Avoid repeated autoplay screen-reader announcements.
- [ ] Integrate in both homepage sources so approved-image packaging preserves it. Keep review links when feed unavailable.
- [ ] Run JS tests and syntax checks; commit.

## Task 4: Packaging, local preview and verification

**Files:** Modify `scripts/validate_site.py`, applicable packaging tests and `tests/test_staging_design_preview.py`; create `scripts/preview_feedback.py`, `tests/test_feedback_preview.py`, `docs/feedback-manager-operations.md`.

**Interfaces:** Local runner binds only `127.0.0.1`, creates temporary private config/storage, uses a preview-only password chosen through protected input, and serves the approved imagery composition plus PHP endpoints. No credentials or runtime records enter Git or release archives.

- [ ] Write failing tests for public-source inventory, private-file exclusion, environment separation and data surviving two simulated releases.
- [ ] Update the explicit source allowlist/hashes without broadening file discovery. Package only code, never local content/config/session files.
- [ ] Implement isolated local runner with explicit loopback HTTP exception; use clearly labelled fictional sample quotes and a visible local-preview marker.
- [ ] Run all PHP tests, `python -m unittest discover -s tests -q`, JS tests, all three site validation modes, brand validation, release-package tests and `git diff --check`.
- [ ] Start local preview; verify login and editing workflow, published versus draft visibility, refresh after publish, keyboard navigation, mobile layout, pause/manual-stop and reduced motion in the browser.
- [ ] Obtain whole-branch review and fix important findings. Record test evidence and local URLs; leave both live sites unchanged.
