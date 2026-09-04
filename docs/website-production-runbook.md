# Guarded Git production deployment runbook

## Authority boundary and publication gates

This runbook is for the first and later production publications from the
generated `deploy-production` branch. It grants no authority by itself. Before
any production mutation, require all of the following recorded gates:

- accepted staging for the source being promoted;
- green `main` after an approved pull request containing only the accepted
  source and explicitly approved publication changes;
- a successful production release workflow with GitHub production approval by
  the required reviewer and no self-approval;
- the final portrait supplied, reviewed, and approved for publication;
- final privacy approval for the published notice and enquiry handling;
- completion of the ICO data protection fee self-assessment and any required
  sole-trader registration;
- an owner-only production configuration verified without exposing values;
- live-recipient confirmation that the sole recipient is exactly
  `melanie@stronger-at-home.co.uk`;
- no staging directives in the artifact; and
- explicit first-publication approval for the exact GitHub deployment commit,
  cPanel repository, document root, and public hostname.

If any gate is missing, stale, or ambiguous, stop. A generated artifact, cPanel
mapping, dry run, or prior staging approval does not imply production approval.
Do not change DNS, mailbox settings, or staging as part of this procedure.

- Source branch: `main`
- Generated deployment branch: `deploy-production`
- Canonical host: `stronger-at-home.co.uk`
- Canonical URL: `https://stronger-at-home.co.uk`
- Allowed redirecting host: `www.stronger-at-home.co.uk`
- Repository root:
  `/home/v0398ees6dry/repositories/stronger-at-home-production`
- Document root:
  `/home/v0398ees6dry/public_html/stronger-at-home.co.uk`
- External configuration:
  `/home/v0398ees6dry/private/stronger-at-home/production/site.php`
- Required cPanel runtime: PHP 8.4
- Guarded profile: `test-123reg`
- Protected audit file: `/private/tmp/sah-cpanel-audit.jsonl`

Never edit `deploy-production`, the cPanel checkout, or the live document root
by hand.

## 1. Verify the approved production artifact

In GitHub, open the exact `deploy-production` tip produced by the approved
production workflow. Read `release.json` directly from that commit and record
the deployment commit identifier. Require:

- `environment` is `production`;
- `sourceBranch` is `main`;
- `sourceSha` equals the approved green `main` commit;
- `deploymentBranch` is `deploy-production`;
- `hostname` is `stronger-at-home.co.uk`; and
- `buildTimestamp` is the expected UTC build time.

Require the branch tree to contain only `.cpanel.yml`, `deploy.sh`,
`release.json`, `public/`, and `vendor/`. Inspect the complete artifact and stop
unless there are no staging directives in the artifact: no staging hostname,
staging configuration or release path, deny-all robots replacement, or
`X-Robots-Tag: noindex, nofollow` directive. Require the final portrait and
approved privacy content to be present. Stop if a secret, external
configuration, test, source-only file, or development dependency is present.

Record this protected source definition in an owner-readable operator file
outside Git and outside public directories:

```json
{
  "url": "git@github.com:mwatsham/stronger-at-home.git",
  "branch": "deploy-production"
}
```

This definition records the approved remote and branch; the reviewed CLI uses
a separate operation-specific update descriptor. Create owner-readable
`/exact/operator/path/stronger-at-home-production-update.json` containing:

```json
{"remote_name": "origin"}
```

Set both operator files to mode `0600`. Neither file may contain a repository
credential, deploy key, token, or private key. cPanel must already have a
provider-supported read-only repository credential.

## 2. Verify the production configuration and runtime

The file
`/home/v0398ees6dry/private/stronger-at-home/production/site.php` must already
be outside the document root, owned only by the cPanel account, mode `0600`, and
not a symlink. The production private and rate-limit directories must be
owner-only and not symlinks. Never print, log, commit, or screenshot values.

An authorised operator must verify without revealing values that:

- `environment` is exactly `production`;
- `allowed_origin` is exactly `https://stronger-at-home.co.uk`;
- the sole recipient is exactly `melanie@stronger-at-home.co.uk`;
- GoDaddy cPanel relay settings are `localhost`, port `25`, authentication
  disabled and encryption `none`; SMTP credentials are not required or used;
- a strong production-only rate-limit secret is configured; and
- `rate_limit_directory` is
  `/home/v0398ees6dry/private/stronger-at-home/production/rate-limit`.

