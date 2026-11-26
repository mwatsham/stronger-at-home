# GoatCounter — minimal analytics activation

## Current authority and release requirements (26 November 2026)

The owner approved updating both sites and enabling tracking, then explicitly approved the minimal account settings and privacy-notice update. This supersedes the preparation-only limits recorded below. Production activation is pending the checked release; do not infer live status from this document.

- Dashboard remains private, public visitor counts disabled and embed access blank.
- Account settings saved: retention **365 days**; sessions, browser, screen, country, region, language and individual-pageview reporting disabled; referrers retained.
- Enable only public production pageviews and accepted-enquiry totals. Staging packages omit the analytics adapter entirely. The adapter also rejects every non-production hostname, private route and preview route.
- Publish the optional-statistics notice and accessible on/off controls together. Honour Do Not Track, Global Privacy Control and a saved opt-out. The only new browser storage is a preference written when someone uses those controls, never an attribution or visitor identifier. Unavailable storage fails closed.
- Narrow CSP additions allow only the pinned provider script and this account's count endpoint, including its image fallback. No general third-party or inline permission is added.
- Keep active enquiries, feedback quotes, staging password protection and the current PHP version unchanged. Do not submit a test enquiry.

Provider bytes were rechecked against the audited SHA-384 pin, with cross-origin integrity support. Offline tests cover both beacon and image fallback, sanitized source labels, preference controls, privacy signals, server-success conversions, and final production/staging packaging. A production pageview/dashboard check follows deployment; it is not proof of enquiry inbox delivery. The historical preparation evidence below is retained, not a statement of current account settings.

### Release decisions

1. Use aggregate statistics for improving this website, with a clear opt-out, not advertising or cross-site profiling. The privacy notice describes provider processing and the site's legitimate-interest basis; this is not a certification of legal compliance.
2. Exclude staging by removing its adapter, in addition to the hostname guard. This is stronger than relying on the runtime guard alone.
3. Keep source attribution page-level: an accepted-enquiry count does not identify the visitor or establish which earlier leaflet scan led to it.
4. Preserve unrelated pending external-link edits outside this release. Update only integrity hashes for reviewed task files.

## Historical preparation record

### Activation review and verification ledger

The fresh, read-only final review found two important packaging safeguards. Both were reproduced with failing tests, then fixed: staging now excludes the adapter asset, references, controls and provider permissions in both enquiry and informational modes; production CSP allows the exact `/count.js` and `/count` paths. Other staging security directives remain byte-for-byte unchanged. The production informational fallback is deliberately not altered by the imagery overlay.

The local privacy controls were checked in the browser: turning analytics off updates the visible status and the choice persists after reload. Offline tests use the actual pinned provider script, with both beacon and rejected-beacon image fallback; no real enquiry was submitted.

Minor deferred: the existing notice's overall last-updated date and historical informational-mode date replacement predate this activation. This does not change the new analytics text or its controls; align those dates in a subsequent copy-only update.

Review boundaries: live receipt and saved account settings require separate operational evidence; no private feedback record or inbox is inspected by the code review; formal legal compliance is not certified; unrelated external-link edits remain excluded. No other issues were deferred.

As of 26 November 2026, the owner has approved local preparation only. Neither live site has been changed. The browser entry passes false, so the local adapter neither loads GoatCounter nor sends counts. Existing CSP also blocks GoatCounter. No account API key or patient information belongs in the code.

## Leaflet QR URL

```text
https://stronger-at-home.co.uk/contact/?utm_source=leaflet&utm_medium=qr&utm_campaign=local-leaflet#appointment-request
```

Encode the complete URL and test the printed QR on a phone before distribution. It opens the enquiry form now; measurement only starts after activation. The three exact tag values map to the fixed source label **Leaflet QR**. Repeated/conflicting tags do not qualify. Unknown parameters are discarded.

Other recognised source/campaign pairs: google/business-profile → Google Business Profile; facebook/business-page → Facebook business page; email/newsletter → Email newsletter. These are source labels, not the separate GoatCounter campaigns widget. Do not put personal information in URL tags.

## What will be measured

