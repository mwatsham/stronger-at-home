# Durable project memory

## 2026-08-17 — sole-trader name adoption

The project sponsor decided to proceed as a sole trader using `Stronger at
Home Physiotherapy` and the `Stronger@Home` display wordmark without applying
for a UK registered trade mark at this stage. The physiotherapy focus is
accepted as sufficient practical differentiation for the current business.

This is a commercial risk decision, not legal clearance. The preliminary
UKIPO evidence from 2026-08-06 remains valid and registration is deferred. The
business must not use the `®` symbol or claim registered trade-mark rights. The
decision must be reviewed if an objection is received, the offer materially
expands beyond physiotherapy, the brand is licensed, ownership changes, or the
business decides to seek registration. Trade-mark review no longer blocks use
of the name. Website publication and unverified credential claims remain
separately gated.

## 2026-08-05 — naming architecture and current v2 artwork

The project sponsor approved the naming architecture: the formal trading name
is `Stronger at Home Physiotherapy`; the styled display wordmark is
`Stronger@Home` with `Physiotherapy`; the endorsement is `by Melanie Watsham`;
and the official sole-trader identity is `Melanie Watsham trading as Stronger at
Home Physiotherapy`. Accessible text, search metadata, ordinary prose and spoken
usage spell out `at`.

The preferred domain is `stronger-at-home.co.uk`. It was unregistered when
checked on 2026-08-04, but registration and control remain unverified. The
public name was then still proposed pending an official UKIPO exact and
confusing-similarity trade mark search in relevant service classes.

On 2026-08-06, an official UKIPO preliminary word-mark screen found no exact
live match for `Stronger at Home` or `Stronger@Home`. A broader live Class 44
screen found registered `STRONGER` mark UK00003586606 for mental-health
services and registered `Everyday Stronger` mark UK00003957710, whose terms
include home healthcare, healthcare in domestic homes and health advice for
elderly people. Because the latter services materially overlap the proposed
offer, the public name is not cleared. UK trade mark attorney review is required
before public use or filing. The detailed evidence and limitations are recorded
in `brand/trademark-screening.md`.

Later on 2026-08-05, the project sponsor confirmed that the domain is
registered. A read-only check of the only configured cPanel profile did not
find the domain or the `melanie@stronger-at-home.co.uk` mailbox, so attachment
and operational control remain unverified. No cPanel change was made.

After the project sponsor attached the production and staging domains, a second
read-only check on 2026-08-05 verified both in the `test-123reg` profile. They
use separate document roots. Public DNS resolves both hosts to the cPanel
server, and valid HTTPS coverage is installed for production, `www` and
staging. Each public website URL returned HTTP 403 because public site content
is not yet available. Public mail uses SecureServer MX and SPF records in the
authoritative GoDaddy DNS zone and has a DMARC quarantine policy. The `melanie`
mailbox is not present in cPanel; because mail is routed externally, delivery
must be verified with the external mail service rather than inferred from
cPanel.

The project sponsor subsequently confirmed on 2026-08-05 that
`melanie@stronger-at-home.co.uk` exists in Titan Email. Titan's official setup
requires `mx1.titan.email`, `mx2.titan.email` and an SPF include for
`spf.titan.email`. A transient recursive lookup later showed those generic Titan
records, but both authoritative GoDaddy nameservers continued to return
SecureServer MX and SPF records. A two-way test through
`webadmin@stronger-at-home.co.uk` then succeeded on 2026-08-05. The reply used a
Titan message identifier and SecureServer delivery infrastructure; Gmail
reported SPF pass, DKIM pass for both `secureserver.net` and aligned
`stronger-at-home.co.uk`, and DMARC pass. DMARC remains `p=quarantine`, with
aggregate reports routed to `dmarc_rua@onsecureserver.net`. This message-level
evidence supersedes the generic Titan-DNS assumption. Delivery for the public
`melanie` address remains unverified. GoDaddy remains authoritative for DNS;
cPanel is not authoritative for these mail records.

