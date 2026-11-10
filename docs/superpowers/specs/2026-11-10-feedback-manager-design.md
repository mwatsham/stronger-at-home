# Feedback manager and quote carousel

## Approved design

The owner approved a built-in feedback manager with Melanie as sole administrator. She can add, edit, preview, order, publish, unpublish and delete direct-feedback quotes without a website release. Each quote has text, public attribution and permission-to-publish confirmation. Do not collect original messages or patient records.

The public homepage retains Google and Trustpilot links and adds clearly labelled direct feedback. Carousel interval is eight seconds. Previous/Next stops autoplay until Play is selected. Pause/Play is visible. Hover and keyboard focus pause rotation; reduced motion disables autoplay. Controls and text remain readable and keyboard accessible.

Keep staging and production content separate. Persist content outside release folders. Keep credentials private; Melanie sets her password privately. Build and test locally for this request; do not change either live site, provision hosting credentials, push, merge or deploy.

## Approaches considered

The owner selected a small built-in manager instead of an external CMS. It fits the existing PHP hosting and avoids another service, but requires authentication, persistence and security testing.

## Implementation decisions

- Use existing PHP and browser JavaScript; no new framework or hosted service.
- Keep the homepage static; fetch published-only JSON from a same-origin PHP endpoint. Existing review links remain usable if JavaScript or the feedback service fails.
- Use an environment-specific private JSON store with locking, atomic replacement, revision checks and restrictive permissions. Small curated quote collections do not require a database.
- Separate admin sessions from enquiry sessions. Use password hashes, secure cookies on HTTPS, CSRF protection, login throttling, session expiry and session-ID rotation.
- No public sign-up or email password reset. Credential setup/recovery is an operator-only process outside the public web root. No default production password.
- Local HTTP is allowed only by explicit local configuration on loopback. Use isolated demo content visibly labelled as preview samples, never fabricated testimonials presented as genuine.
- Published responses contain only quote text, attribution and order; exclude drafts, consent metadata and authentication details. Render text safely, never as HTML.
- An edit to published wording returns that record to draft until publication is confirmed again. Delete requires confirmation. Concurrent edits must report a conflict, not overwrite silently.
- Zero quotes hides the carousel; one quote hides rotation controls. Failed loading leaves the rest of the page intact.

## Acceptance

Verify admin permissions, CSRF, throttling, session expiry, input validation, escaping, concurrent writes, draft isolation, all editing actions, carousel timing/manual-stop/reduced-motion behaviour, packaging exclusions, and persistence across simulated releases. Provide local public and administrator previews. Real feedback and live credential provisioning remain outside this local-preview task.
