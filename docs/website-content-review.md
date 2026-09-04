# Website content and release review

Review date: 2026-09-04

Review scope: the exact local staging candidate; no staging or production mutation

Human approval status: not signed off

This checklist is the human approval boundary for the website. Automated and
browser evidence can support the decision, but does not check any approval box
or authorise publication.

## Exact public source and asset boundary

- [ ] Approve the complete 31-file `site/` tree fingerprinted by
  `APPROVED_PUBLIC_SOURCE_SHA256` in `scripts/validate_site.py`. An added,
  removed, renamed or byte-changed public file requires review and makes the
  validator fail.
- [ ] Approve the deployment mapping: the approved 31-file `site/` source tree
  becomes 31 files under `public/`; the source-only `site/robots-staging.txt`
  supplies staging `public/robots.txt` but is never shipped by name, while the
  approved `site/404.html` bytes are also packaged as cPanel's `public/404.shtml`
  compatibility name. The approved 84-file, fingerprinted production-only Composer
  tree becomes sibling `vendor/`, for 115 package entries in either environment.
  An added, missing or byte-changed dependency file makes packaging fail.
  Repository history, tests, caches, local configuration and secret material
  are outside this boundary.
- [ ] Approve the public logo as the exact approved raster asset copied to
  `site/assets/images/stronger-at-home-logo.png`; no active SVG logo derivative
  is present.
- [ ] Approve the two bundled font files, their two exact SIL Open Font License
  text files, generated brand-token stylesheet, site stylesheet and site script
  under `site/assets/` as the complete public front-end asset set.
- [ ] Confirm that `site/assets/images/portrait-placeholder.svg` is visibly
  labelled `Professional portrait to be supplied`, is non-final, and remains a
  production blocker.
- [ ] Confirm that staging replaces `public/robots.txt` with the exact deny-all
  content `User-agent: *` followed by `Disallow: /`, and adds the staging-only
  response header `X-Robots-Tag: noindex, nofollow` without changing the
  production `.htaccess` source.

## Shared identity, contact and appointment facts

- [ ] The public name is `Stronger at Home Physiotherapy`; `Stronger@Home` is
  confined to the approved raster wordmark and ordinary text spells out `at`.
- [ ] The sole-trader identity is exactly `Melanie Watsham trading as Stronger
  at Home Physiotherapy`, with no implication that the business is incorporated.
- [ ] The public telephone number is `+447843497871` and the public email is
  `melanie@stronger-at-home.co.uk`; email is the preferred contact route.
- [ ] The address is `11 Mospey Crescent, Epsom, Surrey, KT17 4LZ`; the website
  identity is `stronger-at-home.co.uk`, with the `www` host redirected to the
  canonical host.
- [ ] The audience is adults receiving personal physiotherapy visits at home in
  Epsom and surrounding areas.
- [ ] The approved experience claim is `20+ years of NHS experience`.
- [ ] The service area is approximately 10 miles around Epsom and surrounding
  areas, with availability confirmed using the patient's address.
- [ ] Initial assessments last 60 minutes and follow-up appointments last 45
  minutes.
- [ ] Appointments are arranged flexibly and remain subject to availability.
- [ ] Fees are quoted individually because travel requirements vary by
  location; the patient provides a postcode or address and a fixed price is
  confirmed and agreed before the appointment is booked.
- [ ] `Request an appointment` means an enquiry only: submission records that
  the request was received, then Melanie contacts the person to discuss
  availability. The form itself creates no appointment and gives no booking
  confirmation.

## Page-by-page content

### Home — `/`

- [ ] The opening promise is patient-focused, presents personal adult home
  visits and makes `Request an appointment` the primary action.
- [ ] The supported areas are recovery after surgery, hospital admission or a
  fall; decline in mobility or physical function; falls prevention; and work on
  mobility, balance and confidence.
- [ ] The home-visit benefits are described as a personal visit, a familiar
  setting and practical support relevant to daily life.
- [ ] Melanie's introduction uses only the approved experience and approach
  wording; the portrait remains the clearly labelled non-final asset.
