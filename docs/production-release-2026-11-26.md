# Production release completion — 26 November 2026

The owner approved promotion of all staging updates, including the automatic photo crossfade, approved treatment images, Melanie's professional credentials, and prepared but disabled GoatCounter code. Production activation and the follow-up stylesheet-cache correction succeeded.

## Final release provenance

| Environment | Source revision | Deployment artifact | cPanel deployment |
| --- | --- | --- | --- |
| Production | `92d468949bd44859f49ecaab5548733dc960f939` | `00fb3735ef13e4e52d0edd50a6f9a329e523b5a2` | `77` |
| Staging | `04d98226ff3249acb726d29f9377c7f93a1f184c` | `226111fe486962f4957a7bf4893b263342a5271f` | `76` |

- Photo release: PR #47 into develop and PR #48 into main.
- Cache correction: PR #49 into develop and PR #50 into main.
- Final production build: [45874000816](https://github.com/mwatsham/stronger-at-home/actions/runs/45874000816), successful.
- Final staging build: [45873594322](https://github.com/mwatsham/stronger-at-home/actions/runs/45873594322), successful.
- Production source marker matched the final source revision; both deployments reported success with no pending tasks.

## Verification at activation

- Production home, About, contact and feedback-admin sign-in pages returned HTTPS 200 with valid TLS. HTTP and www requests redirected to the canonical HTTPS site during the initial release checks.
- The live enquiry form remained present. No enquiry was submitted and no test email was sent; email delivery was not re-tested.
- Published feedback feed SHA-256 remained `538540d690040a9178355fb69c61c47f0cfc6622ae59d04fc6007e603d42aaf6` before and after activation. Melanie's private quote store and configuration were not modified.
- The live browser initially retained an old photo stylesheet. Content-hashed stylesheet URLs corrected this without requiring visitors to clear their cache. The same browser then displayed the seamless photo frame correctly and automatically advanced from the seated photo to the standing photo, with no photo controls.
- The cache regression test failed before the correction. The local suite then passed 241 Python tests and 36 JavaScript tests; the Python total includes an unrelated local external-link test whose changes were excluded from the release. Independent review found no blocking issues. GitHub checks and final release builds passed.
- Staging continued to return HTTPS 401 to anonymous visitors, retaining password protection. The versioned stylesheet link was checked through cPanel readback; an authenticated staging-browser check was not repeated in this release session.

## Preserved state

- Enquiries remain active; private delivery configuration was not changed.
- PHP was observed as `8.3.37` before and after release. No PHP settings were changed.
- Tracking remains disabled: the published analytics entry point passes `false`, and no GoatCounter script was loaded in the verified browser.
- Melanie's quotes, staging password protection and private configuration were preserved.
- The existing pending-registration exception remains unchanged; this record does not assert completion of ICO registration.

## Repository follow-up

At the owner's request, remote develop was fast-forwarded from `04d98226ff3249acb726d29f9377c7f93a1f184c` to released main `92d468949bd44859f49ecaab5548733dc960f939`. Their file trees were already identical; the sync adds the production merge commit to develop's history.

The sync may automatically prepare a new staging artifact, but artifact preparation does not activate hosting. No cPanel checkout update, hosting deployment, PHP change, tracking activation, enquiry submission or private-data change was performed for this record-and-sync task. Both live sites remain on the deployments listed above.

This documentation is recorded separately from the released source. Unrelated local external-link edits remain preserved and excluded.
