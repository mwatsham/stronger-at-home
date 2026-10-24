# Interim informational release verification — 24 October 2026

Status: built and tested locally; not merged, pushed or deployed. ICO application remains pending.

## Implemented

The tracked publication-mode file selects informational mode for both Git release
workflows. The builder transforms only its validated temporary artifact: approved
enquiry-enabled site sources remain intact. The generated contact page is static,
the endpoint returns generic HTTP 503 with no-store, form-directed buttons say
“Contact Melanie”, and privacy wording reflects the unavailable form. Existing
contact links and appointment-request anchors remain usable.

Informational deployment omits only the external enquiry configuration requirement
and its Apache bindings. Enabled deployment retains that requirement. Atomic swap,
rollback, path guards, existing source/dependency validation and release approvals
remain in place. No hosting, account-wide PHP or mail settings were changed.

## Evidence

- Initial new tests failed because the builder did not support informational mode.
- Mode-file tests failed before CLI/workflow implementation.
- 32 targeted release/workflow/runbook tests passed before final review.
- Independent review identified duplicate JSON key acceptance as Important. A
  regression reproduced a contradictory file selecting enquiries; the parser now
  rejects duplicate keys before creating an artifact. Regression passed after fix.
- Final full Python suite: **197 tests passed**, 30.146 seconds, using Homebrew
  Python in a clean source snapshot with the approved vendor tree.
- All five PHP test scripts passed; PHP syntax checks passed for site, test and
  configuration PHP. Site validation passed in development/staging/production;
  brand validation, JavaScript syntax and whitespace checks passed.
- Real loopback HTTP tests: contact HTTP 200 without form/cookie; endpoint GET,
  POST, PUT and OPTIONS HTTP 503/no-store, no input reflection and no cookies;
  temporary session directory remained empty. No live form submissions or mail.
- Local staging and production informational artifact builds succeeded, with
  noindex retained for staging and absent from the production Apache directives.
- Local simulated-account tests exercised informational deployment without private
  enquiry config and rollback after second-move failure. Existing enabled-mode
  tests still cover missing config and wrong target rejection.
- Browser screenshots inspected desktop contact and mobile 390px-wide home,
  contact and privacy views. The notice alignment issue was corrected and desktop
  contact rechecked. This is not a complete accessibility audit or live Apache test.

## Decisions and limitations

- Worked on local feature branch `codex/interim-informational-release`, preserving
  unrelated staged AGENTS.md and scratch files. No new worktree was created.
- Retained unused approved dependencies in the artifact to preserve the existing
  packaging boundary; the disabled endpoint never loads them.
- Local preview builds used the parent source SHA as a development label before
  commit, not a deployable provenance claim. Regenerate release artifacts from the
  exact approved committed revision before promotion.
- Reviewer minor deferred: add a sentinel-file HTTP test with existing external
  config/autoloader bindings. Current tests omit those bindings; endpoint inspection
  confirms no require/include/bootstrap code, and HTTP tests prove no sessions.
- Reviewer exclusions accepted: legal adequacy is not established by these tests;
  live Apache/cPanel, TLS and production approval remain deployment-stage gates.
  Visual review was performed separately as described above.
- The root source preview still shows the enquiry-enabled source by design. Review
  the generated informational preview at http://127.0.0.1:58634/contact/ instead.

Next: owner review of the generated copy, then separately authorised staging
promotion and production release gates. Do not re-enable enquiries automatically.