- [ ] Appointment lengths, service area, individual quotation wording and
  request meaning match the shared facts above.
- [ ] LocalBusiness structured data contains only the approved name, canonical
  URL, telephone, email, address and service-area facts.

### About Melanie — `/about/`

- [ ] The page presents personal adult home visits, the approved NHS experience
  claim and a calm, practical approach focused on movement, mobility, balance
  and confidence in everyday life.
- [ ] The call to action remains a request whose availability Melanie confirms
  directly.

### How I can help — `/how-i-can-help/`

- [ ] The five areas are recovery after surgery, rehabilitation following
  hospital admission, rehabilitation following a fall, falls prevention, and
  mobility/balance support where mobility or physical function has declined.
- [ ] The wording describes support rather than eligibility, guaranteed
  outcomes or clinical promises.

### Appointments and fees — `/appointments-and-fees/`

- [ ] The page states flexible availability, 60-minute initial assessments and
  45-minute follow-ups.
- [ ] The service-area, address-confirmation, individual quotation and agreed
  fixed-price wording match the shared facts above.
- [ ] The page does not present a standard public price list.

### Contact — `/contact/`

- [ ] The approved telephone and email routes appear before the enquiry form.
- [ ] The form asks only for name, email, phone, preferred contact route,
  postcode, short enquiry, privacy acknowledgement, anti-spam field and
  security token.
- [ ] Name, postcode, short enquiry and privacy acknowledgement are required;
  at least one of email or phone is required and must match the selected
  contact route.
- [ ] The page asks for no detailed or urgent medical information, date of
  birth, medical records or attachment.
- [ ] Validation, rate-limit and delivery states reveal no submitted enquiry or
  provider detail, and the success state preserves the exact request meaning.

### Privacy — `/privacy/`

- [x] The page identifies the exact sole-trader identity, address and email,
  explains which enquiry and security information is used, and states what is
  required to respond.
- [x] The lawful bases cover pre-contract steps, health information and the
  legitimate interest in website security. The acknowledgement checkbox is
  not presented as consent.
- [x] GoDaddy and Titan are identified as service providers, possible
  international processing is explained, and marketing, sale of information
  and automated decision-making are excluded.
- [x] Unconverted enquiries are retained for up to 12 months after last
  contact. Relevant correspondence may become part of an adult patient record,
  normally retained for eight years after last treatment.
- [x] The page explains individual rights, how to contact Melanie and the right
  to complain to the Information Commissioner's Office.
- [x] Melanie approved the independently reviewed revision on 4 September 2026.
  Its draft label and `privacy-approval` blocker have been removed.

### Accessibility — `/accessibility/`

- [ ] The target is WCAG 2.2 level AA, without claiming that every issue has
  already been found.
- [ ] Keyboard navigation, visible focus, text resizing, headings, labelled
  controls and small-screen reflow are described, with the approved email route
  for reporting a problem.

### Error page — `/404.html`

- [ ] The page is marked `noindex`, states that the page was not found and gives
  a route back to the homepage.

## Required omissions and publication gates

- [ ] HCPC, CSP, AGILE and ATOCP wording remains absent until separately
  verified and approved.
- [ ] Referral, eligibility, suitability, exclusion and restriction claims are
  absent from the public copy.
- [ ] Registered-mark symbols or claims, outcome guarantees, testimonials,
  emergency-service claims, unsupported locations, and walk-in or clinic
  wording are absent.
- [ ] No CMS, analytics, advertising, non-essential cookies, calendar
  integration, account system or clinical-data store has been introduced.
- [ ] The final professional photograph of Melanie has replaced the labelled
  placeholder and the `portrait` blocker has been removed before production.
- [x] Melanie has approved the final privacy wording and the
  `privacy-approval` blocker has been removed before production.
- [ ] Melanie has completed the ICO data protection fee self-assessment and,
  if required, the sole-trader registration is active before patient records
  are processed electronically.
- [ ] Production validation reports no blockers before any production package
  or deployment is authorised.

## Local browser review evidence

