# Trustpilot Review Collector — approved local implementation

Requested by the project sponsor: the supplied TrustBox bootstrap script and
Review Collector widget for Stronger at Home Physiotherapy.

- Location: homepage, immediately before the final appointment call to action.
- Loader: HTTPS, asynchronous, homepage only.
- Locale and widget identifiers: preserved as supplied.
- Public fallback link: https://uk.trustpilot.com/review/stronger-at-home.co.uk,
  supplied by the sponsor on 7 September 2026. This changes the HTML link only;
  the provider-controlled widget destination and en-US locale remain unchanged.
- CSP: allow only widget.trustpilot.com for external scripts and frames;
  no wildcard, unsafe-inline, unsafe-eval or invitation endpoint.
- Fallback: a descriptive public Trustpilot profile link remains usable when
  JavaScript or the provider is unavailable.
- No existing reviews or ratings are displayed by this widget.
- No invitation calls, appointment-form values or patient records are sent.

## Browser observations

The official widget rendered at desktop and 390px mobile widths under the actual
site CSP applied to local preview responses. No CSP errors or horizontal
overflow were observed; the fallback link remained visible when the provider
was blocked. No cookies were set in the clean test browser.

The widget made GET requests to Trustpilot for its content and statistics
(impressions and views), including page URL, browser information and referrer.
This is not a guarantee about all future provider behaviour or existing
Trustpilot sessions. The privacy notice includes a factual description of
these requests and the separation from appointment-form data.

## Approval — 7 September 2026

The project sponsor approved the local layout and privacy addition.
The draft label and privacy-approval content blocker have been removed, and
the notice date and approved source fingerprint updated. This approval is
not attributed to Melanie personally. Staging and production deployment
remain separate release decisions.

No deployment or review submission was performed for this change.

## Google review link — 7 September 2026

The sponsor supplied https://g.page/r/CYqDnIzAeBQuEBM/review for the proposed
"Review us on Google" button. It sits beside Trustpilot on wider screens and
stacks on narrow screens. It uses the existing website button style, opens a
new tab and suppresses the referring page address. No Google scripts,
iframes, automatic invitations or ratings were added.

The supplied URL is allowed only as a navigation link, not a script resource.
The automated web reader could not resolve this Google short link; its
business destination still needs confirmation in the user's browser.
This update is local only and does not authorise deployment.