On 2026-08-06, the public `melanie@stronger-at-home.co.uk` address completed a
separate two-way delivery test. Gmail recorded SPF pass, aligned DKIM pass for
`stronger-at-home.co.uk`, an additional DKIM pass for `secureserver.net`, and
DMARC pass at `p=quarantine`. This resolves the public-email operational gate.

The project sponsor approved these public contacts: mobile `+447843497871`,
email `melanie@stronger-at-home.co.uk`, address `11 Mospey Crescent, Epsom,
Surrey, KT17 4LZ`, email as the preferred contact method, and website
`www.stronger-at-home.co.uk`. Public email delivery is verified. The website
must not be published until its content is verified. HCPC, CSP, AGILE and ATOCP
wording remains to be confirmed.

Melanie Watsham approved both exact current v2 files without changes on
2026-08-05:

- `brand/assets/source/logo-primary-raster-v2-2048.png` at 2048 × 640 pixels.
- `brand/assets/source/logo-primary-raster-v2-512.png` at 512 × 160 pixels.

The project sponsor confirmed usage rights on 2026-08-04 for the immutable
supplied-v2 source image with SHA-256
`41267865711ca55f9225df8370c50bca823f68ca966b8fc216852e65a36d0ef1`.
The project sponsor separately confirmed sole usage rights on 2026-08-05 for
the older supplied PNG with SHA-256
`6d066dbeff88023aece19346a1d0a9a1d3f4577f7846545e359ad59fab24f889`.
Trademark/name clearance, public website content, and HCPC/CSP/AGILE/ATOCP
wording verification continue to block public use.

## 2026-08-04 — raster-only primary artwork

The project sponsor approved the raster-only design direction, and Melanie
Watsham subsequently approved both exact final output files without changes on
2026-08-04. The immutable source is
`docs/superpowers/specs/assets/home-physiotherapy-logo-approved-concept-v2.png`
with SHA-256
`41267865711ca55f9225df8370c50bca823f68ca966b8fc216852e65a36d0ef1`.
It is composited only through the fixed crop `(300, 285, 954, 1023)`.

These now-historical approved exact outputs are
`brand/assets/source/logo-primary-raster-2048.png` at 2048 × 640 pixels and
`brand/assets/source/logo-primary-raster-512.png` at 512 × 160 pixels. They
are opaque raster-only lockups: no SVG, transparent, monochrome or AI-redrawn
derivatives may be made. On 2026-08-04, Melanie Watsham approved both exact
raster logo files without changes. This exact-output approval was separate from
the sponsor's design approval and did not itself approve the business name,
credentials, source-image ownership/usage rights, contact information, or any
other clearance item. The project sponsor separately confirmed usage rights for
the exact supplied-v2 source image on 2026-08-04; other clearance items remain
separately gated.

## 2026-08-03 — refreshed-repository rebuild

The Stage 1 repository was rebuilt to restore authoritative Markdown and JSON
brand sources, a decision ledger, and a dependency-free validation foundation.
The public name remains proposed pending clearance. The historical hybrid logo
direction is deprecated. The historical raster-only output pair was approved by
Melanie Watsham on 2026-08-04 and was superseded by the exact v2 wordmark pair
approved on 2026-08-05. All separate launch gates remain unresolved or
verification-gated as recorded in `brand/clearance.md`.

The project sponsor rejected the first reconstructed hybrid logo and selected
an initial supplied reference for the now-deprecated production-cleanup
direction. Its rights status remains unresolved for public use pending explicit
ownership/usage-rights confirmation for that exact supplied image.

The governing requirements are in
[the raster-only logo specification](docs/superpowers/specs/2026-08-04-home-physiotherapy-logo-delicate-home-design.md).
The earlier [supplied-logo production-cleanup specification](docs/superpowers/specs/2026-08-03-supplied-logo-production-cleanup-design.md)
and [hybrid logo exploration specification](docs/superpowers/specs/2026-08-03-stronger-at-home-hybrid-logo-exploration-design.md)
are superseded for the primary artwork direction.
The owned artwork evidence remains read-only at
`/Users/mwatsham/Documents/Codex/2026-08-03/i/outputs`; it must not be altered.