- Pageviews on the seven explicitly approved public pages.
- Referring HTTP(S) hostname, or a fixed approved campaign label. No referring path/query, current query/fragment, patient fields or screen size in our payload.
- One `enquiry-submitted` event after a contact page renders the consumed server success flash. This means acceptance by the mail transport, not delivery, booking or treatment.

Missing referrers appear as direct/unknown: some apps, browser privacy features and copied links omit their origin. Counts are approximate and ad blockers may suppress them. Conversion totals are not persistent, visitor-level attribution to the original leaflet scan. There is no attribution cookie or added local/session storage. The provider may process IP address and user agent for its service: do not describe this as processing no personal data.

The provider's standard script contains raw query and screen-size fields. The adapter replaces its payload projection before manually counting and disables automatic page/click events. An integrity hash pins the reviewed provider bytes; an upstream change fails closed rather than silently altering collection. Re-audit before updating that hash. The offline fixture retains the provider's ISC licence header.

## Required before activation

1. Obtain explicit owner approval for activation; this document is not release authority.
2. Recheck dashboard privacy remains “Only logged in users”, public visitor counts off, embed access blank.
3. Confirm retention (12 months proposed), disable unnecessary country/region, screen and browser reports, and review whether sessions are needed. These account settings have not been changed.
4. Review lawful basis/consent requirements and approve accurate privacy wording. Cookieless does not automatically settle all requirements. Publish the reviewed notice together with activation, not beforehand.
5. Verify the current provider script still matches the integrity hash and supports cross-origin integrity loading. Re-run captured-provider payload tests and browser checks with all analytics requests intercepted.
6. Prepare a separately reviewed activation change: browser false → true; permit only `https://gc.zgo.at` in script-src, `https://stronger-at-home.goatcounter.com` in connect-src and img-src (provider fallback). Preserve every other security directive, staging protection and release guard. Do not add wildcards.
7. Use the normal approved staging/production release process. Staging must never send counts, even with the flag true.
8. With explicit approval, verify a labelled production pageview and its source in the private dashboard. Sending any test enquiry needs separate permission. Never use real patient details for analytics testing.

Rollback: disable the adapter, restore the previous CSP and release normally. Do not delete existing analytics data without separate approval.

The adapter skips prerendered pages rather than recording speculative visits. This may miss a later activated prerender, consistent with approximate counting. The provider's special `#toggle-goatcounter` fragment is excluded to prevent its storage changes and blocking alerts; do not advertise it as an opt-out control.

## Privacy wording draft — NOT active or approved for publication

We use GoatCounter to understand visits to our website, where visitors find us and the total number of successfully submitted enquiry requests. Our tracking does not send your name, contact details or enquiry message. It uses approved page names and limited source information rather than full URL queries. GoatCounter does not use analytics cookies. Its service processes technical information such as IP address and browser information to provide aggregate statistics. [Confirm retention, session settings, legal basis, provider information and any required controls before publishing.]

## Local verification scope

Final local result (26 November 2026): 238 Python tests and 21 JavaScript tests passed; all PHP test scripts passed. Development/staging site validation, brand validation and whitespace checks passed. Independent review completed and both important findings were fixed. Changes remain local and uncommitted; no deployment or activation occurred. Existing external-link edits are preserved.

Tests run against a captured provider script with a fake browser transport, plus the real PHP success-flash rendering using temporary local sessions. No real enquiry or analytics event is sent. Real dashboard receipt, inbox delivery and account settings are not proven by offline tests.

Independent review found two activation-path edge cases (provider toggle fragment and modern prerendering); both now have failing-then-passing regression tests. Minor deferred test coverage: rejected-beacon image fallback has been inspected but is not exercised by the fake transport; include it in pre-activation browser testing. Local browser inspection verifies the deferred local script is present with no GoatCounter script/pixel inserted; it is not a browser network trace.

## Pull-request preparation

The owner subsequently approved pushing this work and opening a pull request into develop, but not merging, deploying or activating it. The GoatCounter-only commit excludes the separate pending external-link edits. Analytics browser-contract tests are invoked by the existing Python CI test discovery; no workflow changes are needed. The disabled flag and existing CSP remain unchanged.
