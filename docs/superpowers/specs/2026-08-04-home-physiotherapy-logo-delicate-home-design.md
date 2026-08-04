# Delicate At-Home Physiotherapy Logo Design

Status: Approved visual direction; awaiting written-spec review.

## Objective

Evolve the existing home-physiotherapy logo into a more delicate, coherent symbol that communicates three ideas without accompanying text:

1. physiotherapy is delivered inside the patient's home;
2. mobility improves through gradual, supported progression; and
3. the service feels reassuring, personal, and capable.

The approved concept study is stored at `assets/home-physiotherapy-logo-approved-concept-v2.png`. It is a visual reference only. The production artwork must be rebuilt as clean, deterministic vector geometry rather than traced from the raster preview.

## Approved composition

### Home

- An open deep-blue house outline shelters the figure and steps.
- The outline consists of a shallow pitched roof, a small chimney, and two short side walls.
- The house remains open at the bottom so it feels welcoming rather than enclosed.
- The vertical roof-to-head clearance is no more than one-and-a-half figure-head diameters, while retaining an intentional transparent gap.
- The roof and walls use rounded caps and joins with one consistent line weight.

### Figure and progression

- A deep-blue monoline figure walks upward inside the house.
- The figure uses the same rounded outline language as the house and hand: outlined circular head, smooth torso, and rounded limbs.
- The pose remains derived from the user's supplied climbing-figure reference, but it is redrawn into coherent vector linework rather than embedded as a raster silhouette.
- Exactly three short, slim warm-gold steps rise from left to right.
- The raised front foot sits directly above the lowest step with a narrow transparent gap and no contact.
- The figure and steps read as one centred activity group with balanced space to the roof and side walls.

### Supporting hand

- A single cupped deep-blue hand supports the home without touching it.
- The hand's outline bounding box spans 88–92% of the house outline's width, making it slightly smaller while retaining visual support.
- The palm uses a light, flowing outline rather than a solid silhouette.
- Four long, tapered fingers have graduated lengths, natural curvature, and visible negative space between them.
- The fingers must not merge, cross, double, or appear claw-like.
- The hand is centred beneath the home with a compact but clearly transparent gap.

## Spatial balance

- The complete symbol has a compact, near-square footprint.
- The house, therapy activity, and hand share one vertical centre.
- Left and right outer margins are visually balanced.
- The house aligns over the usable width of the palm and does not overpower it.
- Internal spacing follows a consistent rhythm: controlled roof headroom, even side margins around the activity, a narrow foot-to-step gap, and a compact house-to-hand gap.
- No two conceptual elements touch or overlap.

## Visual character

- Delicate, reassuring, supportive, calm, and professional.
- Rounded linework rather than heavy filled silhouettes or sharp corners.
- Primary deep blue: `#203E55`, used for the house, figure, and hand.
- Progress accent warm gold: `#C3A26E`, used only for the three steps.
- No gradients, shadows, textures, leaves, medical crosses, arrows, or decorative additions.
- The mark must remain coherent in a single-colour version.

## Production assets

- Portable colour SVG master with no external image references.
- Portable monochrome SVG.
- Transparent PNG at 2048 px.
- Transparent PNG at 512 px.
- The existing filenames remain unchanged so downstream use does not break.

## Acceptance criteria

- The home cue is immediately recognisable without dominating the hand or therapy activity.
- The hand, house, figure, and all three steps remain visually distinct at 48 px.
- The monoline figure remains recognisable as a person walking upward at 48 px.
- The figure's raised front foot aligns above the lowest step with a transparent gap and no overlap.
- The roof retains visible headroom but does not create an empty upper band.
- The four hand fingers remain individually legible and naturally proportioned.
- Colour and monochrome exports preserve the same element separation.
- All exports have transparent backgrounds, contain no watermark, and open without missing assets.

## Supersession

This design replaces the solid-hand and embedded-raster-figure treatment defined in `2026-08-03-home-physiotherapy-logo-design.md`. The earlier specification remains as historical context for the progression and foot-alignment decisions.
