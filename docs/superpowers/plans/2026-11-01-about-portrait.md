# About Portrait Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the approved right-floated portrait to About Melanie.

**Architecture:** Reuse the existing image and portrait-frame styling. Place the figure inside an About-only flow-root biography container, with a scoped right float and a mobile reset.

**Tech Stack:** Existing static HTML, CSS and Python unittest validation.

**Spec:** docs/superpowers/specs/2026-11-01-about-portrait-design.md

## Global Constraints
- Preserve biography wording, homepage, enquiries and PHP.
- Use the existing approved JPEG without alterations or dependencies.
- Mobile breakpoint: 760px; no deployment in this task.
- Reuse the clean existing worktree on a new codex/ branch based on current main; preserve unrelated root edits.

## Review Focus
- At 320px and 390px, portrait and text fit without overflow.
- At 760px and 761px, stacking changes cleanly without cramped text.
- At 1280px, text wraps beside and below the portrait.
- Subsequent sections do not overlap the float.
- The homepage portrait and approved wording remain unchanged.

## Task 1: Implement and verify the approved layout

**Files:** site/about/index.html; site/assets/css/site.css; scripts/validate_site.py; tests/test_site_validation.py.

**Interfaces:** Reuse /assets/images/melanie-watsham-portrait.jpg, .portrait-frame and existing page parser. Introduce .about-biography as a contained float wrapper.

- [ ] Add failing tests asserting the About portrait source, alt text, dimensions and placement after the h1 and before biography text; assert scoped float containment and mobile reset.
- [ ] Run the focused test file and confirm failures are due to the missing layout.
- [ ] Add the figure and wrapper without changing paragraph text. Use float:right, width:32%, max-width:20rem and margin:0.25rem 0 1.5rem 2rem. At max-width:760px use float:none, width:100%, max-width:19rem and margin:0 auto 1.5rem. Retain frame styling.
- [ ] Update the approved About HTML hash in scripts/validate_site.py after reviewing the exact diff.
- [ ] Run the complete Python suite, PHP tests, development and staging site validators, brand validator and git diff --check. All must pass.
- [ ] Inspect the actual local page at the five review widths; verify wrapping, image loading, overflow and section clearance. Compare homepage source and biography text to the base version.
- [ ] Present the tested local change for review; do not push, merge or deploy without authorisation.
