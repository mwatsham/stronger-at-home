# Seamless photo staging preview

Goal: serve the user-approved soft-fade experiment at staging `/design-preview/`, based on develop 8f2dc92 with its existing password protection. Production and existing source pages remain unchanged.

Design: preserve current service copy and branding, with three borderless gradient-blended treatment placements. Keep text outside photographs, use exact section background colours, stack below 48rem, and identify AI-edited photos. Navy tunics, matching trousers and white trainers were approved. The owner explicitly approved uploading the preview code and photographs to the existing public GitHub repository.

Implementation: store the static preview outside `site/`. Add a preview-only packaging helper to the staging workflow after the existing release build. Require the generated staging authentication before copying. Reject symlinks and unexpected file types. Production workflows never invoke the helper and its production mode copies nothing. The existing release builder, hosting paths, authentication configuration and atomic deployment script remain untouched.

Verification: staging contains both preview pages and three images; production excludes the preview; symlinked source parents are rejected. Run existing source, release and PHP checks. No enquiry submissions, credential changes, production publication or security relaxation.

Deployment blocker: the guarded cPanel read cannot resolve the hosting server from this session. Upload and PR preparation can proceed; hosting activation still requires the normal guarded process once connectivity is available.
