# Production release acceptance — 8 November 2026

The owner accepted the production website following publication of the approved treatment photographs, navy-tunic portrait and seamless photo fades.

## Release provenance

- Production source: `bf51c234150ec2f1f3354854a08e938b768400eb`, merged through PR #33.
- Production artifact: `e8b14333d97a3f28e475c4580b1b6c168ce1cf7a`.
- Production workflow: `42507545439`, all quality and production gates successful.
- cPanel deployment: `65`, successful with matching live artifact and no pending task.
- Owner explicitly approved production promotion and activation, then confirmed “Looks good.”

## Verification

All 217 local Python tests passed, production and brand validation passed, and independent review found no remaining actionable issues after the informational-fallback guard was added. Production Home, About and services pages and approved image assets match the accepted staging composition.

After activation, all seven public pages, the Google verification file, fade stylesheet and four approved images returned HTTPS 200. The three updated page responses and the new image/CSS bytes matched the release artifact exactly. The navy portrait and respiratory photo fades were checked in the browser. An existing cached services page required a fresh release query parameter; refresh if older content appears.

HTTP redirects to HTTPS. Production `/design-preview/` returns 404 and does not have staging authentication. The contact page retains the enquiry form and CSRF markup. No enquiry was submitted and no test email was sent during this release; email delivery was not re-tested.

## Preserved state

- Production enquiries remain active; private email configuration was not changed.
- PHP remains `8.3.36`; no PHP settings were changed.
- The existing pending-registration exception `owner-pending-registration-2026-10-24` remains unchanged. This release does not assert completion of ICO registration.
- Staging remains deployment `64`, artifact `bc1bc419d0723e753489ea1b25cf5f9d4c85c9cf`, with the expected HTTP 401 Basic authentication challenge.
- Previous production artifact `9cbda3ea3ce4122d412a27ba90d6dcbe705e13a8` remains identifiable in release history for recovery through the guarded process.

## Repository follow-up

The owner requested recording acceptance and syncing `develop` with `main`, keeping both live sites unchanged. This record accompanies the main-to-develop integration. Automatic staging artifact preparation is not a hosting activation; no cPanel checkout update or deployment is authorised by this documentation-only follow-up.
