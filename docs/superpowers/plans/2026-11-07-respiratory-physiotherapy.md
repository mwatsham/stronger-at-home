# Respiratory physiotherapy — approved local update

## Scope
Apply the user-approved respiratory wording to the homepage, How I can help and About Melanie, including search and social descriptions. Keep adult-only scope, existing services, imagery and enquiry handling unchanged. Local preview only; no publication.

## Implementation
1. Add a navigation regression test proving the homepage respiratory link targets a unique service-page section; observe failure before implementation.
2. Add the approved three-paragraph service description and short homepage/About summaries. Reuse the existing two-column card layout; no CSS changes.
3. Refresh approved page hashes, run the existing suite and validators, review the diff and open a local preview.

## Progress
- Isolated branch: codex/respiratory-physiotherapy, based on origin/main.
- Navigation test failed as expected before the new section/link existed.
- Copy and metadata applied to three pages; production configuration untouched.
- Human prose reviewed against approved wording, not locked into redundant exact-text tests.
- Verified: 205 Python tests pass; PHP tests, development/staging site validation, brand validation, JavaScript syntax and diff whitespace checks pass.
- Existing homepage copy expectation aligned with the approved breathing-support sentence.
- Independent review found no important defects; desktop previews checked for all three changed pages.
- Local preview: http://127.0.0.1:58637/how-i-can-help/#respiratory-physiotherapy. No push or deployment.
