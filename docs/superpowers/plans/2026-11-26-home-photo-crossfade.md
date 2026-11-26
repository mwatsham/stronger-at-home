# Home Photo Crossfade Implementation Plan

**Owner revision after preview:** automatic-only presentation. Remove Previous, Next, Pause/Play and counter markup. Keep reduced-motion, hover, hidden-page and off-screen safeguards. Original control-related steps/results below describe the first reviewed version, superseded by this revision. Controller supports optional controls but this website renders none.

Revised local preview: http://127.0.0.1:58645/#benefits-at-home. Zero buttons/counter and automatic photo advancement verified in the browser; 36 JavaScript tests pass.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provide the approved accessible home-visit photo crossfade and a tested local preview, without changing either live site.

**Architecture:** Enhance the existing approved homepage composition with a standalone photo controller and progressive-enhancement markup. Keep the first photo visible without JavaScript; use opacity transitions within a fixed frame and retain the existing seamless overlay. Do not couple the photo component to the feedback feed or its carousel.

**Tech Stack:** Existing HTML, CSS, first-party JavaScript, Node test runner and Python unittest packaging tests.

**Spec:** `docs/superpowers/specs/2026-11-26-home-photo-crossfade-design.md`

## Global Constraints

- Use existing approved seated-treatment, standing-balance and home-exercise photographs, starting with seated treatment; do not generate or alter images.
- Approximately eight seconds per photograph and a one-second crossfade; stable responsive frame and seamless edges.
- Previous, Next and Pause/Play controls; manual navigation stops autoplay until Play is selected.
- Pause on hover, focus, hidden page and off-screen component. Reduced motion disables autoplay and transitions.
- No automatic live-region announcements; expose only active-image alternative text.
- Image failure cannot replace a working photograph with a blank frame; static fallback hides inactive controls.
- Preserve unrelated external-link edits, feedback data, analytics settings, enquiries, PHP and both live sites. Do not push, merge or deploy.

## Review Focus

- Overlapping focus/hover/visibility blockers must not resume rotation prematurely (Task 1).
- A delayed image load must not undo a newer manual navigation or resume a paused timer (Task 1).
- Failed images must leave the current photo visible and allow other working photos (Task 1).
- Reduced motion changing during playback must immediately stop scheduling and animation (Tasks 1 and 2).
- Packaging must resolve assets on both the main and design-preview routes without weakening authentication or changing analytics (Task 2).

### Task 1: Tested photo rotation controller

**Files:** Create `site/assets/js/photo-carousel.js`, `tests/js/photo-carousel.test.js` and `tests/test_photo_carousel.py`.

**Interfaces:** Export `PhotoCarousel` for Node tests. Constructor consumes count and injected render, scheduling and cancellation functions; methods `move(direction)`, `play()`, `pause()` and `block(reason, active)` control rotation. Browser initializer consumes `[data-photo-carousel]`, image elements and explicitly named controls. Keep loading/decoding verification and stale-request protection in the browser adapter.

- [ ] Write failing Node tests for 8000ms advancement, wrapping, manual stop, explicit play, zero/one-image behaviour and overlapping blockers. Add browser-adapter tests for delayed/failed loading, reduced-motion changes, visibility, off-screen pause and exposed active alt text; execute these through the Python test wrapper as well.
- [ ] Run `node --test tests/js/photo-carousel.test.js`; confirm failure because the controller is absent.
- [ ] Implement controller and browser initialization. Decode the incoming image before changing active state, reject stale async completions, preserve the visible photo on failure, and keep automatic changes silent. Use native buttons and fresh eight-second intervals after temporary blockers clear.
- [ ] Run the Node tests and `python -m unittest tests.test_photo_carousel -v`; require all tests to pass.

### Task 2: Composition, styling and packaging

**Files:** Modify `design-previews/seamless-photo/index.html`, `design-previews/seamless-photo/assets/css/photo-fades.css`, `scripts/validate_site.py`, `tests/test_staging_design_preview.py` and `tests/test_site_package.py`.

**Interfaces:** Reference the shared `/assets/js/photo-carousel.js` with `defer`; image paths remain under `/design-preview/assets/` so the existing release builder rewrites them for the main page. Store controller code outside the preview directory; do not expand its accepted file extensions.

- [ ] Add failing packaging tests for the three slides, static fallback, hidden controls, script availability and resolvable image paths in generated main/preview pages. Assert staging protection, enquiry handlers and disabled analytics remain unchanged.
- [ ] Run `python -m unittest tests.test_staging_design_preview -v`; confirm the added assertions fail.
- [ ] Add approved slide markup and controls. Keep overlay on the image frame rather than over controls; use a stable 4:5 frame, contain images to avoid clipping subjects, one-second opacity transitions, minimum 44px control targets and visible keyboard focus. Override transitions for reduced motion. Expose only the initial image until successful enhancement.
- [ ] Update the public-source allowlist/hash for the new JavaScript only and adjust package totals from 126/42 to 127/43. Preserve all unrelated pending hashes and edits.
- [ ] Run `python -m unittest tests.test_staging_design_preview tests.test_site_package tests.test_photo_carousel -v` and `node --test tests/js/*.test.js`; require all tests to pass.

### Task 3: Local preview and final verification

**Files:** Local temporary generated release only; update this plan with verification results.

- [ ] Generate an isolated local package using the existing builder and approved-image inclusion function. Never symlink dependencies into a test fixture or invoke deployment tools. Serve its public folder on loopback only.
- [ ] Inspect desktop and narrow layouts, keyboard controls, at least one timed crossfade, manual stop/resume, reduced-motion behaviour and lack of layout movement. Inspect all three subjects for poor framing. Confirm no analytics provider request or form submission is made.
- [ ] Run the full existing Python suite, all JavaScript tests and applicable validators. Review the diff for accidental unrelated changes. If required by the execution workflow, request one independent final review and resolve findings before claiming completion.
- [ ] Open the local homepage at `#benefits-at-home` and report the verified results and any limitations. Leave changes local and both live sites untouched.

## Execution results — 26 November 2026

Tasks 1–3 implemented and verified locally. Initial controller tests failed before implementation; packaging test failed with zero slides before the composition was added. Independent review identified two slow-image interaction defects; both were reproduced with failing tests and fixed in one pass.

- Final Python regression suite: 241 tests passed using the pinned Pillow 12.3.0 environment.
- JavaScript suite: 35 tests passed, including 14 photo-controller/browser-adapter tests.
- Development, staging and brand validators passed; git diff whitespace check passed.
- Browser verification: automatic advancement, manual stop, keyboard Previous, one-second computed transition, stable 478.734px × 598.406px desktop frame, and narrow layout without horizontal overflow. Controls measured at least 44px in both dimensions.
- Reduced-motion preferences and changing preferences verified through controller/browser-adapter tests and the CSS media rule; no claim of physical screen-reader or OS-level reduced-motion testing.
- Final local preview: http://127.0.0.1:58644/#benefits-at-home
- Local generated package: /private/tmp/sah-photo-preview-20261126/final/public. Its source marker identifies the base checkout, not a committed/deployable revision of these uncommitted changes.
- No push, merge, deployment, enquiry submission, PHP change or analytics activation. Both live sites left unchanged.

Implementation decisions: retain uncommitted work and task records for owner review; test image preparation through an injectable asynchronous boundary while performing actual decode in the browser; prioritise explicit manual navigation over temporary autoplay blockers. Existing unrelated external-link edits were preserved, not included as new work. No review findings deferred.
