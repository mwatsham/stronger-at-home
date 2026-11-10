# Public-content cleanup release — complete

Recorded on 10 November 2026 from the successful deployment and verification performed on 8 November 2026.

## Approved scope

The owner explicitly approved expedited staging and production release of the removal of home-address references, including structured metadata, AI-content notices, and complaints references. General service-area wording, business email and phone, and enquiry handling were retained. Historical internal records, Git history and third-party search caches were not purged.

## Release provenance

| Environment | Source commit | Deployment artifact | Successful cPanel deployment |
| --- | --- | --- | --- |
| Staging | `8324b890c5931c5994f1dbf46477c922b2657e37` | `82ee9101d73b256f0260d6526eea276dd7d7bf5b` | 66 |
| Production | `f5e1d492ec3c64258510f025067a2bf2cb86b3a0` | `adfc4ad859404291ec89898ec7131ab956a8498c` | 67 |

- [PR #36](https://github.com/mwatsham/stronger-at-home/pull/36) merged the cleanup into develop after CI passed.
- [Staging build](https://github.com/mwatsham/stronger-at-home/actions/runs/42528323988) passed and its provenance and public contents were checked before activation.
- [PR #37](https://github.com/mwatsham/stronger-at-home/pull/37) passed CI and merged into main after staging verification.
- [Production build](https://github.com/mwatsham/stronger-at-home/actions/runs/42528612798) passed all quality and production gates before activation.

## Completed release checks

- All 218 local Python tests passed, including scans of the built staging and production public files for the removed references.
- Development, staging, production and brand validation passed; independent review found no blocking issues.
- Both cPanel deployment tasks succeeded with the expected artifact identifiers and no pending tasks.
- All seven production sitemap pages returned HTTPS 200 with the requested references absent. Static page responses matched the approved production artifact byte-for-byte.
- Production contact page retained the active enquiry form and reported PHP 8.3.36.
- Staging deployed page contents were checked using read-only hosting access. Anonymous requests to home, privacy, contact and design preview returned HTTP 401 with the expected Basic authentication realm.
- Staging password-file metadata remained unchanged.
- No enquiry was submitted, no test email was sent, and no PHP or private email configuration was changed.

## Repository follow-up — 10 November 2026

The owner requested this record and synchronisation of develop with main while keeping both live sites unchanged. This documentation-only integration includes the production merge commit in develop's history. The automatic staging workflow may prepare a new deployment artifact; artifact preparation does not activate a live site.

No cPanel checkout update, activation, production workflow dispatch, password change or PHP change is part of this follow-up. This record does not assert completion of ICO registration or re-test email delivery.