This live-recipient confirmation is a hard gate. Stop if there is any second
recipient, staging recipient, forwarding ambiguity, or unverified SMTP route.
The production artifact's `.htaccess` must bind `STRONGER_HOME_CONFIG` to the
exact production file and `STRONGER_HOME_AUTOLOAD` to the source-SHA release
directory under
`/home/v0398ees6dry/stronger-at-home-releases/production/`. Do not add a
fallback or override either generated binding.

Run these read-only preflight commands:

```bash
cpanel-admin profiles show test-123reg
cpanel-admin --profile test-123reg domains inspect --domain stronger-at-home.co.uk
cpanel-admin --profile test-123reg diagnostics has-feature --name lvephpsel
cpanel-admin --profile test-123reg diagnostics has-feature --name ea-php84
cpanel-admin --profile test-123reg diagnostics quota
cpanel-admin --profile test-123reg --audit-file /private/tmp/sah-cpanel-audit.jsonl --pretty runtime version-control
cpanel-admin --profile test-123reg --audit-file /private/tmp/sah-cpanel-audit.jsonl --pretty runtime deployments
```

Require account user `v0398ees6dry`, the exact production host and document
root, sufficient storage and inodes, exactly one Stronger@Home production
mapping at the repository root above, remote `origin`, and branch
`deploy-production`. The staging mapping must remain unchanged. Stop for any
path conflict, unexpected mapping, active deployment task, or nonzero command
exit.

Do not run `runtime php-*` for this account because MultiPHP support is disabled.
An authorised human must use **Software > Select PHP Version** without making a
change and record PHP 8.4 and `display_errors` **Off**. Do not use MultiPHP
Manager. Browser automation is not permitted for cPanel checks.

## 3. Review and execute `runtime git-update`

Reconfirm every publication gate and the unchanged GitHub deployment commit
immediately before this mutation. Dry-run the exact update:

```bash
cpanel-admin --profile test-123reg \
  --audit-file /private/tmp/sah-cpanel-audit.jsonl --pretty \
  runtime git-update \
  --repository-root /home/v0398ees6dry/repositories/stronger-at-home-production \
  --name stronger-at-home-production \
  --branch deploy-production \
  --source-repository /exact/operator/path/stronger-at-home-production-update.json \
  --dry-run
```

Review the normalized profile, exact repository root, name, branch, update
descriptor fingerprint, impact, recovery, digest, and expiry. Stop on any
difference. Obtain explicit production approval for this exact plan, then
repeat the identical command with `--dry-run` replaced by its returned,
unexpired `--confirm DIGEST --expires-at TIMESTAMP`. Any parameter, descriptor,
preflight state, approval, or branch-tip change requires a new dry run.

After a zero exit, run `runtime version-control` again. Require the exact
repository mapping, branch `deploy-production`, and checked-out identifier to
equal the GitHub deployment commit reviewed in section 1. Stop before
deployment for an absent, stale, or different identifier.

## 4. Review and execute `runtime deployment-create`

Run `runtime deployments` and require no active task for the production
repository. Prepare a separate deployment mutation:

```bash
cpanel-admin --profile test-123reg \
  --audit-file /private/tmp/sah-cpanel-audit.jsonl --pretty \
  runtime deployment-create \
  --repository-root /home/v0398ees6dry/repositories/stronger-at-home-production \
  --dry-run
```

Review the exact repository root, impact, recovery, digest, and expiry. Obtain
separate explicit production approval, then repeat the identical command with
`--dry-run` replaced by this plan's own unexpired
`--confirm DIGEST --expires-at TIMESTAMP`. Never reuse the git-update digest.

Poll only the status read and never start a second task while one is active:

```bash
cpanel-admin --profile test-123reg \
  --audit-file /private/tmp/sah-cpanel-audit.jsonl --pretty \
  runtime deployments
```

Require the new task's deployment status to be successful for the exact
repository root and record its deployment ID. A successful task is not public
acceptance. In File Manager, read only
`/home/v0398ees6dry/stronger-at-home-releases/production/<sourceSha>/deployed-source-sha`
and require its one 40-character value to equal `release.json`'s `sourceSha`.
Stop and begin rollback on any task failure, missing marker, or mismatch.

