# Stronger at Home prominent logo integration design

Status: proposed final design for sponsor review; implementation not yet approved

Approval owner: Project sponsor for the website composition; Melanie Watsham
retains final approval of the unchanged logo artwork and public-facing wording

Prepared on: 2026-09-05

## Objective

Make the approved Stronger at Home Physiotherapy logo feel more prominent and
more deliberately integrated into the website without modifying, redrawing or
deriving new artwork from the approved raster logo.

The design must preserve the calm, accessible, patient-focused website while
making the brand identity easier to recognise and the homepage promise more
immediate.

## Context and constraints

- The approved primary website logo is the existing raster artwork at
  `site/assets/images/stronger-at-home-logo.png`, synchronised from the approved
  brand source.
- The logo artwork, geometry, colours, wording and internal spacing must remain
  unchanged.
- No SVG, transparent-background, monochrome, cropped or AI-redrawn derivative
  is part of this work.
- The logo raster background is approximately `#F9F4F2`; the main site warm
  background is `#F7F2E8`. The composition must account for that difference
  rather than exposing an accidental-looking image tile.
- The wordmark retains `Stronger@Home`. Ordinary page copy and accessible text
  continue to spell out `Stronger at Home`.
- The existing navigation structure, appointment enquiry behaviour, portrait,
  accessibility provisions and approved service content remain in scope and
  must not regress.

## Approved direction

The selected direction is **B3: compact editorial**, within the wider
**promise-led hero** approach.

This direction has three defining decisions:

1. Increase the approved logo's displayed size and give it a deliberate brand
   surface.
2. Pair the logo with a concise service-and-location strap in the identity
   header.
3. Promote the approved brand promise to the homepage's main heading.

The brand is improved through scale, spacing and integration only. Revising the
logo artwork itself is explicitly deferred.

## Site-wide identity header

Use the compact editorial identity header on every public page for consistent
brand recognition.

### Identity band

- Create a full-width identity band using `#F9F4F2`, matching the raster logo's
  own background closely enough that the logo reads as part of the surface.
- Constrain the inner content to the existing site content width.
- Place the approved logo at the left on desktop.
- Display the logo at approximately 315 CSS pixels wide on desktop, compared
  with the current approximately 256 pixels.
- Preserve the image's intrinsic aspect ratio and declared dimensions.
- Do not apply clipping, filters, blending, recolouring, masking or background
  removal.

### Service-and-location strap

Place the following two-line strap to the right of the logo on desktop:

> **Home physiotherapy for adults**
>
> Epsom and surrounding areas

The first line is the dominant line. The second line is quieter supporting
text. A restrained Warm Sand accent may separate the strap from the logo, but
the strap must not compete with the logo or resemble another call to action.

### Navigation row

- Place the primary navigation in a separate, quieter row beneath the identity
  band.
- Retain the current five navigation destinations.
- Keep `Request an appointment` as the only high-emphasis action in the header.
- Use spacing and weight to identify ordinary navigation links; remove the
  persistent heavy underlining that currently competes with the logo.
- Preserve clear link affordance through hover, focus, active-page state and
  sufficient contrast. Underlining may appear on hover or focus.
- Use a thin Warm Sand separator between the header/navigation area and page
  content to make the composition intentional.

## Homepage promise-led hero

Retain the existing two-column editorial hero and Melanie's approved portrait,
but change the content hierarchy.

### Approved opening

Use:

> Home physiotherapy in Epsom
>
> # Experienced care. Personal progress. At home.
>
> Personal physiotherapy visits for adults recovering strength, mobility,
> balance and confidence.

The three-sentence promise becomes the single homepage `h1`. It should remain
readable as three short thoughts rather than being forced into a particular
line break.

Retain the existing `Request an appointment` primary action, the quieter
`Call Melanie` action and the approved `20+ years of NHS experience` trust
point beneath the opening copy.

Do not repeat the full promise elsewhere near the hero or in the site-wide
header. The identity strap explains the service; the hero expresses the
patient-facing promise.

## Responsive behaviour

### Desktop and wider tablet

