# Guarded Git staging deployment runbook

## Authority boundary

This runbook activates an already reviewed `deploy-staging` commit in the
individual cPanel account. It does not authorise a mutation by itself and never
authorises production. Stop before each cPanel mutation until the project
sponsor approves its exact dry-run plan. Do not change DNS, mailbox settings,
the production repository, the production document root, or any production
file.

- Source branch: `develop`
- Generated deployment branch: `deploy-staging`
- Target host: `staging.stronger-at-home.co.uk`
- Repository root:
  `/home/v0398ees6dry/repositories/stronger-at-home-staging`
- Document root:
  `/home/v0398ees6dry/public_html/staging.stronger-at-home.co.uk`
- External configuration:
  `/home/v0398ees6dry/private/stronger-at-home/staging/site.php`
- Required cPanel runtime: PHP 8.4
- Guarded profile: `test-123reg`
- Protected audit file: `/private/tmp/sah-cpanel-audit.jsonl`

The generated deployment branch is the only deployable input. Do not edit it,
the cPanel checkout, or the document root by hand. The previously published
manual package stays live until a Git deployment succeeds and all staging
checks pass.

## 1. Verify the reviewed deployment commit

In GitHub, open the exact `deploy-staging` tip produced from the accepted
`develop` commit. Read `release.json` directly from that commit and record the
deployment commit identifier and these required values:

- `environment` is `staging`;
- `sourceBranch` is `develop`;
- `sourceSha` equals the accepted `develop` commit;
- `deploymentBranch` is `deploy-staging`;
- `hostname` is `staging.stronger-at-home.co.uk`; and
- `buildTimestamp` is the expected UTC build time.

Require the branch tree to contain only `.cpanel.yml`, `deploy.sh`,
`release.json`, `public/`, and `vendor/`. Stop if the source SHA is unexpected,
the branch moved during review, a secret or private configuration is present,
or the artifact contains any production environment binding.

Record this protected source definition in an owner-readable operator file
outside Git and outside any public directory:

```json
{
  "url": "git@github.com:mwatsham/stronger-at-home.git",
  "branch": "deploy-staging"
}
```

This definition records the approved remote and branch; it is not the update
descriptor accepted by the reviewed CLI. Create a separate owner-readable
`/exact/operator/path/stronger-at-home-staging-update.json` containing exactly:

```json
{"remote_name": "origin"}
```

Set both operator files to mode `0600`. Do not put a repository credential,
deploy key, token, or private key in either file. cPanel repository access must
already be configured through its provider-supported read-only credential.

## 2. Read-only cPanel preflight

Use only the named individual-account profile over verified TLS on cPanel port
2083. These commands are reads and do not approve either later mutation:

```bash
cpanel-admin profiles show test-123reg
cpanel-admin --profile test-123reg domains inspect --domain staging.stronger-at-home.co.uk
cpanel-admin --profile test-123reg diagnostics has-feature --name lvephpsel
cpanel-admin --profile test-123reg diagnostics has-feature --name ea-php84
cpanel-admin --profile test-123reg diagnostics has-feature --name multiphp
cpanel-admin --profile test-123reg diagnostics has-feature --name multiphp_ini_editor
cpanel-admin --profile test-123reg diagnostics has-feature --name filemanager
cpanel-admin --profile test-123reg diagnostics has-feature --name backup
cpanel-admin --profile test-123reg diagnostics quota
cpanel-admin --profile test-123reg --audit-file /private/tmp/sah-cpanel-audit.jsonl --pretty runtime version-control
cpanel-admin --profile test-123reg --audit-file /private/tmp/sah-cpanel-audit.jsonl --pretty runtime deployments
```

Require account user `v0398ees6dry`, the exact host and document root above,
sufficient storage and inodes, exactly one Stronger@Home staging mapping at the
exact repository root, remote `origin`, and branch `deploy-staging`. Stop for a
path conflict, unexpected mapping, changed branch or remote, an active
deployment task, or any nonzero command exit. Do not expose profile data or
credentials in the deployment record.

Do not run `runtime php-*` for this account: those reads require the disabled
MultiPHP or MultiPHP INI Editor capabilities. Do not use `files inspect` or
`files list` for the target: their current audit adapter rejects this path.
Those known failures are not runtime or target evidence.