The visual review uses the in-app browser against a loopback PHP server. Every
primary page is captured at 390×844, 768×1024 and 1440×1000. Evidence is stored
under `output/review/website-task-8/`, outside source control.

| Check | Result | Evidence |
|---|---|---|
| Fifteen primary-page viewport captures | Pass | Full-page files listed below |
| Mobile menu pointer disclosure | Pass | `mobile-menu-open-390x844.jpg` |
| Keyboard-only order and activation | Pass | Main-session key sequence and resulting menu states recorded below |
| Visible focus treatment | Pass | Menu capture and `contact-field-errors-390x844.jpg` |
| Contact field errors | Pass | Status, five invalid controls and native feedback observed |
| 200% reflow | Pass | Native browser UI reported 200%; DPR and scroll metrics recorded below |
| Horizontal overflow | Pass | Document and body widths equal client width in all 15 required captures and five reflow checks |
| Reduced-motion behaviour | Partial | Live rule and zero inline animated elements verified; active emulation unavailable |
| Portrait placeholder is visibly non-final | Pass | All three homepage captures |
| Console warnings and errors | Pass | No warning/error entries after the review route set |

### Required viewport captures

- 390×844: `home-390x844.jpg`, `about-390x844.jpg`,
  `how-i-can-help-390x844.jpg`, `appointments-and-fees-390x844.jpg`,
  `contact-390x844.jpg`.
- 768×1024: `home-768x1024.jpg`, `about-768x1024.jpg`,
  `how-i-can-help-768x1024.jpg`, `appointments-and-fees-768x1024.jpg`,
  `contact-768x1024.jpg`.
- 1440×1000: `home-1440x1000.jpg`, `about-1440x1000.jpg`,
  `how-i-can-help-1440x1000.jpg`, `appointments-and-fees-1440x1000.jpg`,
  `contact-1440x1000.jpg`.

Each path is relative to `output/review/website-task-8/`. At the three required
sizes the browser reported client widths of 375, 753 and 1425 CSS pixels after
the vertical scrollbar; `documentElement.scrollWidth` and `body.scrollWidth`
matched the client width for every page.

### Interaction and reflow record

- At 390×844 the menu began with `aria-expanded="false"` and hidden primary
  navigation. Pointer activation changed it to `aria-expanded="true"` and made
  the primary navigation visible. The capture shows the disclosed links and a
  three-pixel, two-colour focus treatment on the menu control.
- Submitting the empty contact form was stopped in the browser. Focus moved to
  `name`; the live status read `Please check the highlighted fields before
  sending your appointment request.`; and `name`, `email`, `postcode`,
  `message` and `privacy-acknowledged` carried `aria-invalid="true"`. The page
  retained zero horizontal overflow.
- At 390×844, keyboard Tab focus progressed from the skip link to the home logo
  and then the collapsed Menu control. Return changed the control to expanded
  and exposed the navigation links. Space collapsed it again while focus
  remained on the control.
- In the main controlled browser session, native Chrome UI reported `Zoom:
  200%`. At that state `devicePixelRatio` was 2, `innerWidth` was 839, and the
  root and body scroll widths were both 832; horizontal overflow was false.
  Zoom was reset to 100% after the check. Supplementary layout-equivalent
  720×500 captures remain at
  `home-200-percent-reflow-equivalent-720x500.jpg` and
  `contact-200-percent-reflow-equivalent-720x500.jpg`.
- The loaded CSSOM contains
  `@media (prefers-reduced-motion: reduce)` with `scroll-behavior: auto` and a
  `0.01ms` transition duration. The live page also reported zero inline
  animated elements. The current operating-system preference was `false`, and
  neither exposed browser-control surface offered reduced-motion emulation, so
  active reduced-motion behaviour is not claimed. This tooling limitation and
  the verified static safeguards are recorded separately rather than
  presenting an emulated result.

## Human sign-off

- [ ] Project sponsor content and staging-review sign-off

  Name: ____________________  Date: ____________________

- [ ] Melanie Watsham final content, portrait and privacy sign-off

  Signature/name: ____________________  Date: ____________________

Neither line is signed. Production remains unauthorised.
