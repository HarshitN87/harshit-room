# Harshit Room in 3D — Cozy Diorama

A hand-detailed cozy 3D room diorama in the browser, built **100% procedurally
in Three.js** on the [`room-3d-mvp` pipeline](https://github.com/brunosimon/my-room-in-3d)
(Vite + current Three.js, canvas textures, real-time lights — no Blender bake
step, so what you edit is what you see).

## Run

```bash
npm install
npm run dev
```

Open the printed localhost URL. Drag to orbit, scroll to zoom.
Click the **lamp**, the **laptop screen**, or the **ceiling pendant** —
or use the chips: 💡 Lamp · 🖥 Screen · 🔆 Pendant · ☀️ Day/Night.

## Build / deploy

```bash
npm run build   # outputs dist/
npm run preview
```

`dist/` is a static site (Vercel/Netlify-ready, `base: './'`).

## Architecture (room-3d-mvp pipeline)

- `src/main.js` — renderer (ACES, sRGB, soft shadows), studio light rig,
  day/night mix, dust motes, raycast interaction, intro tween, `__snapView`
  hook for screenshot verification.
- `src/components/materials.js` — shared canvas textures (star tile,
  walnut, weaves, screen UIs) + `MeshStandardMaterial` set.
- `src/components/helpers.js` — `box` / `rbox` (rounded) / `aoBlob` factories.
- One builder per fitting: `shell` · `windowWall` · `door` · `wardrobe` ·
  `bed` · `desk` · `chair` — each exports `buildX(scene, ctx)` with
  `ctx = { M, box, rbox, aoBlob, W, D, H }`, same signatures as the MVP.

## What's modelled (same room as before — nothing added, nothing removed)

| Fitting | Detail |
|---|---|
| Shell 4×4×3 | Starburst tile floor, west window opening, north door opening, skirting, contact-shadow gradients |
| Window | 4-pane muntins, architrave, latch, sill + apron, rod with finials/brackets/rings, night glass with moon + skyline |
| Curtains | Pink + teal, vertex-wave folds animated in the loop, hems, header tape |
| Door | Leaf ajar on 3 hinges, shaker insets, lever + rosettes |
| Wardrobe | Crown + plinth, 2 drawers, 4 inset doors with beads, bar handles, lock with brass key |
| Bed | Frame + legs + slats, piped mattress with buttons, 2 sculpted pillows, wavy purple blanket with ridges + pleated drape |
| Desk | Grommet, tray + rails, footrest, drawer + cabinet with gaps/insets, desk mat |
| Laptop | Code-editor screen UI (click to toggle), 50 keys + spacebar, touchpad, hinges, webcam, glow |
| Mouse | Wheel, glowing sensor |
| Lamp | Articulated arms, spring, cable, shade + reflector, bulb (click to toggle) |
| Bottle | Liquid level, label, knurled cap |
| Charger | Seam, LED, cable run to laptop |
| Books ×3 | Page blocks, title bands |
| Mug + pens | Coffee surface, torus handle, coaster, clips + tips |
| Bucket | Rolled rim, 12 ribs, inner shadow |
| LED strip | Channel + diffuser, 24 alternating diodes, end caps |
| Pendant | Canopy, wire, socket, filament bulb + halo (click to toggle) |

## History note

The repo previously rendered a single Blender-baked GLB (`room_generator.py`
+ `*_baked_combined.*`). That snapshot is retired — the stale binaries are
removed and the script is kept only as a modelling reference — because a
frozen bake is exactly why the site "looked the same" after edits. Every mesh
above is live geometry now.

## Council note (degraded mode)

A supervisor-mediated advisor council (oracle-fork + reviewer, 2-pass cap) was
convened per `council-mode`, but the runtime reported *"No usable subagent
models remain"* for both advisors, so the parent proceeded in direct mode as
critical judge, scoring each fitting against the Bruno bar (bevels, seams,
hardware, material breakup, light response) under the standing constraint of
no new object categories.
