# Harshit Room in 3D — Cozy Diorama & WebGL Viewer

A hand-detailed cozy 3D room diorama in the browser, inspired by Bruno Simon's
**[My Room in 3D](https://github.com/brunosimon/my-room-in-3d)**. Every visible
fitting is modelled — nothing is a flat box anymore.

## How to run (Bruno Simon workflow)

```bash
npm install
npm run dev
```

Open the local link (usually `http://localhost:5173`). Drag to orbit, scroll
to zoom. Use the panel buttons to fly to the **Desk / Bed / Wardrobe / Window**,
toggle **Auto-rotate**, or **Reset** the view.

## How it is built

- `room_generator.py` — Blender procedural modeller. Run headless to rebuild
  everything from scratch:

  ```bash
  blender --background --python room_generator.py
  ```

  Outputs are **portable** (relative to the repo, works on any machine and on
  Vercel): `room_model.glb`, `room_model.fbx`, `room_render.png`,
  `public/room_baked_combined.glb` + `public/room_baked_combined.png`.
- Baking: full Cycles **Combined** bake (diffuse + shadows + emissive) into one
  **4096px** texture on a single merged mesh, rendered unlit in Three.js at
  60 FPS — the same trick Bruno's room uses for crisp real-time quality.
- `src/main.js` — Three.js viewer: orthographic isometric camera, damped
  orbit controls, ACES tone mapping, breathing glow lights synced to the
  baked emissives, floating dust motes, focus fly-tos, polished loader.

## Detail pass (no new furniture — only deeper craft)

Constraint honored throughout: **no object category was added**. Each upgrade
is a sub-detail of something already in the room:

| Component | What got detailed |
|---|---|
| Parquet floor | Grout bed + skirt, per-tile height/tone jitter, bevels, pin dot, grain bump |
| Walls / baseboards | Plaster micro-bump, top caps, baseboard lips |
| Window | Sill nose, reveal liners, 4-pane muntins, architrave, latch + lever, glass streak |
| Door | Shaker insets + rims, 3 hinges + plates, rosette, keyhole, bottom gap shadow |
| Curtain rod | Finial spheres, wall brackets |
| Curtains (pink + teal) | 26 folds each (was 16), dual-frequency ripple, hems, pinch pleats, metal rings |
| Wardrobe | Crown + plinth, side trims, gap shadows, inset beads, handle backplates, key bow + teeth |
| Bed frame | Legs + feet, rail lips, 5 slats |
| Mattress | 4 piping seams, 6 tuft buttons |
| Pillows | Piping frames, center dimples |
| Blanket | Hem, 6 fold ridges, 5 pleated drape folds |
| Desk | Front edge band, cable grommet ring + hole, panel feet, modesty notch, tray rails + lip, footrest grips, drawer/cabinet gaps + insets, handle posts |
| Chair | Hub cap, fork yokes + axles, wheel hubs, gas rings, seat piping + quilt dimples, tilt lever + knob, arm screws, mesh ribs + lumbar pad, headrest posts |
| Laptop | Feet, ports, hinge barrels, bezel, webcam, baked screen UI (menu bar, code lines, dock), 50 sculpted keys + wide spacebar, touchpad + click line |
| Mouse | Scroll wheel, seam, glowing sensor, cable |
| Lamp | Base felt + stem, springs, routed cables, joint washers, shade inner + rim, bulb + filament, rocker switch, desk cable run |
| Bottle | Glass body, water level, paper label + stripe, neck, knurled cap (8 ribs), punt |
| Charger | Seam, prongs, LED, 3-segment cable run to the desk |
| Books ×3 | Page blocks, spines, title bands, bookmark ribbons |
| Mug | Inner wall, coffee surface, base ring, torus handle, wooden coaster |
| Pen holder + pens | Inner floor, rim, clips, metal tips, grip rings |
| Bucket | Rolled rim, 12 grip ribs, inner shadow, foot ring |
| LED strip | Channel, diffuser, 24 alternating diodes, end caps |
| Ceiling pendant | Canopy, wire + clip, socket + ring, bulb + glass + filament |

Materials all carry procedural micro-surface (wood grain + roughness breakup,
fabric weave, plastic grain, brushed metal) so close-ups never look flat.

## Files

- `room_baked_combined.glb` / `.png` (repo root copy) + `public/` serving copy
- `room_model.glb` / `room_model.fbx` — editable separates with lights/cameras
- `room_render.png` — Cycles reference render from the isometric camera
- `wood_baked.png` — baked walnut grain embedded in the model

## Deploy

```bash
npm run build   # outputs dist/
```

Deploy `dist/` to Vercel/Netlify as a static site.

## Council note (degraded mode)

A supervisor-mediated advisor council (oracle + reviewer, 2-pass cap) was
convened per `council-mode`, but the runtime reported *"No usable subagent
models remain after registry, scope, and cached-exclusion filtering"* for both
advisors, so no advisory reports were produced. The parent proceeded in direct
mode as critical judge instead: each component above was scored against the
Bruno bar (bevels, seams, hardware, material breakup, baked AO) and iterated
until no flat/crude spot remained — without adding any new object category.
