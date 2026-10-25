# Pending-registration Enquiries Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore enquiries while accurately recording pending registration and owner approval.

**Architecture:** Extend the release configuration validator with an explicit exception record; preserve the existing form and transport. Propagate the actual registration status to release metadata and configure production privately before activation.

**Tech Stack:** Python release builder, PHP enquiry service, GitHub Actions, guarded cPanel CLI.

**Spec:** docs/superpowers/specs/2026-10-24-pending-registration-enquiries-design.md

## Global Constraints

- ICO status remains pending; exception identifier is owner-pending-registration-2026-10-24.
- Production sole recipient is melanie@stronger-at-home.co.uk; staging remains webadmin.
- Retain PHP 8.3.36 and all existing security checks.
- Use synthetic test data only; no secrets in Git, chat or public files.

## Review Focus

- Missing, misspelled or duplicate exception fields must fail before writing an artifact.
- CLI-generated metadata must retain pending status rather than omit or mislabel it.
- Restored builds must include the real form, privacy wording and private config bindings.
- Informational fallback must still produce a session-free 503 endpoint.
- Missing production private configuration must prevent activation.

## Task 1: Auditable exception and release selection

Files: scripts/build_git_release.py, config/publication-mode.json,
tests/test_informational_release.py, docs/website-production-runbook.md,
docs/website-content-review.md.

- [ ] Add failing tests for explicit pending exception acceptance and metadata propagation; reject absent/unknown/duplicate exception values.
- [ ] Run focused tests and verify the expected failure.
- [ ] Extend strict configuration validation and metadata propagation without weakening other combinations or bypassing private-config requirements.
- [ ] Select enquiries/pending with the approved exception in tracked configuration; update runbook and review notes without checking ICO completion.
- [ ] Test restored form, privacy copy, config bindings, disabled fallback and missing-config guard; run the entire Python/PHP/validation suite.
- [ ] Review the diff and commit only task-owned files on an isolated feature branch.

## Task 2: Staging and production readiness

- [ ] Review and merge via the existing PR/check process, build staging and verify provenance.
- [ ] Present exact cPanel plans for staging checkout and activation; execute only after required approvals.
- [ ] Verify staging security behavior and synthetic email receipt; obtain staging acceptance.
- [ ] Prepare protected production configuration with a fresh secret and verify non-secret settings without displaying secrets.
- [ ] Present separate cPanel directory/file mutation plans for approval, execute and verify ownership/permissions.
- [ ] Promote accepted source through main and build production; request exact-release owner-only authorisation and activation approval.
- [ ] Activate, verify public routes/security and labelled synthetic delivery, then record results and remaining ICO obligation.