- Arrange the logo and strap as a balanced two-part identity row.
- Keep the logo visually dominant over the strap.
- Keep navigation links and the appointment action on the row below.
- Preserve the current hero's copy-and-portrait relationship.

### Narrow screens

- Centre the logo and keep it large enough for the symbol and endorsement to
  remain recognisable without causing horizontal overflow.
- Place the service-and-location strap beneath the logo.
- Retain the existing accessible menu disclosure behaviour.
- Keep `Request an appointment` easy to reach inside the disclosed navigation.
- Stack hero copy and portrait in the current accessible reading order: promise,
  explanatory copy, actions, trust point, then portrait.
- Support reflow at 320 CSS pixels and text zoom to 200 percent.

## Accessibility and semantics

- Retain the logo link's accessible name as `Stronger at Home Physiotherapy,
  home` and the image alternative as `Stronger at Home Physiotherapy by Melanie
  Watsham`.
- Keep one `h1` per page; only the homepage adopts the new promise as its `h1`.
- Keep keyboard access, visible focus indicators, minimum touch targets and the
  skip link.
- Do not rely on the Warm Sand separator alone to communicate navigation or
  structure.
- Ensure navigation link states remain distinguishable without colour alone.
- Do not place essential service information only inside the raster logo.

## Logo and wording assessment

The current logo concept remains appropriate for launch:

- the house clearly communicates care at home;
- the person and rising steps suggest mobility and progression;
- the hand conveys support;
- Navy and Warm Sand feel credible, calm and personal;
- `Stronger@Home` is memorable and aligns with the registered domain.

Its main weakness is small-size legibility, particularly the endorsement
`by Melanie Watsham`. The approved solution for this phase is a larger display
size and a calmer surrounding header, not revised artwork.

The `@` character can feel slightly digital or email-like, so prose, metadata,
accessible text and service descriptions must continue to use the written word
`at`. A future raster-only responsive lock-up could test a larger endorsement,
tighter internal spacing or a less dominant `@`, but that would be separate new
artwork requiring Melanie's explicit approval.

## Implementation boundaries

This design authorises a future implementation plan to change:

- the shared header markup on all public pages;
- site header, navigation and responsive styling;
- the homepage hero heading and supporting sentence;
- automated validation and visual regression coverage needed for these changes.

It does not authorise:

- changing the logo source or generated raster asset;
- creating SVG or other logo derivatives;
- changing appointment handling, contact details or clinical claims;
- adding credentials not already verified for publication;
- deploying directly to production.

Implementation should be reviewed locally, then on staging. Production release
remains a separate approval.

## Verification criteria

Implementation is acceptable when:

1. Every public page uses the new identity band and separate navigation row.
2. The approved raster logo bytes remain unchanged.
3. The desktop logo displays at approximately 315 CSS pixels wide and remains
   legible without dominating the navigation or page title.
4. The identity band visually absorbs the logo's raster background without an
   accidental tile edge.
5. The exact approved strap appears in the site-wide header.
6. The homepage uses the approved promise as its only `h1` and the approved
   supporting sentence immediately follows it.
7. Navigation, menu disclosure, appointment links, skip link and focus states
   continue to work by keyboard and pointer.
8. Pages reflow without clipping at 320, 360, 768, 1024 and 1280 CSS pixels and
   at 200 percent text zoom.
9. Automated site, accessibility-oriented markup and asset-integrity tests pass.
10. Staging is visually reviewed on desktop and mobile before any production
    deployment is proposed.

## Risks and trade-offs

- A larger logo makes the header taller. The 315-pixel compact editorial size
  is the approved balance between recognition and keeping the page promise near
  the top of the viewport.
- Matching the identity band to the logo raster background introduces a second
  warm neutral beside the existing site cream. The Warm Sand separator and
  deliberate full-width band make the distinction intentional.
- Removing persistent navigation underlines reduces visual competition but can
  weaken link recognition if states are not designed carefully. Spacing,
  weight, hover/focus underlines and strong focus indicators are required.
- The endorsement inside the approved raster may still be difficult to read at
  the smallest widths. The service-and-location strap and accessible text carry
  essential meaning without altering the artwork.

