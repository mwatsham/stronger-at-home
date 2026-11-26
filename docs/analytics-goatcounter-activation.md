# GoatCounter — prepared, not activated

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
