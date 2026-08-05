# Clearance register

All fields below are unresolved unless a dated evidence record is added. An
unresolved entry is not permission to publish.

| Item | Status | Required evidence | Public-use boundary |
|---|---|---|---|
| `Stronger at Home Physiotherapy` formal trading name and `Stronger@Home` display wordmark | sole-trader use confirmed; trademark clearance pending | Project sponsor confirmed intended use on 2026-08-05; official UKIPO exact and confusing-similarity trademark search remains required | Do not use publicly before trademark/name clearance. Treat `@` as equivalent to `at` during clearance. |
| `stronger-at-home.co.uk` preferred domain | registered; cPanel attachment, DNS and HTTPS verified; website content pending | Read-only cPanel and public network checks on 2026-08-05 verified production, `www` and staging; each public website URL currently returns HTTP 403 | Domain-control gate resolved. Do not publish the website until content is deployed and reviewed. Domain status is not trademark clearance. |
| HCPC wording | verification-gated | Dated credential verification | Do not publish as verified. |
| CSP wording | verification-gated | Dated credential verification | Do not publish as verified. |
| AGILE wording | verification-gated | Dated credential verification | Do not publish as verified. |
| ATOCP wording | verification-gated | Dated credential verification | Do not publish as verified. |
| Public contact fields | approved; Titan mailbox existence confirmed; website content, email delivery and DKIM unverified | Approved by project sponsor on 2026-08-05: mobile `+447843497871`; email `melanie@stronger-at-home.co.uk`; address `11 Mospey Crescent, Epsom, Surrey, KT17 4LZ`; preferred method email; website `www.stronger-at-home.co.uk`; external Titan mailbox existence confirmed; live MX and SPF still point to SecureServer | Do not publish the email or website until Titan DNS, mail delivery and website content are operationally verified. |
| Source Serif 4 and Atkinson Hyperlegible Next files | provenance confirmed | Action-time approval and 2026-08-03 official Google Fonts download; paired SIL Open Font License 1.1 files, source URLs and SHA-256 hashes recorded in `brand/fonts/README.md` | Local editable artwork and review only; not a clearance of the public name, credentials, or final artwork. |
| Owned source artwork | provenance confirmed | Source path, acquisition date, ownership statement and SHA-256 recorded with asset work | Keep source evidence read-only. |
| Supplied PNG `6d066dbeff88023aece19346a1d0a9a1d3f4577f7846545e359ad59fab24f889` | sole usage rights confirmed | Project sponsor confirmed sole usage rights for this exact supplied image on 2026-08-05 | Evidence applies only to this exact file; the artwork remains deprecated and must not replace the current primary assets. |
| Supplied v2 PNG `41267865711ca55f9225df8370c50bca823f68ca966b8fc216852e65a36d0ef1` | rights confirmed | Project sponsor confirmed usage rights for this exact supplied image on 2026-08-04 | Evidence applies only to this exact file; all other launch gates remain in force. |
| `brand/assets/source/logo-primary-raster-2048.png` historical raster artwork | deprecated; historically approved | Approved without changes by Melanie Watsham on 2026-08-04; superseded by the v2 wordmark | Preserve as immutable history; do not use as the current primary artwork. |
| `brand/assets/source/logo-primary-raster-512.png` historical raster artwork | deprecated; historically approved | Approved without changes by Melanie Watsham on 2026-08-04; superseded by the v2 wordmark | Preserve as immutable history; do not use as the current primary artwork. |
| `brand/assets/source/logo-primary-raster-v2-2048.png` exact current raster artwork | approved | Approved without changes by Melanie Watsham on 2026-08-05 | Do not export or use publicly until every separate launch gate is resolved. |
| `brand/assets/source/logo-primary-raster-v2-512.png` exact current raster artwork | approved | Approved without changes by Melanie Watsham on 2026-08-05 | Do not export or use publicly until every separate launch gate is resolved. |

## cPanel verification record

On 2026-08-05, a read-only check of the only configured cPanel profile
completed successfully. That account listed `fabratory.co.uk` and its staging
subdomain, but did not contain `stronger-at-home.co.uk`; inspecting the latter
returned “Unable to locate the domain.” The account also did not contain the
`melanie@stronger-at-home.co.uk` mailbox. No cPanel mutation was attempted.

After the project sponsor created the production and staging domains, a second
read-only check on 2026-08-05 verified `stronger-at-home.co.uk` and
`staging.stronger-at-home.co.uk` as add-on domains in `test-123reg`, with
separate document roots. Public DNS resolves production, `www` and staging to
`92.205.168.229`; HTTPS certificate coverage is installed for all three. Each
URL currently returns HTTP 403, so website content is not operational. Public
mail records point to GoDaddy/SecureServer, with SPF and a DMARC quarantine
policy. No `melanie` mailbox exists in cPanel, which is consistent with external
mail routing but does not verify that the external mailbox exists or receives
mail. The account does not expose cPanel's `emailauth` feature, so cPanel-based
DKIM, SPF and DMARC validation was unavailable. No mutation was attempted.
The project sponsor then confirmed that the `melanie` mailbox exists in Titan
Email. This confirms existence, not successful send/receive delivery or DKIM.
Authoritative GoDaddy DNS still points MX and SPF to SecureServer rather than
Titan's standard records, so mail-routing changes must be made and verified in
the GoDaddy DNS control plane, not this non-authoritative cPanel zone.
