# Warm editorial refinement

User selected direction 2 and explicitly requested implementation without mockups or further design questions on 24 October 2026.

## Intent
Keep the personal, credible existing brand while making the appointment journey easier to find and use for adult patients and carers.

## Approaches
Considered a minimal spacing tidy-up, warm editorial refinement, and a compact clinical redesign. The user chose warm editorial refinement: a stronger hierarchy and balanced layouts without replacing the identity.

## Scope and decisions
- Preserve exact raster logo, portrait, palette, typefaces and verified service copy; no new claims or clinical advice.
- Tighten shared header and hero whitespace while retaining the prominent logo and centred narrow-screen identity. At 1280×720 the homepage hero appointment action and initial reassurance should be visible without scrolling.
- Use a restrained inner-page heading scale and consistent editorial rhythm, cards and button treatment across existing pages.
- Balance the contact page with a centred readable-width form, not an invented content sidebar.
- Keep /contact/#appointment-request working but make arrival include its heading and introductory context. Update JS form lookup if the fragment target moves to the section.
- Preserve form fields, validation, CSRF, consent/privacy wording, SMTP and submission behaviour. No real form submissions.
- Keep the HTML/PHP/CSS architecture; no dependencies, framework rebuild, new images or font assets.

## Verification
Responsive checks at 320, 375, 768, 1024 and 1280 pixels; keyboard focus and no-JS navigation; 200% zoom/reflow; anchor heading visibility. Retain 44px controls and avoid horizontal overflow. Run existing Python and PHP suites and targeted browser regression tests. Update only intentional public-file approval hashes; unchanged image hashes remain pinned.

## Release boundary
Local implementation and preview only. No merge, push, staging or production deployment. Preserve unrelated staged AGENTS.md and untracked user files.