The generated script preserves the previous public tree inside the new release
directory and restores it automatically if the atomic public-tree swap fails.
Do not manually rename, copy, patch, or delete a production tree.

## 5. Production smoke and security checks

Stop and begin rollback on the first failed check. Keep patient and health data
out of all tests and evidence.

- Request `https://stronger-at-home.co.uk` and require valid HTTPS, status 200,
  no mixed content, and the exact canonical URL on every production page.
- Request `https://www.stronger-at-home.co.uk` and representative paths. Require
  a permanent redirect to the equivalent bare canonical HTTPS URL without a
  loop or path loss. Reject every unapproved host.
- Require the absence of `noindex`: no `X-Robots-Tag` noindex response header,
  no robots meta noindex, and no deny-all robots replacement. Require
  `/robots.txt` to allow crawling and name only the production sitemap.
- Require `X-Content-Type-Options: nosniff`,
  `Referrer-Policy: strict-origin-when-cross-origin`, the approved
  `Permissions-Policy`, and the approved Content Security Policy.
- Check all routes and assets: Home, About Melanie, How I can help,
  Appointments and fees, Contact, Privacy, Accessibility, styles, scripts,
  images, sitemap, robots, and an unknown URL. Require correct navigation, no
  missing asset, and the custom 404 response.
- Prove the external configuration and vendor paths are inaccessible. Request
  `/vendor/autoload.php`, `/.git/`, `/.cpanel.yml`, `/release.json`,
  `/deploy.sh`, and the external configuration path translated under each
  public host. Require no private content, deployment metadata, or directory
  listing.
- At 390×844, 768×1024, and 1440×1000, require readable layout, the approved
  final portrait, no overflow, complete keyboard navigation, visible focus,
  correct mobile disclosure state, and 200% reflow without loss or
  two-dimensional scrolling. Check reduced-motion behavior and record the
  available test coverage accurately.
- Verify generic failure behaviour with invalid and CSRF-invalid synthetic form
  submissions. Require field-level or generic failure feedback as appropriate,
  no mail delivery, no submitted values in the URL or status, no provider
  detail, no stack trace, and no credential or private path. Verify the
  honeypot's silent no-delivery behavior. Do not deliberately break live SMTP or
  consume the production rate limit without separate authority.

## 6. One authorised live-recipient message

This test requires separate, explicit authority after sections 1–5 pass. Send
one explicitly authorised message to Melanie using fictitious contact details
and a short message containing no health, patient, or other private information.
The sole destination must be `melanie@stronger-at-home.co.uk`.

Require the generic success response to mean only that the request was received.
Verify exactly one message with the approved subject, from, reply-to, and body
rendering. Confirm that no credential, token, provider debug output, application
path, or submitted private detail leaks. Record only UTC time, authorisation,
recipient label, source SHA, deployment ID, and pass/fail; do not copy the
message body or address into deployment logs.

## 7. Rollback verification

This rollback verification is required before the restored release is accepted.
Rollback immediately for a wrong target or identifier, failed deployment task,
failed canonical HTTPS behavior, any production noindex control, missing route
or asset, exposed private content, missing final content, accessibility failure,
unexpected recipient, form-security failure, duplicate delivery, or any other
smoke-check failure. Record the incident and stop further publication.

Rollback is a new audited deployment:

1. Identify the last accepted source SHA from the recorded `release.json` and
   source history.
2. Prepare and approve a new source commit on `main` that reverts the fault or
   restores the last accepted source state; do not rewrite history.
3. Run all production publication gates and the GitHub production approval so
   the workflow creates a regenerated `deploy-production` commit.
4. Review its `release.json`, production-only tree, and publication approvals.
5. Perform a new reviewed `runtime git-update` with a fresh dry run and explicit
   approval, then verify the checked-out identifier.
6. Perform a new reviewed `runtime deployment-create` with its own fresh dry run
   and approval, then verify task success and `deployed-source-sha`.
7. Repeat the complete production smoke checks and, only with fresh authority,
   the one-message verification before recording rollback acceptance.

`runtime git-delete`, `runtime deployment-delete`, and deleting document-root
files are not rollback mechanisms. Never patch the live tree or force-push a
source or deployment branch. Preserve non-sensitive failure evidence and keep
production unavailable rather than improvising if recovery cannot be proved.
