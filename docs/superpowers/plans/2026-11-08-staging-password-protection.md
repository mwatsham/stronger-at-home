# Staging Password Protection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Preserve Melanie's working staging password protection across every Git deployment without changing production.

**Architecture:** Generate staging-only Apache Basic authentication rules in the release builder. Reference cPanel's external password file and abort staging deployment before changing any public tree when that file is missing, empty, unreadable or a symlink. Never package credentials or copy arbitrary live configuration.

**Tech Stack:** Python release builder/tests, Apache .htaccess, Bash atomic deployment, guarded cPanel CLI.

**Spec:** `docs/superpowers/specs/2026-11-08-staging-password-protection-design.md`

## Global Constraints

- Keep production, PHP 8.3.36, mail routing and enquiry behaviour unchanged.
- Credential file: `/home/v0398ees6dry/.htpasswds/public_html/staging.stronger-at-home.co.uk/passwd`.
- Authorised user: `melanie`; no password or hash in Git, artifacts, output or chat.
- Require staging authentication for pages, assets and API routes; preserve noindex controls.
- Keep the existing protection enabled while preparing and deploying the change.
- Preserve the user's unrelated root-worktree changes; reuse a suitable clean worktree based on current develop.

## Review Focus

1. Production accidentally receives authentication: compare production artifacts before/after for identical generated configuration and scripts.
2. Missing/empty/unreadable/symlink password file: fail before public-tree swap and leave the existing protected site intact.
3. A subsequent release silently removes protection: exercise two generated releases and require identical authentication blocks in both.
4. HTTP credential challenge or error-page recursion: test Apache HTTP/HTTPS behaviour; use a local 401 response rather than protected error-page recursion.
5. Informational publication mode bypasses protection: require the same authentication in all staging publication modes.

## Task 1: Durable staging artifact and deployment guard

**Files:** Modify `scripts/build_git_release.py`; extend `tests/test_git_release.py`; update `docs/website-staging-runbook.md`.

**Interfaces:** Keep `deployment_script(environment, source_sha, publication_mode)` and `_configure_htaccess(htaccess, environment, bindings)` signatures. Add internal staging-only constants/helpers as needed; no secret CLI inputs or credential exports.

- [ ] Write failing artifact tests asserting staging `AuthType Basic`, the exact external `AuthUserFile`, `Require user melanie`, and non-recursive 401 handling; verify presence in enquiries, enquiries-pending and informational modes. Assert production output is unchanged.
- [ ] Run `/opt/homebrew/bin/python3 -m unittest discover -s tests -p test_git_release.py -v`; confirm new tests fail for absent authentication, not fixture errors.
- [ ] Implement deterministic staging authentication generation with HTTPS-only credential handling. Review Apache semantics against official documentation before choosing directive ordering; do not rely on a late redirect to make an early authentication challenge safe.
- [ ] Add failing executable deployment tests for absent/empty/unreadable/symlink credential files and successful valid-file deployment. Test both first and subsequent releases, including existing atomic-swap rollback.
- [ ] Implement pre-swap staging-only credential checks. Update temporary deployment fixtures using synthetic local credentials only. Never read real credential contents.
- [ ] Run focused tests and the complete project quality gate, including PHP tests/lint, Python discovery, site/brand validators and JavaScript syntax check. Report any unavailable live-Apache verification separately rather than claiming coverage.
- [ ] Update the staging runbook: expected anonymous 401, owner-assisted authenticated verification, HTTPS handling, credential persistence and no rollback to old unprotected artifacts.
- [ ] Review and commit only the scoped code/tests/docs in the isolated checkout. Present results for the normal PR/deployment approval workflow; do not deploy production.

## Task 2: Guarded staging rollout and acceptance

**Interfaces:** Consume Task 1's validated staging artifact through existing GitHub/cPanel release workflow, not manual website edits.

- [ ] Obtain required PR/merge and exact cPanel checkout/activation approvals. Verify production remains at its existing deployment throughout.
- [ ] Confirm cPanel still lists `melanie` and the verified credential path; inspect metadata only.
- [ ] Activate the reviewed staging artifact. Require deployment success and matching private source marker.
- [ ] Anonymous HTTPS requests to home/contact/CSS/image/API return 401 without application output; HTTP does not invite credential entry or expose protected content. Check production remains public.
- [ ] Ask owner to verify authenticated navigation using Melanie's password in their own browser. Do not send an enquiry or request the password in chat.
- [ ] Prove persistence with a separately approved subsequent staging release, including anonymous and owner-assisted authenticated checks. Record limitations until that repeat-deployment test is complete.

## Planning status

Verified existing account and current anonymous protection on 8 November 2026.
Task 1 implemented and tested natively: 211 Python tests, PHP tests/lint,
site/brand validators and JavaScript syntax checks passed. Production generated
configuration and deployment scripts are byte-identical in all three modes.
Independent review found an inherited-authorization issue; a failing native
Apache regression was added and the fix preserves existing file-access denials.
No hosting mutations performed. Task 2 remains behind separate release approval
and owner-assisted hosted acceptance, including a subsequent deployment.
