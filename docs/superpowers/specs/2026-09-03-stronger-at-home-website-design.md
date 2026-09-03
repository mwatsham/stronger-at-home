# Stronger at Home Physiotherapy website design

Status: approved design; implementation and publication not yet approved

Approval owner: Project sponsor for this design; Melanie Watsham retains final
approval of public-facing content and compositions

Approved on: 2026-09-03

## Objective

Create a calm, reassuring website that helps an adult patient understand the
home physiotherapy service and request an appointment. The website must build
trust progressively, work well for people with mobility or accessibility
needs, and avoid implying that an enquiry is an instant confirmed booking.

The initial success measure is a clear, usable route to a suitable appointment
request by email, phone or website enquiry. Online scheduling, payments,
patient accounts and clinical record storage are outside this design.

## Approved decisions

- The primary audience is the adult patient. Family members and professional
  referrers may use the site, but the homepage speaks directly to the person
  receiving treatment.
- The primary call to action is `Request an appointment`.
- The initial website has five principal pages: Home, About Melanie, How I Can
  Help, Appointments & Fees, and Contact.
- The content follows a reassurance-first journey rather than a service
  directory or clinician-first presentation.
- Melanie appears on the homepage with a short personal introduction and a
  portrait. A clearly labelled placeholder may be used in development, but it
  must not be treated as final or published to production.
- The visual direction is the approved calm-editorial homepage composition:
  warm, spacious, patient-focused and balanced by Melanie's portrait.
- The implementation is a lightweight static website with a small server-side
  enquiry handler on the existing cPanel hosting.
- Staging is reviewed at `staging.stronger-at-home.co.uk` before any production
  release to `stronger-at-home.co.uk`.

## Content architecture

### Home

The homepage leads the patient through this sequence:

1. Patient-focused promise and `Request an appointment` action.
2. Common reasons the patient may need physiotherapy.
3. Benefits of receiving physiotherapy at home.
4. Short introduction to Melanie with a portrait placeholder during
   development.
5. Initial-assessment and follow-up visit information.
6. Service area and individual-fee explanation.
7. Final appointment-request prompt.

The approved opening is:

> **Physiotherapy to help you feel stronger at home**
>
> Personal home visits for adults in Epsom and surrounding areas, supporting
> recovery, mobility, balance and confidence.
>
> **Request an appointment**

`Call Melanie` is the quieter secondary action. Supporting trust points may
include `20+ years of NHS experience`, `Adults only`, and treatment in the
patient's home. Do not present unverified credentials.

### About Melanie

Explain Melanie's personal approach, professional experience and motivation
in concise, patient-friendly language. The approved claim is more than 20
years of NHS experience. HCPC, CSP, AGILE and ATOCP wording remains excluded
until separately verified and approved.

A professional portrait is required before production publication. The image
should feel warm and credible, use a simple uncluttered setting, and remain a
photograph rather than an AI recreation of Melanie.

### How I Can Help

Use need-led headings instead of an exhaustive list of diagnoses. Cover:

- recovery after surgery;
- rehabilitation following hospital admission;
- decline in mobility or physical function;
- rehabilitation following a fall;
- falls prevention; and
- mobility, balance and confidence at home.

The page must not claim guaranteed outcomes. Referral suitability, exclusions
and escalation wording are deferred and must not be invented.

### Appointments & Fees

Explain that:

- initial assessments last 60 minutes;
- follow-up appointments last 45 minutes;
- appointment hours are flexible and subject to availability;
- visits are available within approximately 10 miles of Epsom and surrounding
  areas, subject to address confirmation;
- fees are quoted individually because travel requirements vary by location;
- the patient supplies a postcode or address; and
- a fixed price is confirmed and agreed before the appointment is booked.

Payment can be made by cash or bank transfer. Do not publish payment timing,
account information or additional payment conditions unless they are
separately approved.

### Contact

Present the approved telephone number and email address prominently, followed
by the enquiry form. The page explains that submitting the form requests an
appointment and that Melanie confirms availability directly.

The address may appear in the site footer or legal identity area because it is
an approved public contact field. It must not be presented as a walk-in clinic
or patient-visit location.

### Supporting pages

The footer links to Privacy and Accessibility notices. A custom 404 page,
`robots.txt` and XML sitemap support the public site but do not appear in the
primary navigation.

## Visual system

Use the existing approved tokens:

- Deep Navy `#203E55` for primary text, navigation and strong sections.
- Pale Sky `#E8F1F6` for supportive information panels.
- Warm Cream `#F7F2E8` for calm editorial backgrounds.
- Warm Sand `#C3A26E` for restrained progress accents and selected calls to
  action.
- Source Serif 4 for display headings.
- Atkinson Hyperlegible Next for body and functional text.

The exact approved raster-only logo files are used without redrawing,
recolouring, transparency conversion or geometry changes. Web optimisation may
select the appropriate approved size and use lossless delivery techniques; it
must not change the approved pixels.

The layout uses generous whitespace, clear section boundaries, short line
lengths and rounded but restrained information cards. Decorative movement
motifs should suggest progress without becoming clinical diagrams. Avoid
stock-photo stereotypes of frailty, hospital imagery, intrusive animation and
visual clutter.

## Responsive and accessible behaviour

The implementation targets WCAG 2.2 AA. It must include:

- semantic landmarks and a logical heading hierarchy;
- a keyboard-accessible navigation menu and visible focus indicators;
- a skip link;
- descriptive alternative text for meaningful images and empty alternative
  text for decoration;
