# Home-visit photo crossfade

## Intent and scope
Replace the single photograph in the homepage's “Care in the place where daily life happens” section with a calm, accessible rotation of existing approved treatment photographs. Prepare a local preview only. Neither live site, deployment settings, PHP, enquiries, feedback records nor analytics settings will change.

## Approaches
Soft crossfade was selected by the owner over horizontal sliding, fading through the cream background and instant changes. It preserves the calm visual treatment and existing seamless edges without lateral movement.

## Behaviour
Show each photograph for approximately eight seconds and crossfade over one second. Keep the photograph area a fixed size so the page does not jump. Preserve the current responsive layout and seamless edges.

Use the approved seated-treatment, standing-balance and home-exercise photographs, beginning with the current seated-treatment photograph. This selection is the implementer's proposal; do not generate or alter photographs. Keep the wording and Melanie's portrait unchanged.

Owner revision after local preview: remove all controls and the counter; automatic rotation only. Temporarily suspend rotation while the pointer or keyboard focus is inside the component, while the page is hidden and while the component is off screen. The absence of an explicit pause button is an accessibility limitation; do not claim full accessibility compliance for this automatic-only presentation.

Respect reduced-motion preferences: no automatic rotation and no animated transitions; show the first photo. Do not announce automatic changes through a live region. Only the active photograph has exposed alternative text. Without JavaScript, show the first photograph. A failed image must not replace a working photograph with a blank frame.

## Implementation boundary
The release builder takes this homepage section from `design-previews/seamless-photo/index.html`, not directly from `site/index.html`. Implement the component in that composition, with small first-party JavaScript and styling compatible with the existing packaging and security checks. Preserve unrelated external-link edits already present in the worktree.

## Verification and handoff
Test timing, wrapping, manual stop/resume, temporary pause conditions, reduced motion, image failures and the static fallback. Check the generated homepage, desktop and mobile layout, keyboard controls and packaging validation. Open a local preview for owner review; do not push, merge or deploy this change.
