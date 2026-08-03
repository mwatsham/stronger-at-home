# Stronger at Home Physiotherapy Hybrid Logo Exploration Design

Status: approved exploration design; final artwork remains proposed

Date: 2026-08-03

Approval roles:

- Project sponsor: approves the exploration direction and implementation scope.
- Melanie Watsham: must explicitly approve final public artwork before any logo asset becomes `approved`.

## 1. Outcome

Replace the previously approved wordmark-only architecture with a proposed hybrid architecture for the next artwork round. The primary identity will combine the existing typographic wordmark with a house-and-care symbol. The symbol may accompany the wordmark but is not approved for standalone use.

This design revises only the logo exploration and approval path. Existing strategy, message hierarchy, palette and typography remain unchanged.

## 2. Approved inputs

- Brand name: `Stronger at Home Physiotherapy`, still `proposed` pending business-name clearance.
- Endorsement: `by Melanie Watsham`.
- Core message: `Experienced care. Personal progress. At home.`
- Primary ideas: reassurance, professional care at home, increasing strength and personal progression.
- Primary audience: patients and older adults; professional referrers remain secondary.
- Palette: Deep Navy `#203E55`, Pale Sky `#E8F1F6`, Warm Cream `#F7F2E8`, Warm Sand `#C3A26E`.
- Typography: Source Serif 4 for wordmark and headings; Atkinson Hyperlegible Next for endorsement and functional text.

## 3. Chosen identity architecture

Use a horizontal hybrid lockup:

1. A simple house outline with an open doorway.
2. The complete owned care-and-progression symbol placed inside the house.
3. The existing two-line wordmark placed to the right.
4. The endorsement retained and made more legible at small sizes.

The house symbol and wordmark form one primary composition. Do not approve or document the symbol as an independent badge during Stage 1.

## 4. Owned source asset and provenance

The user confirmed full ownership of the supplied source artwork on 2026-08-03. The reference files are:

- `/Users/mwatsham/Documents/Codex/2026-08-03/i/outputs/home-physiotherapy-logo.svg`
- `/Users/mwatsham/Documents/Codex/2026-08-03/i/outputs/home-physiotherapy-logo-monochrome.svg`
- `/Users/mwatsham/Documents/Codex/2026-08-03/i/outputs/home-physiotherapy-logo-2048.png`
- `/Users/mwatsham/Documents/Codex/2026-08-03/i/outputs/home-physiotherapy-logo-512.png`

The supplied SVGs contain an embedded raster figure. They are provenance sources, not production-ready logo masters. Reconstruct the person as clean vector geometry by tracing the owned source faithfully. Preserve the hand, moving person and three ascending steps. Do not use an image model to recreate or reinterpret the geometry.

Copy source evidence into the project only as a provenance reference during implementation. Record its original path, acquisition date, ownership statement and SHA-256 hash. Do not modify the files in `/Users/mwatsham/Documents/Codex/2026-08-03/i/outputs`.

## 5. Symbol composition

### House

- Use one continuous Deep Navy outline.
- Keep the silhouette simple and immediately recognisable as a home.
- Leave a clear doorway opening at the base.
- Do not add a chimney, windows, medical cross, leaf, spine, decorative roof detail or enclosing badge.

### Care and progression artwork

- Place the complete hand, person and three steps inside the house outline.
- Keep the hand and person Deep Navy.
- Recolour all three progression steps Warm Sand.
- Align the lowest step with the open doorway so the movement reads as crossing the threshold and progressing upward within the home.
- Preserve generous negative space between the house outline and internal artwork.
- Simplify nodes and curves only where required for reliable rendering at small sizes; preserve the meaning and recognisable pose.

### Relationship to the wordmark

- Place the symbol to the left of the wordmark.
- Keep the symbol optically subordinate to the words `Stronger at Home`.
- Maintain a clear gap between symbol and lettering.
- Avoid placing the symbol above the wordmark in the primary composition because it would increase vertical depth and reduce usefulness on letters, referral documents and website headers.

## 6. Typography and colour

- Retain `Stronger at Home` and `Physiotherapy` as editable Source Serif 4 text in the source SVG.
- Retain `by Melanie Watsham` as editable Atkinson Hyperlegible Next text.
- Increase the endorsement size or adjust spacing so it remains legible in the agreed small-header test.
- Use only Deep Navy and Warm Sand in the primary source artwork.
- Use Pale Sky and Warm Cream only as review or application backgrounds.
- A reversed and monochrome treatment may be designed only after the primary hybrid lockup is explicitly approved by Melanie.

## 7. Review compositions

Present the proposed primary hybrid lockup:

- On Warm Cream, Pale Sky and Deep Navy review fields.
- At full review size, half size and small-header size.
- Beside the supporting line `Experienced care. Personal progress. At home.`
- With a close view of the house-symbol geometry.
- With the label `PROPOSED — NOT FOR PUBLIC USE`.

The Deep Navy field may use a Warm Cream holding surface until a reversed variant exists. Do not imply that a reversed asset has been approved.

## 8. Validation and acceptance tests

Automated validation must confirm:

- The production SVG contains no embedded raster `<image>` element.
- The SVG includes accessible title text containing the full business name and endorsement.
- The exact business-name and endorsement strings remain present as editable text.
- Only `#203E55` and `#C3A26E` are used in the primary artwork.
- The asset-manifest path and SHA-256 hash match the source file.
- The primary hybrid logo begins with status `proposed` and null review metadata.
- Any `approved` logo requires `reviewed_by: "Melanie Watsham"` and an actual ISO review date.
- The full brand validation suite and generated-token drift checks pass.

Visual acceptance must confirm:

- The home outline is recognisable without feeling generic or decorative.
- The hand, person and three steps remain distinguishable at the small-header test size.
- The progression steps read as improvement rather than an accessibility barrier.
- The symbol does not overpower the wordmark.
- The endorsement is legible and appropriately secondary.
- The primary navy-and-sand treatment remains clear on every approved review background; monochrome validation is deferred until a post-approval variant is designed.

## 9. Governance and migration

The current proposed wordmark artwork remains a valid exploration artifact but is not approved for public use.

During implementation:

- Change decision `D-10` from the approved wordmark-only architecture to `deprecated`.
- Add a new `proposed` hybrid-architecture decision approved for exploration by the project sponsor.
- Keep the final hybrid artwork `proposed` until Melanie explicitly approves it.
- Update `brand/identity.md`, `.ai/context/brand.json`, `MEMORY.md` and the asset manifest to distinguish architecture approval from artwork approval.
- Replace the current Task 5–6 implementation sequence with hybrid-primary creation, explicit Melanie approval, then optional variants.

Do not silently overwrite the existing wordmark source. Retain it as a traceable proposed exploration asset or move it only through a documented, recoverable migration step.

## 10. Out of scope

- Patient flyers, referral sheets, website pages, social templates, uniforms, vehicle graphics or signage.
- A standalone house-symbol badge.
- Photography or illustration direction changes.
- Public use of the uncleared business name.
- Claims, credentials or contact details not already verified through the clearance workflow.

## 11. Completion boundary

This exploration is complete only when:

1. The revised implementation plan has been approved.
2. The proposed hybrid primary logo has passed automated and visual review.
3. The user confirms Melanie Watsham explicitly approved the final artwork.
4. Approval metadata and governance documents are updated consistently.

Until all four conditions are met, the hybrid logo remains proposed and must not be propagated into public templates or exports.
