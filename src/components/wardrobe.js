import * as THREE from 'three'

/* Harshit full-wall built-in wardrobe on the MVP pipeline: north wall from
   the west corner to the door frame (~2.5m), floor to ceiling, all honey
   wood (no dark brown), NO drawers — 4 shutter columns (2 pairs): tall
   lower doors (75%) + loft doors (25%), chrome bar handles + knobs,
   brass key in the right-hand door (same fitting). */
export function buildWardrobe(scene, ctx, layout) {
  const { M, box, aoBlob } = ctx
  const { ZN } = layout
  const X0 = -2.0, X1 = 0.5 // full wall except the door
  const CX = (X0 + X1) / 2, W2 = X1 - X0 // -0.75, 2.5
  const DP = 0.55, FZ = ZN + DP // front face z ≈ -1.45

  const g = new THREE.Group(); g.name = 'wardrobe'; scene.add(g)
  function wbox(w, h, d, mat, x, y, z) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m
  }

  // carcass + plinth + cornice, all honey (scribed wall to wall)
  wbox(W2, 2.72, DP, M.woodMat, CX, 0.10 + 2.72 / 2, ZN + DP / 2)
  wbox(W2, 0.10, DP - 0.04, M.woodMat, CX, 0.05, ZN + DP / 2) // plinth
  wbox(W2 - 0.02, 0.05, 0.06, M.woodMat, CX, 0.115, FZ - 0.01).castShadow = false // plinth step
  wbox(W2 + 0.06, 0.10, DP + 0.06, M.woodMat, CX, 2.87, ZN + DP / 2) // cornice
  wbox(W2 + 0.02, 0.025, DP + 0.02, M.woodMat, CX, 2.81, ZN + DP / 2).castShadow = false // cornice step
  // side scribes into the walls
  wbox(0.04, 2.82, DP, M.woodMat, X0 + 0.02, 1.46, ZN + DP / 2)
  wbox(0.04, 2.82, DP, M.woodMat, X1 - 0.02, 1.46, ZN + DP / 2)
  // mid rail dividing 75 / 25
  wbox(W2 - 0.04, 0.09, 0.03, M.woodMat, CX, 2.165, FZ + 0.015)

  const NCOL = 4, colW = W2 / NCOL // 4 shutters, ~0.625m each
  const handleSide = [-1, 1, -1, 1] // mirror pairs: outer edges + center
  for (let ci = 0; ci < NCOL; ci++) {
    const ccx = X0 + colW * (ci + 0.5)
    // lower door (75%) + raised shaker panel + bead
    wbox(colW - 0.04, 1.98, 0.035, M.woodMat, ccx, 1.13, FZ + 0.008)
    wbox(colW - 0.15, 1.76, 0.014, M.woodMat, ccx, 1.13, FZ + 0.027).castShadow = false
    wbox(colW - 0.21, 1.66, 0.010, M.woodMat, ccx, 1.13, FZ + 0.030).castShadow = false
    // upper loft door (25%) + panel
    wbox(colW - 0.04, 0.55, 0.035, M.woodMat, ccx, 2.485, FZ + 0.008)
    wbox(colW - 0.15, 0.39, 0.014, M.woodMat, ccx, 2.485, FZ + 0.027).castShadow = false
    // chrome bar handle on the pair-split side
    const hx = ccx + handleSide[ci] * (colW / 2 - 0.10)
    wbox(0.028, 0.35, 0.028, M.chromeMat, hx, 1.25, FZ + 0.055)
    for (const hy of [1.11, 1.39]) {
      const post = new THREE.Mesh(new THREE.CylinderGeometry(0.009, 0.009, 0.04, 8), M.darkMetalMat)
      post.rotation.x = Math.PI / 2; post.position.set(hx, hy, FZ + 0.032); g.add(post)
      const ros = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.006, 10), M.chromeMat)
      ros.rotation.x = Math.PI / 2; ros.position.set(hx, hy, FZ + 0.030); g.add(ros)
    }
    // small chrome knob on the loft door
    const knob = new THREE.Mesh(new THREE.SphereGeometry(0.02, 12, 10), M.chromeMat)
    knob.position.set(ccx, 2.32, FZ + 0.045); knob.castShadow = true; g.add(knob)
  }
  // dentil blocks under the cornice + fluted side pilasters
  for (let i = 0; i < 16; i++)
    wbox(0.07, 0.06, 0.03, M.woodMat, X0 + 0.12 + i * (W2 - 0.24) / 15, 2.775, FZ + 0.01).castShadow = false
  for (const s of [-1, 1]) for (const off of [-0.05, 0, 0.05])
    wbox(0.018, 2.6, 0.012, M.woodMat, (s < 0 ? X0 + 0.055 : X1 - 0.055) + off * 0.4, 1.46, FZ + 0.008).castShadow = false
  // split beads at the 3 internal column gaps, full height
  for (let gi = 1; gi < NCOL; gi++)
    wbox(0.02, 2.65, 0.014, M.woodMat, X0 + colW * gi, 1.465, FZ + 0.028).castShadow = false
  // lock + brass key in the right-hand lower door, below its handle
  const kx = X0 + colW * 3.5 + (colW / 2 - 0.10) // right column handle x
  const plate = new THREE.Mesh(new THREE.CylinderGeometry(0.017, 0.017, 0.012, 12), M.chromeMat)
  plate.rotation.x = Math.PI / 2; plate.position.set(kx, 0.92, FZ + 0.032); g.add(plate)
  wbox(0.05, 0.11, 0.008, M.woodMat, kx, 0.92, FZ + 0.028).castShadow = false // escutcheon backplate
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.0045, 0.0045, 0.055, 8), M.brassMat)
  shaft.rotation.x = Math.PI / 2; shaft.position.set(kx, 0.92, FZ + 0.06); g.add(shaft)
  const bow = new THREE.Mesh(new THREE.TorusGeometry(0.015, 0.005, 8, 18), M.brassMat)
  bow.position.set(kx, 0.92, FZ + 0.092); bow.castShadow = true; g.add(bow)
  wbox(0.009, 0.009, 0.014, M.brassMat, kx, 0.91, FZ + 0.068).castShadow = false
  wbox(0.009, 0.009, 0.014, M.brassMat, kx, 0.93, FZ + 0.076).castShadow = false

  aoBlob(W2 + 0.4, DP + 0.7, CX, ZN + DP / 2 + 0.15, 0.005, 0.9)
}
