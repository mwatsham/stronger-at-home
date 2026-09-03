# Reversible staging deployment runbook

## Authority boundary

This runbook prepares a cPanel-only staging release. It does not authorise a
staging mutation by itself, and it never authorises production. Stop before the
first cPanel write until the project sponsor explicitly approves the exact
archive and staging target. Do not change DNS, mailbox settings, the production
document root or any production file.

Target host: `staging.stronger-at-home.co.uk`

Exact document root: `/home/v0398ees6dry/public_html/staging.stronger-at-home.co.uk`

Required cPanel runtime: PHP 8.4

Expected archive: `output/site-package/stronger-at-home-staging.zip`

Approved SHA-256: use the exact final-commit rebuild hash in the Task 8 handoff
report. A hash from an earlier commit or rebuild does not authorise upload.

## 1. Fresh local release gate

Run from the repository root and stop on any non-zero exit:

```bash
composer install --no-dev --no-interaction --prefer-dist
for test_file in tests/php/*Test.php; do php "$test_file" || exit 1; done
for php_file in $(find site tests/php config -type f -name '*.php' | sort); do php -l "$php_file" || exit 1; done
/opt/homebrew/bin/python3 -m unittest discover -s tests -q
/opt/homebrew/bin/python3 scripts/validate_site.py --mode development
/opt/homebrew/bin/python3 scripts/validate_site.py --mode staging
/opt/homebrew/bin/python3 scripts/validate_brand.py
node --check site/assets/js/site.js
/opt/homebrew/bin/python3 scripts/package_site.py --environment staging --destination output/site-package
sha256sum output/site-package/stronger-at-home-staging.zip
```

Require all tests and validators to pass, the archive hash to equal the Task 8
handoff value, exactly 115 regular archive entries, and `public/robots.txt` to
contain:

```text
User-agent: *
Disallow: /
```

Build a second time into a fresh local destination and require identical hashes
before continuing. Inspect the archive names and stop if any root other than
`public/` or `vendor/` appears, or if configuration, a secret, a test, cache or
repository metadata is present.

## 2. Read-only cPanel preflight

Use only the named individual-account profile and cPanel HTTPS port 2083:

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
```

These exact reads were exercised against `test-123reg` on 2026-09-03. The
profile and domain reads succeeded and returned account user `v0398ees6dry`,
port 2083 and the exact document root above. The feature probes succeeded with
CloudLinux PHP Selector, PHP 8.4, File Manager and Backup enabled; MultiPHP and
MultiPHP INI Editor were disabled. The quota read succeeded and reported the
account below both storage and inode limits.

Do not run `runtime php-*` for this account: those reads require the disabled
MultiPHP or MultiPHP INI Editor capabilities. Do not use `files inspect` or
`files list` for the target: their current audit adapter rejects this path.
Those known failures are not runtime or target evidence.

An authorised human must use the enabled cPanel interfaces without changing
anything: open **Software > Select PHP Version** (CloudLinux PHP Selector) and
record that the current account runtime is PHP 8.4. In its **Options** view,
record that `display_errors` is **Off** without changing it. Then open **File
Manager** and list the exact staging document root to record its current
metadata. Do not use MultiPHP Manager. Stop if Select PHP Version is absent,
does not show 8.4, cannot be shown to govern the staging host, or shows
`display_errors` On; stop if File Manager shows a different target. Record the
free quota and archive byte count without profile data or credentials. Browser
automation is not permitted for either cPanel check.

## 3. Create and verify recovery material in cPanel

Before overwriting anything, use cPanel File Manager to compress the exact
directory
`/home/v0398ees6dry/public_html/staging.stronger-at-home.co.uk` into a uniquely
dated ZIP under `/home/v0398ees6dry/staging-backups/`. If
`/home/v0398ees6dry/public_html/vendor` already exists, back it up separately
because it is the required sibling dependency directory. Record paths, sizes
and UTC creation time.

Inspect both backup archives in File Manager and extract each into a new
temporary verification directory. Confirm that the expected top-level entries
can be listed, then remove only those temporary verification copies. Do not test
a restore over the live target. Stop if either backup is missing, unreadable or
incomplete, or if quota cannot hold the backup plus the new release.

## 4. Prepare external staging configuration

Use cPanel account facilities to create an owner-readable configuration outside
the staging document root at:

`/home/v0398ees6dry/private/stronger-at-home/staging/site.php`

Bind `STRONGER_HOME_CONFIG` to that exact path through a cPanel-supported PHP
environment setting. Runtime writes are not available through the guarded
`cpanel-admin` interface, so this is a recorded human cPanel action. If the
account cannot provide that binding, stop; never put the file or its values in
the archive or staging document root.

Build the file from `config/site.example.php` without committing, logging or
screenshooting values. Require:

- `environment` exactly `staging`;
- `allowed_origin` exactly `https://staging.stronger-at-home.co.uk`;
- a controlled staging-only safe recipient selected by the project sponsor,
  never the live Melanie address;
- authenticated SMTP values supplied through the operator's secret source;
- a strong independent rate-limit secret; and
- `rate_limit_directory` under
  `/home/v0398ees6dry/private/stronger-at-home/staging/rate-limit`, outside the
  document root, owner-only and not a symlink.

Set the private directory to owner-only access and the PHP file to mode `0600`.
Verify that neither path is reachable over HTTPS. Do not print or record any
value from the file.

## 5. Upload and stage the archive without touching the live target

