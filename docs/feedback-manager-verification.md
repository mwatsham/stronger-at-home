# Feedback manager — local verification

Date: 10 November 2026. Branch: `codex/feedback-manager`.

## Scope

Melanie-only private feedback administration and published-quote carousel. No push, merge, hosting configuration, deployment, enquiry submission or live-site changes were performed. Hosted credentials have not been created.

## Evidence

- Python regression suite: 229 tests passed using the pinned Pillow 12.3.0 dependency from the existing temporary dependency directory.
- Feedback storage and authentication PHP tests passed.
- Carousel: seven JavaScript tests passed, including eight-second timing, manual stop, reduced motion, temporary pause and native browser timer binding.
- Development, staging and production source validation passed; brand validation passed.
- Local HTTP integration covers authentication, CSRF, publish permission, CRUD, draft-only edits, revision conflicts, escaping, throttling and unavailable storage.
- Independent whole-feature review identified one important issue: rejected saves discarded unsaved wording. Fixed with failing-then-passing HTTP regression coverage. Stale revisions remain stale until explicit reconciliation, so the fix cannot silently overwrite newer changes.
- Browser inspection found native timers called with the controller as their receiver. Fixed with failing-then-passing regression coverage and verified the carousel renders in the in-app browser.
- Desktop and 390px-wide browser checks confirmed readable quote cards and Previous/Next/Play controls; manual navigation stops autoplay. Private login screen verified visually.

## Local preview

- Website: http://127.0.0.1:58640/#share-your-experience
- Manager: http://127.0.0.1:58640/feedback/admin/
- Username: `melanie`; password is a random local-only value in an owner-only temporary file, not in this repository.
- Sample quotes are explicitly labelled demonstrations, not patient feedback. Enquiry endpoints are disabled in the local runner.
- Automated HTTP tests exercise the signed-in workflow; interactive signed-in visual review remains for the user, who has been given the local password-file location. Reduced-motion behavior has automated coverage; browser OS reduced-motion preference was not changed.

## Before any hosted rollout

Provision separate private staging/production configurations and credentials through a separately approved operation, test staging behind its existing password protection, and obtain release approval. Back up the private quote store independently of code releases. Do not publish demonstration quotes.
