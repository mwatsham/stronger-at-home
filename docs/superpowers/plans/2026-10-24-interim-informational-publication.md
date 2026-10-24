# Interim Informational Publication Implementation Plan

Execution status: implementation and local verification completed 24 October
2026; see `docs/interim-release-verification.md` for exact evidence, review findings
and deviations. No merge, push or deployment. The procedural checkboxes below are
the original plan; the verification record is authoritative for executed coverage.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and test a Git-managed informational release with website enquiries disabled; do not publish during this task.

**Architecture:** Keep approved enquiry-enabled source unchanged. Add a deterministic release transformation selected by a tracked release-mode configuration. Informational artifacts contain a static contact page and an inert PHP endpoint, not the operational enquiry handler. Generate mode-specific deployment preconditions and metadata.

**Tech Stack:** Python release builder and unittest; PHP endpoint and local HTTP tests; existing HTML/CSS/JavaScript; GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-24-interim-informational-publication-design.md` (approved by owner in chat).

## Global Constraints

- ICO application remains pending; do not claim legal compliance.
- Keep existing phone/email links, approved identity, service information and review links.
- No DNS, mailbox, account-wide PHP, live form submissions or deployments.
- Preserve unrelated working-tree changes and read-only `sources/`.
- Enquiry reactivation requires a separate approved Git change, not a date or environment fallback.
- Retain all existing validation and rollback protections for enquiry-enabled releases.

## Review Focus

- Direct POST/GET requests must not start a session, load mail/configuration or echo request content.
- Informational contact HTML and privacy copy must not promise an available form.
- Missing or invalid tracked mode must fail closed in release automation.
- Informational deployment without private enquiry configuration must succeed; enabled deployment without it must still fail before mutation.
- Existing deep links, staging noindex controls, production canonical rules and rollback behavior must remain intact.

## Task 1: Deterministic informational artifact and regression coverage

**Files:** Create `scripts/informational_release.py`, `tests/test_informational_release.py`; modify `scripts/build_git_release.py`.

**Interfaces:** `prepare_informational_public_tree(public_root: Path) -> None` transforms an extracted, already source-validated release. Extend `build_git_release(..., publication_mode: str = "enquiries") -> Path` and `deployment_script(environment, source_sha, publication_mode="enquiries") -> str`. Accept only `enquiries` and `informational`; preserve existing callers and enabled output behavior. Informational metadata includes `publicationMode: informational` and `icoStatus: pending`.

- [ ] Write failing tests for a real packaged informational release: contact response has no form, input or session cookie; GET and synthetic POST to `/api/enquiry.php` return generic HTTP 503 with `Cache-Control: no-store`, no reflected payload and no session cookie, even with absent configuration/autoloader. Run against a loopback PHP server with temporary session storage and verify it stays empty. Assert the endpoint contains no application bootstrapping.
- [ ] Add artifact tests for all public CTA labels (“Contact Melanie”), preserved appointment-request anchor, no active form claims, privacy disclosures reflecting disabled form/session/rate limiting but retaining hosting and third-party review disclosures. Assert no unexpected PHP remains in the informational contact document.
- [ ] Run `python -m unittest tests.test_informational_release -v`; expect failures because informational mode is absent.
- [ ] Implement the transformer using checked replacements (unexpected source structure fails the build), static contact content, generic disabled endpoint and mode-aware metadata. Transform only the temporary extracted artifact, never approved source files or the deployed site.
- [ ] Add deployment execution tests using temporary account directories: informational succeeds without enquiry config; enabled still rejects missing config; wrong home/root still fails; second-swap failure restores prior public tree. Require no enquiry bindings in informational `.htaccess` and retain canonical/security controls.
- [ ] Implement only the mode-specific configuration precondition/binding change, preserving atomic swap and recovery. Retaining unused dependency files is acceptable; they must remain inaccessible and never loaded by the disabled endpoint.
- [ ] Run `python -m unittest tests.test_informational_release tests.test_git_release tests.test_packaging -v` (resolve actual packaging test module name before execution); expect all tests passing. Commit only task-owned files.

## Task 2: Git-controlled mode selection and release documentation

**Files:** Create `config/publication-mode.json`; modify `scripts/build_git_release.py`, `.github/workflows/release-staging.yml`, `.github/workflows/release-production.yml`, `tests/test_git_release_workflows.py`, `tests/test_informational_release.py`, `docs/website-production-runbook.md`, `docs/website-content-review.md`, and the approved spec status.

**Interfaces:** Both release workflows pass `--publication-mode-file config/publication-mode.json`. This file contains exactly `{"publicationMode": "informational", "icoStatus": "pending"}` for the interim release. CLI validates both fields and rejects missing files, unknown keys/values and contradictory state. Do not permit workflow inputs to silently override tracked mode. Existing CLI callers without the flag retain their existing enquiry-build behavior for regression tests; production/staging workflows must always supply the tracked file.

- [ ] Write failing tests for tracked selection, malformed/missing mode file, CLI propagation to metadata and both workflows using the tracked file. Test explicit enabled mode remains available but is not selected by either interim workflow.
- [ ] Run those tests and confirm the expected missing-feature failures.
- [ ] Implement the mode-file reader/CLI wiring and tracked interim selection. Keep all existing source quality and production checks; test the actual transformed artifact in the new suite.
- [ ] Document the owner-approved informational-only exception to ICO completion, recipient/configuration and email-test gates. Keep those requirements unchanged for enabled releases, and retain exact-commit approval, staging acceptance, GitHub reviewer, cPanel dry-run confirmations, TLS/security and rollback checks for both modes. Mark application pending, never completed.
- [ ] Run workflow, runbook and informational tests; expect all passing. Commit only task-owned files.

## Task 3: Complete verification and handoff

**Files:** Update this plan's checkboxes and a task-specific verification record under `docs/`; no public-site edits.

- [ ] Run the full Python suite with `/opt/homebrew/bin/python3 -m unittest discover -s tests -q` in a clean temporary source snapshot with approved vendor dependencies, excluding unrelated root scratch files/worktrees. Run every `tests/php/*Test.php`, PHP lint, all site-validation modes, brand validation and JavaScript syntax checks.
- [ ] Build local staging and production informational artifacts using the tracked mode. Inspect metadata, public boundaries, noindex/canonical differences, contact HTML and endpoint responses. Do not claim these are deployed.
- [ ] Render informational contact/home/privacy at narrow and desktop widths and inspect notice, CTA links, privacy readability and overflow. Use the generated artifact, not the unchanged source preview.
- [ ] Obtain a fresh whole-change code review under the execution skill, address important findings with failing-then-passing regression tests, and rerun affected tests plus the complete suite.
- [ ] Report exact verification results, artifact location and any remaining limitations. Leave the changes ready for staging review; no merge, push or production deployment in this build-and-test step.
