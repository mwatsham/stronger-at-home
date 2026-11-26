# GoatCounter analytics — approved local preparation

## Goal and authority

Prepare traffic-source measurement and accepted-enquiry counts for Stronger at Home. On 26 November 2026 the owner confirmed email verification and approved local implementation and testing. Activation is NOT approved. Both live sites remain unchanged.

## Scope and constraints

- Tracking is disabled by default; disabled means no GoatCounter script, request, pixel or preconnection.
- Only HTTPS on the exact production hostname `stronger-at-home.co.uk` and explicitly listed public pages is eligible after a future activation.
- Never track staging, localhost, preview pages, feedback administration, API endpoints or unknown routes.
- Preserve existing enquiries, private feedback, credentials, password protection and PHP configuration. No deployment, push, email submission or account-setting changes in this task.
- Preserve the worktree's pending external-link changes.

## Measurement

Pageviews use static public paths and titles, never raw query strings or fragments. Referrers are reduced to HTTP(S) hostnames; same-site and missing referrers become empty. “Direct” therefore means no identifiable source, not proof of a typed address.

Recognise only these fixed campaign pairs: `utm_source=google&utm_campaign=business-profile`, `utm_source=facebook&utm_campaign=business-page`, and `utm_source=email&utm_campaign=newsletter`. Map them to fixed source labels, not arbitrary supplied values. This first implementation reports these as source labels; it does not promise GoatCounter's separate campaign widget or visitor-level conversion attribution.

Record `enquiry-submitted` / `Enquiry submitted` only from the existing one-use server success flash on the contact page. Submit clicks, validation failures, delivery failures, honeypot redirects and manually opening `?sent=1` do not count. The event means the mail transport accepted the request, not inbox delivery or an appointment booking. Count at most once per document; refreshing consumes no second server success flash. No form fields are read for analytics.

Approved addition: the exact triple `utm_source=leaflet&utm_medium=qr&utm_campaign=local-leaflet` maps to **Leaflet QR**. Repeated/conflicting tags do not qualify. The QR URL ends with `#appointment-request` to open the form section.

## Integration and privacy boundaries

Use GoatCounter's manual counting interface with automatic page and click tracking disabled. Endpoint: `https://stronger-at-home.goatcounter.com/count`; script: `https://gc.zgo.at/count.js`. Explicitly supply safe path, title and referrer. Inspect the provider script before integration for query-derived campaign fields and other defaults; prevent unsanitised URL data reaching any payload. Do not enable localhost tracking or persistent client-side attribution storage.

Keep current CSP unchanged during disabled preparation. Document the narrowly scoped CSP changes needed for future activation. Analytics loading or counting failures must never interrupt navigation or enquiry handling.

The dashboard was verified private before this request. Recommended retention and reduced device/location collection remain activation checklist items, not changes made by this task. Draft truthful privacy wording separately; do not describe analytics as active on the current website. No assertion that cookieless analytics automatically satisfies every legal obligation.

## Acceptance

Tests use an injected fake browser/transport, not GoatCounter or SMTP. Verify default-off network silence, production-only eligibility, sensitive-data removal, one-use accepted-enquiry behaviour, graceful provider failure and exclusions. Run existing site, enquiry and carousel regressions and an independent final review. Leave code disabled and live sites untouched.

## References

- https://www.goatcounter.com/help/js
- https://www.goatcounter.com/help/campaigns
- https://www.goatcounter.com/help/privacy
