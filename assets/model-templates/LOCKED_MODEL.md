# Locked model identity — v2

## Canonical facial identity reference

`locked-model-frontal-v2.png`

## Canonical body and view reference

`locked-model-views-body-v3.png`

This four-view sheet is the canonical reference for body proportions, full-body silhouette, front/side/back consistency, and neutral clothing fit. It supplements the frontal portrait; it does not replace the frontal portrait as the facial identity anchor.

This **front-facing portrait** is the sole identity anchor for all future fashion keyframes and video prompts.

## Non-negotiable invariants

- Preserve the same adult East Asian woman's frontal facial proportions, eye shape and spacing, nose, lips, face shape, natural skin tone, long straight black hair, and slender body proportions.
- Include the actual canonical image as reference 1 on EVERY image generation and image edit, including local clothing/background corrections. Text mentioning this file is not an attached reference. Never use a drifted generated image alone as identity.
- Use `locked-model-views-body-v3.png` as a supporting body/view reference when a full-body, side-view, back-view, or proportion-sensitive result is required. The frontal portrait remains identity reference 1.
- For VIDEO generation, attach only the accepted identity-carrying keyframe(s), not the separate original face image unless the user explicitly requests re-locking. Follow the 2026-09-08 gates in `../locked-model-outfit-tests/VIDEO_WORKFLOW_RULES.md`.
- Do not use the older walking or side-view image as a facial identity reference. It may only inform body scale or composition when needed.
- Change only clothing, accessories, environment, lighting, and pose; do not redesign the person.
- For video keyframes, keep full body, both feet visible, eye-level camera, and a clear central walking path unless a specific shot requires otherwise.