Use a unique holding directory under the account home. The archive is below the
guarded uploader's 10 MiB limit. In cPanel File Manager, first create the empty
directory `/home/v0398ees6dry/staging-releases/task8-20260903` and verify that it
contains no prior archive or extracted files. First run the exact upload as a
dry run:

```bash
cpanel-admin --profile test-123reg files upload \
  --directory staging-releases/task8-20260903 \
  --source output/site-package/stronger-at-home-staging.zip \
  --dry-run
```

Review the normalized profile, path, local hash, remote preflight, impact and
recovery guidance. File upload is treated as destructive because a same-named
remote file could be overwritten. Obtain immediate approval for that exact
plan, then replace `--dry-run` with its unexpired `--confirm DIGEST` and
`--expires-at TIMESTAMP`. If any parameter or preflight changes, discard the
plan and repeat the dry run.

The guarded CLI does not extract or rename archives. A human operator must use
cPanel File Manager to extract the uploaded ZIP inside its unique holding
directory and confirm that it yields only `public/` and `vendor/`. Never use
SSH, FTP, a raw cPanel request or a shell fallback.

Before the swap, confirm that `/home/v0398ees6dry/public_html/vendor` is not
served by another host and is not shared with another application. Stop if it
is exposed or shared. In File Manager:

1. Rename the existing staging document root to a unique `.previous-UTC`
   sibling; do not delete it.
2. Rename the extracted `public/` directory to the exact staging document-root
   path.
3. If an existing sibling `vendor/` is present, rename it to a unique
   `.previous-UTC` sibling; do not delete it.
4. Move the extracted `vendor/` into
   `/home/v0398ees6dry/public_html/vendor`.
5. Confirm that no configuration file, upload archive or backup is below the
   staging document root.

Record every rename and final path. Keep the previous directories and backup
archives until staging acceptance is complete.

## 6. Staging smoke, security and accessibility checks

Stop and roll back on the first failed smoke check.

- Request the HTTPS homepage and require a valid certificate, no mixed content,
  status 200 and no redirect to production.
- Request `/robots.txt` and require the exact two-line deny-all response. Check
  that the staging host is not present in the production sitemap and that all
  page canonicals still name the production canonical URL.
- Require `X-Robots-Tag: noindex, nofollow` on staging page responses. Stop if
  it is missing, duplicated or has a weaker value. This header is inserted only
  in the staging archive; it must not be added to the production source
  `.htaccess`.
- Require `X-Content-Type-Options: nosniff`,
  `Referrer-Policy: strict-origin-when-cross-origin`, the approved
  `Permissions-Policy`, and the approved Content Security Policy.
- Check Home, About Melanie, How I can help, Appointments and fees, Contact,
  Privacy, Accessibility and an unknown URL. Require correct pages, assets,
  navigation and the custom noindex 404 response.
- At 390×844, 768×1024 and 1440×1000, check the five primary pages for readable
  layout, no horizontal overflow and the visibly non-final portrait label.
- Use keyboard only to expose the skip link, traverse every menu item, operate
  the mobile disclosure and reach each form control. Require a clearly visible
  focus indicator and accurate `aria-expanded` state.
- At 200% browser zoom, require content to reflow without loss, overlap or
  two-dimensional page scrolling. With reduced motion enabled, require no
  meaningful animation or smooth scrolling.
- Submit an invalid form and require clear field-level errors without a network
  delivery attempt. Require the redirected page to target `#form-feedback` and
  move focus to the first invalid field; success, rate and delivery feedback
  must move focus to the generic status message without exposing submitted
  details.
- Fill the honeypot through browser developer tools and require the silent
  anti-spam response with no message sent and no visible success claim.
- With the SMTP host deliberately set to a non-routable test value, submit five
  valid synthetic requests and require generic delivery-failure feedback with
  no provider detail; the sixth request from the same test address must show the
  generic rate-limit response. Restore the reviewed configuration and clear
  only the exact staging counter through cPanel File Manager after recording
  the test.

Use fictitious details and a message containing no health or private
information for every form test.

## 7. Controlled end-to-end message — separate later authority

Do not run this test during packaging or merely because staging deployment was
approved. Obtain explicit authority for one delivery to the named safe staging
recipient after the previous checks pass and the reviewed SMTP configuration is
restored.

Submit one synthetic request. Require the generic success message to mean only
that the request was received, verify exactly one message at the safe staging
recipient, check subject/from/reply-to/body rendering, and confirm that no
credential, security token or provider debug output appears. Do not send to
Melanie's live address. Record only time, recipient label and pass/fail; do not
copy the message or address into the repository.

## 8. Rollback criteria and procedure

Rollback immediately for a wrong target/runtime, failed HTTPS or security
header check, indexable staging response, missing/broken asset or route,
horizontal overflow, inaccessible navigation/form, exposed configuration,
unexpected recipient, form-security failure, duplicate/unexpected delivery or
any smoke-check failure.

Using cPanel File Manager only:

1. Rename the failed staging document root and failed sibling `vendor/` to
   unique `.failed-UTC` names; do not overwrite evidence.
2. Rename the recorded `.previous-UTC` document root and dependency directory
   back to their exact original paths.
3. If either previous directory is unusable, stop and have the authorised human
   operator extract the verified cPanel backup into empty recovery paths; the
   guarded integration does not execute restores.
4. Re-run the HTTPS, deny-all robots, staging noindex header, security headers,
   routes and asset checks.
5. Record the failure and recovery evidence without secrets.

Keep staging unavailable rather than improvise when recovery cannot be proved.
No step in this runbook changes or authorises production.
