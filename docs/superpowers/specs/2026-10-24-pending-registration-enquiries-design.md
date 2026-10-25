# Enquiries while registration is pending

## Authority and intent

On 24 October 2026 the owner confirmed the ICO application and fee steps are
still being completed and instructed: “Record the pending-registration exception
and proceed with enabling enquiries.” This supersedes the informational-only
restriction for the requested enquiry release. It does not assert registration,
payment, exemption, or legal compliance. ICO status must remain pending.

## Approach

Restore the existing approved enquiry form, controller, privacy notice and
appointment wording through the normal Git release pipeline. Do not redesign
the form, create patient records, add analytics, or change PHP settings.
Reject falsely marking registration completed and reject direct live-file edits.
Keep CSRF, validation, rate limiting, escaping, honeypot and session protections.

Represent the exception explicitly in tracked publication configuration and
generated release metadata using a fixed approval identifier
`owner-pending-registration-2026-10-24`. Pending enquiry mode without this
identifier must continue to fail closed. This identifier is an audit reference,
not a credential or a finding of compliance. Preserve existing informational
and completed-registration modes.

## Hosting and delivery

Read-only inspection found the production private configuration directory absent.
Before activation, create owner-only production configuration and rate-limit
storage outside the web root through separately approved cPanel dry-run plans.
Use production origin https://stronger-at-home.co.uk, sole recipient
melanie@stronger-at-home.co.uk, and the existing provider relay approach
(localhost:25, no SMTP authentication/encryption). Verify sender against the
existing supported setup; never copy staging recipients or reuse its rate secret.
Generate a new production rate-limit secret without displaying or committing it.
Keep PHP 8.3.36 unchanged. Staging delivery remains directed to webadmin only.

## Release checks

Run automated security and release tests, then a staging delivery test with
synthetic data. Require receipt confirmation and accepted staging before
production promotion. Obtain exact production deployment approval, then perform
one clearly labelled synthetic production delivery test to Melanie and request
receipt confirmation. Do not use actual patient information. Preserve recovery
files and check TLS, redirects, assets, session-cookie protections and private
file exclusion. The owner-only approval from the prior release was one-release
only; request a new owner-only release approval when presenting this artifact.

## Constraints

No representation that ICO registration is completed. No change to unrelated
hosting, DNS, email accounts, GitHub protection settings or other websites.
The form's medical-information warning and privacy notice remain in place;
these controls do not remove the possibility of receiving health information.