An authorised human must use the enabled cPanel interfaces without changing
anything: open **Software > Select PHP Version** (CloudLinux PHP Selector) and
record that the current account runtime is PHP 8.4. In its **Options** view,
record that `display_errors` is **Off**. Then open **File Manager** only to
record current metadata for the exact staging document root and existing
external configuration; do not change either. Do not use MultiPHP Manager.
Stop if Select PHP Version is absent, does not show 8.4, cannot be shown to
govern the staging host, or shows `display_errors` On. Browser automation is not
permitted for these cPanel checks.

## 3. Verify the external staging configuration

The file
`/home/v0398ees6dry/private/stronger-at-home/staging/site.php` must already be
outside the document root, owned only by the cPanel account, mode `0600`, and
not a symlink. The private directory and rate-limit directory must also be
owner-only and not symlinks. Never print, log, commit, or screenshot values.

An authorised operator must verify without revealing values that:

- `environment` is exactly `staging`;
- `allowed_origin` is exactly
  `https://staging.stronger-at-home.co.uk`;
- the recipient is the sponsor-approved safe staging recipient and is not
  `melanie@stronger-at-home.co.uk`;
- authenticated SMTP settings come from the protected operator source;
- a strong independent rate-limit secret is configured; and
- `rate_limit_directory` is
  `/home/v0398ees6dry/private/stronger-at-home/staging/rate-limit`.

The staging deployment artifact's `.htaccess` must bind
`STRONGER_HOME_CONFIG` to that exact file and `STRONGER_HOME_AUTOLOAD` to the
source-SHA release directory under
`/home/v0398ees6dry/stronger-at-home-releases/staging/`. Do not add a fallback
or override either generated binding. Confirm the configuration, release,
vendor, Git metadata, and audit paths cannot be retrieved over HTTPS.

## 4. Review and execute `runtime git-update`

Re-read the recorded GitHub deployment commit immediately before the dry run.
Use the reviewed CLI update descriptor containing only `remote_name`; pass the
reviewed branch separately:

```bash
cpanel-admin --profile test-123reg \
  --audit-file /private/tmp/sah-cpanel-audit.jsonl --pretty \
  runtime git-update \
  --repository-root /home/v0398ees6dry/repositories/stronger-at-home-staging \
  --name stronger-at-home-staging \
  --branch deploy-staging \
  --source-repository /exact/operator/path/stronger-at-home-staging-update.json \
  --dry-run
```

Review the normalized profile, exact repository root, name, branch, source
descriptor fingerprint, impact, recovery, digest, and expiry. Stop if they do
not exactly match this runbook. Obtain explicit staging activation approval,
then repeat the identical command with `--dry-run` replaced by the returned,
unexpired `--confirm DIGEST --expires-at TIMESTAMP`. Never reuse a digest or
execute after any parameter, descriptor, preflight state, or branch tip changes.

After a zero exit, run `runtime version-control` again. Require the exact
repository mapping, branch `deploy-staging`, and checked-out identifier to equal
the GitHub deployment commit reviewed in section 1. Stop before deployment if
the identifier is absent, stale, or different.

## 5. Review and execute `runtime deployment-create`

Run `runtime deployments` and require no active task for this repository. Then
prepare the separate deployment mutation:

```bash
cpanel-admin --profile test-123reg \
  --audit-file /private/tmp/sah-cpanel-audit.jsonl --pretty \
  runtime deployment-create \
  --repository-root /home/v0398ees6dry/repositories/stronger-at-home-staging \
  --dry-run
```

Review the exact repository root, impact, recovery, digest, and expiry. Obtain
separate explicit approval, then repeat the identical command with `--dry-run`
replaced by its own unexpired `--confirm DIGEST --expires-at TIMESTAMP`. The
git-update confirmation does not authorise deployment and must never be reused.

Poll only the read command below; never start a second task while one is active:

```bash
cpanel-admin --profile test-123reg \
  --audit-file /private/tmp/sah-cpanel-audit.jsonl --pretty \
  runtime deployments
```

Require the new task's deployment status to be successful for the exact
repository root and record its deployment ID. A cPanel success is necessary but
is not acceptance. In File Manager, read only
`/home/v0398ees6dry/stronger-at-home-releases/staging/<sourceSha>/deployed-source-sha`
and require its single 40-character value to equal `release.json`'s `sourceSha`.
Do not expose the release directory publicly. Stop and begin the Git rollback
procedure for a failed task, missing marker, or mismatch.

