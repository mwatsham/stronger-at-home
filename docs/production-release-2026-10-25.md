# Production release acceptance — 25 October 2026

## Released and accepted

- Website: https://stronger-at-home.co.uk/
- Source: `255601532ba45a1692f52d0ab380498742d9560d` (PR #19).
- Release: `b4285565c3ecdcfe77d3738138f09888f0328e5f`.
- Production preparation: GitHub Actions run `40191644574`, successful.
- cPanel deployment: `52`, successful; deployed source marker matched.
- Owner explicitly approved activation of this release and enquiries to Melanie.
- PHP remained `8.3.36`; no PHP settings were changed.

## Verification and delivery

All seven public pages and checked CSS, JavaScript, logo, robots and sitemap returned HTTP 200. HTTPS/canonical redirects, security headers, production indexing, form and CSRF presence, secure session cookie flags and private-file protection passed. The enquiry endpoint returned 405 for GET, invalid CSRF returned 403, and the honeypot followed its no-mail response path. Responsive and keyboard checks were not repeated during this activation.

The owner separately authorised one labelled synthetic production enquiry. Exactly one was submitted; the application returned its success confirmation. The owner subsequently confirmed that Melanie received the test email on 25 October 2026. End-to-end delivery to the configured sole production recipient, `melanie@stronger-at-home.co.uk`, is therefore confirmed. No patient or health information was used.

Production enquiries are active. This acceptance does not assert legal compliance: ICO status remains **pending**, with recorded owner exception `owner-pending-registration-2026-10-24`.

## Google verification follow-up

The owner supplied `googled25927956a9f99cc.html` for publication at the website root. Its exact content is retained in `site/` and included in the approved public-file manifest and release packaging regression test. SHA-256: `727e794a60581a49b99dec5151b336be565cf40065a5e9013226dfb3ba81ad3b`.

This follow-up is not part of release `b428556`. Publish it through the Git release workflow, verify HTTP 200 and matching content at `https://stronger-at-home.co.uk/googled25927956a9f99cc.html`, then complete verification in Google Search Console. Google verification has not yet been confirmed.
