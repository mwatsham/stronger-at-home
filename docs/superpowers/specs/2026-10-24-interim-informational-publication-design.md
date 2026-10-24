# Interim informational publication

Status: Owner approved this design and native implementation on 2026-10-24. Building and testing locally; not deployed.

## Intent and scope

Publish Stronger at Home's approved informational website while Melanie's ICO application is in progress. Record the application as pending, not completed. This is a website release scope decision, not a finding of legal compliance or permission for other patient-data processing.

## Approaches

- Full enquiry-enabled publication: deferred while the recorded ICO gate is unresolved.
- Informational publication with the appointment form and submission endpoint disabled: selected by the owner.
- Hiding only the form: rejected because direct submissions would remain possible.

## Proposed implementation

- Introduce an explicit Git-controlled informational release mode, recorded in release metadata and tested before promotion. No automatic expiry or re-enabling.
- In that mode, render a static contact page with no form, session startup, CSRF token, or form feedback. Retain approved phone and email links. Replace the form section with “Online appointment requests are temporarily unavailable.”
- Reject every request to the enquiry endpoint before configuration loading, session startup, validation, rate-limit storage or mail transport. Return a generic unavailable response without echoing submitted values. Do not log request bodies in application code.
- Change form-directed calls to action to “Contact Melanie” and remove statements that visitors can submit a website enquiry. Preserve the existing appointment-request anchor as a link to the availability notice so old links remain useful.
- Adapt privacy wording to the actual informational site, retaining applicable hosting/security logging and third-party review disclosures. Do not claim that the site collects no personal data at all or that email/phone contact is exempt from obligations.
- Preserve approved artwork, layout, service information and review links. No DNS, mailbox, account-wide PHP, analytics or other unrelated changes.
- Update the production runbook with a narrowly scoped owner-approved informational-release exception: ICO status remains pending; enquiry-specific configuration and mail tests are deferred only for an artifact demonstrably unable to accept website enquiries. Keep all other release gates and rollback safeguards.
- Review the deployment script's current requirement for external enquiry configuration; do not create dummy secrets or silently remove checks from enquiry-enabled releases.

## Verification and release

Prove both rendered absence of form inputs and rejection of direct endpoint requests, with no sessions or mail side effects. Validate all public links and copy, privacy accuracy, both release modes, production artifact identity, and existing regression tests. Use synthetic requests locally only; do not send live mail.

Promote through Git, review staging, then use the guarded production workflow and separately confirmed cPanel mutation plans. Verify public HTTPS, routes, disabled endpoint and deployed source identifier. A successful build alone is not publication.

Re-enabling enquiries requires a separate approved Git release after the pending gate and production enquiry configuration are resolved.