The generated script preserves the previous public tree inside the new release
directory and restores it automatically if the atomic public-tree swap fails.
Do not manually rename, copy, patch, or delete either tree.

## 6. Staging smoke, security and accessibility checks

Stop and begin rollback on the first failed check. Use fictitious details and a
message containing no health or private information for every form test.

- Request the HTTPS homepage and require a valid certificate, no mixed content,
  status 200, the staging host, and no redirect to production.
- Request `/robots.txt` and require the exact deny-all response:

  ```text
  User-agent: *
  Disallow: /
  ```

  Confirm staging is absent from the production sitemap and each page retains
  its intended production canonical URL.
- Require `X-Robots-Tag: noindex, nofollow` exactly once on staging page
  responses. It is inserted only in the staging deployment artifact and must
  not appear in a production artifact.
- Require `X-Content-Type-Options: nosniff`,
  `Referrer-Policy: strict-origin-when-cross-origin`, the approved
  `Permissions-Policy`, and the approved Content Security Policy.
- Check all routes and assets: Home, About Melanie, How I can help,
  Appointments and fees, Contact, Privacy, Accessibility, styles, scripts,
  images, and an unknown URL. Require correct navigation, no missing asset, and
  the custom noindex 404 response.
- Request likely private paths including `/vendor/autoload.php`, `/.git/`,
  `/.cpanel.yml`, `/release.json`, `/deploy.sh`, and the external configuration
  path translated under the host. Require no private content and no directory
  listing.
- At 390×844, 768×1024, and 1440×1000, check the five primary pages for readable
  layout, no horizontal overflow, and the visibly non-final portrait label.
- Use keyboard only to expose the skip link, traverse every menu item, operate
  the mobile disclosure, and reach each form control. Require visible focus and
  accurate `aria-expanded` state.
- At 200% browser zoom, require reflow without loss, overlap, or two-dimensional
  page scrolling. With reduced motion enabled, require no meaningful animation
  or smooth scrolling.
- Submit an invalid form and require clear field-level errors without a delivery
  attempt. Require focus to move to the first invalid field; success, rate, and
  delivery feedback must focus the generic status without exposing input.
- Fill the honeypot through developer tools and require the silent anti-spam
  response with no delivery and no visible success claim.
- In an explicitly approved test window, use the reviewed safe staging recipient
  and controlled non-routable SMTP setting to require generic delivery-failure
  feedback without provider detail. Five valid failures may consume the limit;
  the sixth request from the same test address must return the generic rate
  response. Restore the reviewed configuration and clear only that exact
  staging counter after recording the result.

## 7. Controlled safe-recipient message — separate authority

Do not send merely because deployment was approved. After every preceding check
passes and the reviewed SMTP configuration is restored, obtain explicit
authority for exactly one synthetic delivery to the named safe staging
recipient. Never use Melanie's live address.

Require the generic success message to mean only that the request was received.
Verify exactly one message at the safe staging recipient and check its subject,
from, reply-to, and body rendering. Confirm no credential, security token,
provider debug output, patient detail, or private configuration appears. Record
only UTC time, a non-sensitive recipient label, and pass/fail.

## 8. Rollback verification

Rollback immediately for a wrong target or identifier, failed deployment task,
failed HTTPS or security header, indexable staging response, missing route or
asset, inaccessible navigation or form, exposed private content, unexpected
recipient, form-security failure, duplicate delivery, or any other smoke-check
failure. Production remains blocked.

Rollback is a new audited deployment:

1. Identify the last accepted source SHA from the recorded `release.json` and
   source history.
2. Revert the faulty source change or prepare a new source commit on `develop`.
3. Run the complete validation and staging build workflow so GitHub produces a
   regenerated `deploy-staging` commit. Never edit the generated branch.
4. Review its `release.json` and tree as in section 1.
5. Perform a new reviewed `runtime git-update` with a fresh dry run and approval,
   then verify the checked-out deployment identifier.
6. Perform a new reviewed `runtime deployment-create` with a separate fresh dry
   run and approval, then verify task success and `deployed-source-sha`.
7. Repeat the complete staging smoke checks, accessibility checks, and authorised
   safe-recipient verification before recording rollback acceptance.

`runtime git-delete`, `runtime deployment-delete`, and deleting document-root
files are not rollback mechanisms. Do not patch the live document root or
restore a tree by hand. Preserve non-sensitive failure evidence and keep staging
unavailable rather than improvising when recovery cannot be proved.
