# Deployment-safe staging password protection

## Scope and selected approach

Protect staging.stronger-at-home.co.uk with HTTP Basic authentication over HTTPS, using Melanie's existing cPanel Directory Privacy account. Production, PHP, mail routing and enquiry handling must remain unchanged. Passwords and password hashes must never enter Git, build artifacts or chat.

The owner selected password protection instead of temporary invitation links. A one-off cPanel toggle is insufficient because deployment atomically replaces the public directory. The proposed durable implementation generates staging-only Apache authentication directives in every release, referencing the verified external cPanel password file. Do not copy arbitrary existing .htaccess content or credentials into releases.

## Required behaviour

- Protect pages, assets and enquiry endpoints before application processing; no enquiry submissions during testing.
- Keep staging noindex controls. Ensure HTTPS before allowing credential use; verify plain HTTP does not serve protected content or invite insecure credential entry.
- Use the exact verified cPanel account spelling and external password-file path, not an inferred path. Permit only the authorised staging account(s).
- Validate the password file is nonempty, readable, regular and not a symlink before deployment swaps the public tree. Missing prerequisites abort deployment without replacing the current site.
- Keep authentication mandatory in staging artifacts and absent from production artifacts, tested independently in both publication modes.
- Handle authentication failures without recursive error pages or private-path disclosure.
- Retain password protection through subsequent staging releases and rollback; never restore an old unprotected artifact directly.

## Verification and release

Tests must cover environment separation, missing/empty/symlink credential files, protection present before atomic swap, and preservation of existing deployment safeguards. Hosting acceptance requires unauthenticated HTTPS requests to pages/assets/API to be denied, authenticated browser access verified by the owner, and public production access unaffected. Test a subsequent staging deployment to prove persistence.

## Resolved prerequisite discrepancy — 8 November 2026

The owner reports melanie in Authorised Users for the staging root. Supported cPanel reads still report no users and no protection at that root. The corresponding private password directory exists, but its listing is empty and neither passwd nor .htpasswd was found. A public subdirectory named melanie is also present; this is not proof of an authentication account. No password/hash was read and no hosting changes were made. Resolve the discrepancy before setting the credential path or activating protection. Do not recreate, reset or remove the owner's account or directory speculatively.

Later verification resolved this discrepancy: the earlier account was a Web Disk subaccount. The owner disabled Web Disk and created the Directory Privacy user. cPanel now returns exactly `melanie`, Basic protection enabled, and password file `/home/v0398ees6dry/.htpasswds/public_html/staging.stronger-at-home.co.uk/passwd`. Metadata confirms a nonempty regular file; its contents were not read. Anonymous staging home/contact/CSS return 401 with an authentication challenge; equivalent production requests return 200 with no challenge. Production remains unchanged. The generated releases must preserve this verified protection.
