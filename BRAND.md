# Stronger at Home Physiotherapy

Status: approved strategy, identity and website design; staging deployment and production publication blocked
Approval owner: Melanie Watsham

Experienced care. Personal progress. At home.

## Adoption boundary

This repository is the Stage 1 source of truth for the brand system. The public
name `Stronger at Home Physiotherapy` is approved for sole-trader physiotherapy
use. The project sponsor accepted the residual risk identified by the
preliminary UKIPO screen and deferred registration on 2026-08-17. This is a
commercial decision, not legal clearance or a registered trade mark. Do not use
the `®` symbol. `Stronger@Home` is reserved for the display wordmark, with
`Physiotherapy` as the service descriptor and `by Melanie Watsham` as the
endorsement. Accessible text, search metadata, ordinary prose and spoken usage
must spell out `at`.

Melanie Watsham confirmed on 2026-08-05 that the business will operate as a
sole trader using `Stronger at Home Physiotherapy` and the `Stronger@Home`
display wordmark. Official paperwork must identify `Melanie Watsham trading as
Stronger at Home Physiotherapy` and must not imply that the business is
incorporated.

The preferred domain `stronger-at-home.co.uk` and staging host
`staging.stronger-at-home.co.uk` are attached to the configured `test-123reg`
cPanel account with separate document roots. Public DNS and HTTPS were verified
on 2026-08-05, but all three website URLs returned HTTP 403 because no public
site content is available yet. The public contact details approved on
2026-08-05 are mobile `+447843497871`, email
`melanie@stronger-at-home.co.uk`, address `11 Mospey Crescent, Epsom, Surrey,
KT17 4LZ`, preferred contact method email, and website
`www.stronger-at-home.co.uk`. The project sponsor confirmed that the external
Titan `melanie` mailbox exists. Authoritative GoDaddy DNS routes mail through
SecureServer infrastructure. A two-way test using
`webadmin@stronger-at-home.co.uk` succeeded on 2026-08-05; Gmail verified SPF,
aligned DKIM and DMARC as passing. DMARC is active at `p=quarantine`, with
reports routed to an `onsecureserver.net` address. The public `melanie` mailbox
passed its own two-way delivery test on 2026-08-06; Gmail verified SPF, aligned
DKIM and DMARC as passing. The mailbox is not hosted in this cPanel account.
The email operational gate is resolved. Do not publish the website until its
content is operationally verified.

Melanie Watsham approved both exact current v2 raster-only primary artwork files
without changes on 2026-08-05. The project sponsor confirmed usage rights for
their immutable supplied-v2 source image on 2026-08-04 and sole usage rights
for the older supplied PNG on 2026-08-05. Professional credential wording
remains to be confirmed. Name use is no longer blocked by trade-mark review.
Website publication remains blocked until its content is operationally
verified, and professional credentials must not be claimed until their
wording is verified in `brand/clearance.md`. No patient, referral, website,
social, uniform, vehicle or signage templates are included in this stage.

The reassurance-first, five-page website design was approved by the project
sponsor on 2026-09-03. It uses `Request an appointment` as its primary action,
addresses the adult patient directly and adopts the calm-editorial homepage
composition. The design is documented in
`docs/superpowers/specs/2026-09-03-stronger-at-home-website-design.md`.
Approval of the design does not authorise production publication.

The local staging workflow prepared on 2026-09-03 packages the exact approved
public tree as `public/` with a sibling production-only `vendor/` tree pinned to
PHPMailer 7.1.1. The package gate fingerprints the exact 84-file dependency tree
and rejects any added, missing or changed vendor file. Staging uses deny-all
robots and requires a reversible cPanel runbook, an external safe-recipient
configuration and separate deployment authority. No hosting change has been
made. The public site and its human content-review checklist intentionally
contain no payment-method wording; the approved individual quotation and agreed
fixed-price wording remains. Only the final professional portrait and approved
privacy retention wording remain as production content blockers; unverified
credential and referral wording stays omitted.

Start with [strategy](brand/strategy.md), [messaging](brand/messaging.md),
[identity](brand/identity.md), [clearance](brand/clearance.md), and the
[trade mark screen](brand/trademark-screening.md), then consult the [decision
ledger](DECISIONS.md).
