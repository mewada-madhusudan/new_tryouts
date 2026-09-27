/brag --tone "single cohesive team narrative, cinematic, full-bleed layouts"

Use the existing data in "Team Promotional data/" instead of re-researching:
- Company/brand facts: sto-brand-and-site-data.md
- Team roster and overall stats (total projects delivered, years active, etc.): team-roster.md
- Individual bios: profiles/*.md (24 people)
- Photos: photos/

Structure requirements — this is a rework of a previous render (sto-team-video.mp4) that had two specific problems, fix both:

1. NO PER-PERSON SEGMENTS. Do not give each of the 24 people their own full scene.
   Build one unified story arc instead:
   - Opening scene: who we are, our mission, in one sentence
   - Impact scene: aggregate stats ONLY stated once (total projects delivered,
     years in operation, client count) — never repeat these numbers per person
   - Team scenes: group people in clusters of 4-6 per scene (by team/function
     if the roster has that info, otherwise just visually grouped), showing
     photos + names + one distinct detail per person, not a repeated bio template
   - Closing scene: call to action / brand sign-off

2. FULL-SCREEN LAYOUTS. Previous render left large empty areas — every scene
   must fill the entire 1920x1080 frame edge-to-edge. Use full-bleed background
   imagery/color, vary composition across scenes (don't center-align every
   scene identically), and vary layout per scene type (grid for team clusters,
   full-frame photo + overlay text for stats, etc.).

Target length: 45-60 seconds. Keep narration/text sparse — this is a visual
showcase, not a read-aloud bio for 24 people.

Save output as a new file, don't overwrite sto-team-video.mp4 — use
sto-team-video-v2.mp4 so I can compare.
