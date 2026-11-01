# About Melanie portrait

## Approved design
On 1 November 2026 the user approved the right-floated portrait preview.
Use the existing approved Melanie portrait unchanged, inside the biography after the heading. On wider screens, text flows beside its left edge and continues underneath. At widths of 760px or less, centre the portrait above the biography and remove the float. Retain the existing soft rounded frame, alt text and image dimensions.

## Approaches
- Separate right-hand column: initially previewed; does not allow text beneath the portrait.
- Right float within the biography: selected and approved, preserving natural text flow.
- Above the biography at all widths: retained only for narrow screens to avoid cramped text.

## Scope and constraints
Keep the approved biography wording and homepage unchanged. Reuse the JPEG; no image editing or additional dependencies. Scope new CSS to the About page. Do not alter enquiries, PHP, hosting, privacy content or credentials. Implementation remains local until separate release authorisation.

## Acceptance
Desktop portrait is right-aligned with space between image and text. Mobile portrait is centred between heading and biography. No horizontal overflow or clipping; following sections clear the float. Existing page validation and regression suite pass. Verify both desktop and mobile visually before handoff.
