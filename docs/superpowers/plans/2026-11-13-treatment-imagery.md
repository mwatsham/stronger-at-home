# Treatment imagery update

Goal: integrate the owner-selected seated and standing treatment photographs into the existing seamless staging layout, retaining the breathing photograph, portrait and feedback carousel.

Authority: owner approved the three placements and cPanel update on 13 November 2026. Target remains staging, as previously requested; production promotion is outside this change.

Approach: use the existing `design-previews/seamless-photo` pages and guarded release helper. The helper already applies those pages to the main staging routes. Replace the homepage exercise image with the latest seated image (bags removed, subtly warmer expression), and replace the services mat image with the standing balance image. Keep subject proportions, hands, feet and equipment visible; use existing cream/pale-blue edge fades, no frames. Static images complement the existing feedback carousel.

Implementation:
- [x] Export metadata-free 480px and 960px WebP derivatives from approved generated masters; keep masters unchanged.
- [x] Update homepage and services HTML with accurate alt text, dimensions, responsive sources and lazy loading. Adapt portrait layout without changing enquiry, security or feedback code.
- [x] Check release packaging, links, production isolation and existing feedback behavior; review the final diff.
- [ ] Upload a focused feature branch/PR, wait for CI and merge into develop within the approved staging scope.
- [ ] Verify the generated deploy-staging artifact and activate through guarded cPanel commands when connection/preflight permit. Never report deployment without successful verification.

Constraints: preserve the dirty original checkout by editing this archived source snapshot. No production workflow changes, runtime changes, authentication changes, patient outcome claims, or enquiry submissions.

Initial preflight: cPanel read returned exit 5, hostname resolution failure. Hosting activation is blocked until the supported integration can connect. Source base: `2b26e53684826a12b61455e52d5a40efcb3ac3d5`.

Validation: 35 targeted release/feedback tests passed; staging site and brand validation passed; all eight feedback-carousel JavaScript tests passed. Independent review found no further important issues after the expected mat-image assertion was updated to the selected standing image.