- labels, instructions and field errors associated with form controls;
- no meaning conveyed by colour alone;
- support for text resizing and reflow without horizontal page scrolling at
  narrow widths;
- touch targets appropriate for users with reduced dexterity;
- reduced-motion preferences; and
- tested colour contrast for text, controls and focus states.

The mobile layout keeps the appointment action visible without covering page
content. Navigation collapses to a labelled menu button. Content order stays
the same as the approved desktop hierarchy.

## Enquiry form

The form collects only:

- name;
- email address;
- phone number;
- preferred contact method;
- postcode;
- a short enquiry message; and
- acknowledgement of the privacy notice.

Name, postcode, message and privacy acknowledgement are required. At least one
of email address or phone number is required, and the field matching the
preferred contact method must be present. The interface asks patients not to
include detailed or urgent medical information. It does not request date of
birth, medical records, payment information or attachments.

Submitting the form posts to a small same-origin server-side handler. The
handler performs server-side validation and sanitisation, applies accessible
spam controls and rate limiting, and sends the enquiry to
`melanie@stronger-at-home.co.uk` through an authenticated, deployment-time
configured mail transport. Mail credentials live outside the public document
root and are never committed to source control.

The application does not create a patient database. Any temporary
rate-limiting data must contain no enquiry content and expire automatically.
Server and application logs must not record the submitted message or contact
details.

On success, use a redirect-after-post flow and show an acknowledgement that
the request was received. The acknowledgement must not say or imply that an
appointment is booked. On validation failure, show field-level guidance and
preserve only safely escaped, non-sensitive values. If delivery fails, show a
general error and the approved phone and email alternatives without exposing
technical or credential details.

Staging uses a safe test recipient or disables external delivery. Production
delivery is not enabled until a controlled end-to-end test reaches Melanie's
mailbox and a reply route is verified.

## Technical architecture

The public pages are standards-based HTML with shared CSS and minimal
progressive-enhancement JavaScript. The enquiry handler is the only required
server-side application component. The implementation plan must select a
maintained mail library and lock its version rather than implementing SMTP
protocol handling from scratch.

Recommended source boundaries:

- `site/` for public pages and supporting files;
- `site/assets/css/` for shared styles;
- `site/assets/js/` for navigation and form enhancements;
- `site/assets/images/` for approved web assets;
- `site/api/` for the enquiry handler; and
- configuration and secrets outside `site/` and outside version control.

No CMS, analytics, advertising, non-essential cookies, online payments,
calendar integration, account system or clinical-data store is introduced.
Each would require a new approved requirement.

## Search and sharing

Each page has a unique title and description using the formal written name
`Stronger at Home Physiotherapy`. Accessible text, ordinary prose, metadata
and structured data spell out `at`; `Stronger@Home` remains the visual
wordmark only.

The implementation includes canonical production URLs, social-sharing
metadata, an XML sitemap and local-business structured data limited to
approved facts. Staging must be excluded from search indexing. No unsupported
service locations, credentials, reviews or outcome claims may be added for
search optimisation.

## Security and privacy boundary

- Enforce HTTPS and redirect production `www` and bare-domain traffic to one
  canonical host.
- Apply restrictive security headers compatible with the static site and form.
- Validate all input on the server and encode all reflected values.
- Use same-origin submission checks, a non-visible honeypot and bounded rate
  limiting without introducing inaccessible challenge puzzles.
- Keep secrets and writable operational data outside the public document root.
- Do not expose stack traces or mail-provider responses to visitors.
- Publish the approved privacy notice before enabling the production form.

This specification defines implementation safeguards, not legal advice. The
privacy notice, retention wording and controller details require explicit
approval before production publication.

## Deployment and review

1. Build and test locally without real patient submissions.
2. Deploy to `staging.stronger-at-home.co.uk` with search indexing disabled
   and test-only form delivery.
3. Review every page on mobile and desktop, replace the portrait placeholder,
   and confirm all public facts and legal notices.
4. Verify form delivery, failure behaviour, redirects, security headers and
   HTTPS on staging.
5. Obtain Melanie Watsham's explicit approval of the complete production
   composition and content.
6. Deploy the approved build to `stronger-at-home.co.uk`, run production smoke
   tests and only then remove the website-publication gate.

Production and staging remain separate document roots. Deployment must be
reversible and must not alter the external Titan mailbox or authoritative DNS
records without a separately approved operational change.

## Verification criteria

Before production approval, verify:

- every navigation route, footer link, image and canonical URL;
- responsive layouts at representative phone, tablet and desktop widths;
- keyboard-only navigation, focus order, screen-reader names and zoom/reflow;
- WCAG 2.2 AA contrast and accessible form errors;
- client-side and server-side form validation;
- spam controls and bounded rate limiting;
- success, invalid-input, mail-failure and duplicate-submit paths;
- test enquiry delivery without leaking personal data into logs;
- correct sole-trader identity and approved contact details;
- absence of unverified credentials, guaranteed outcomes, payment timing and
  bank-account details;
- HTTPS, host redirects, 404 behaviour, security headers, sitemap and staging
  no-index controls; and
- no generated, redrawn or altered version of the approved logo.

## Deferred decisions and dependencies

- Exact HCPC, CSP, AGILE and ATOCP wording and evidence.
- Referral suitability, exclusions and medical escalation language.
- Final professional portrait of Melanie.
- Approved privacy-notice and retention wording.
- Deployment-time mail transport credentials and safe staging recipient.

These items do not block local implementation or staging review when the
relevant feature is visibly labelled, disabled or omitted. They do block the
affected content or functionality from production publication.
