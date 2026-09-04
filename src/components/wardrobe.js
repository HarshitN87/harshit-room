import * as THREE from 'three'

/* Harshit full-wall built-in wardrobe on the MVP pipeline: north wall from
   the west corner to the door frame (~2.5m), floor to ceiling, NO drawers —
   2 tall lower doors (75%) + 2 upper loft doors (25%), bar handles,
   brass key in the right door, cornice + plinth (same fitting). */
export function buildWardrobe(scene, ctx, layout) {
  const { M, box, aoBlob } = ctx
  const { ZN } = layout
  const X0 = -2.0, X1 = 0.5 // full wall except the door
  const CX = (X0 + X1) / 2, W2 = X1 - X0 // -0.75, 2.5
  const DP = 0.55, FZ = ZN + DP // front face z ≈ -1.45
  const H = 3

  const g = new THREE.Group(); g.name = 'wardrobe'; scene.add(g)
  function wbox(w, h, d, mat, x, y, z) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m
  }

  // carcass + plinth + cornice (scribed wall to wall)
  wbox(W2, 2.72, DP, M.woodMat, CX, 0.10 + 2.72 / 2, ZN + DP / 2)
  wbox(W2, 0.10, DP - 0.04, M.frameWoodMat, CX, 0.05, ZN + DP / 2) // plinth
  wbox(W2 - 0.02, 0.05, 0.06, M.edgeBandMat, CX, 0.115, FZ - 0.01).castShadow = false // plinth shadow line
  wbox(W2 + 0.06, 0.10, DP + 0.06, M.frameWoodMat, CX, 2.87, ZN + DP / 2) // cornice
  wbox(W2 + 0.02, 0.025, DP + 0.02, M.edgeBandMat, CX, 2.81, ZN + DP / 2).castShadow = false // cornice step
  // side scribes into the walls
  wbox(0.04, 2.82, DP, M.frameWoodMat, X0 + 0.02, 1.46, ZN + DP / 2)
  wbox(0.04, 2.82, DP, M.frameWoodMat, X1 - 0.02, 1.46, ZN + DP / 2)
  // mid rail dividing 75 / 25
  wbox(W2 - 0.04, 0.09, 0.03, M.frameWoodMat, CX, 2.165, FZ + 0.015)

  const colW = W2 / 2 // two columns, ~1.25m each
  for (const ci of [0, 1]) {
    const ccx = X0 + colW / 2 + ci * colW
    // lower door (75%) + recessed shaker panel + bead
    wbox(colW - 0.05, 2.0, 0.035, M.woodMat, ccx, 0.14 + 1.0, FZ + 0.008)
    wbox(colW - 0.22, 1.78, 0.014, M.frameWoodMat, ccx, 1.14, FZ + 0.027).castShadow = false
    wbox(colW - 0.30, 1.68, 0.010, M.woodMat, ccx, 1.14, FZ + 0.030).castShadow = false
    // upper loft door (25%) + inset
    wbox(colW - 0.05, 0.55, 0.035, M.woodMat, ccx, 2.21 + 0.275, FZ + 0.008)
    wbox(colW - 0.22, 0.39, 0.014, M.frameWoodMat, ccx, 2.485, FZ + 0.027).castShadow = false
    // long vertical bar handle near the center split
    const hx = ccx + (ci === 0 ? colW / 2 - 0.14 : -(colW / 2 - 0.14))
    wbox(0.028, 0.42, 0.028, M.chromeMat, hx, 1.25, FZ + 0.055)
    for (const hy of [1.08, 1.42]) {
      const post = new THREE.Mesh(new THREE.CylinderGeometry(0.009, 0.009, 0.04, 8), M.darkMetalMat)
      post.rotation.x = Math.PI / 2; post.position.set(hx, hy, FZ + 0.032); g.add(post)
    }
    // small knob on the loft door
    const knob = new THREE.Mesh(new THREE.SphereGeometry(0.02, 12, 10), M.chromeMat)
    knob.position.set(hx, 2.32, FZ + 0.045); knob.castShadow = true; g.add(knob)
  }
  // center split bead, full height
  wbox(0.024, 2.68, 0.014, M.edgeBandMat, CX, 1.47, FZ + 0.028).castShadow = false
  // lock + brass key in the right lower door
  const kx = X1 - 0.30
  const plate = new THREE.Mesh(new THREE.CylinderGeometry(0.017, 0.017, 0.012, 12), M.chromeMat)
  plate.rotation.x = Math.PI / 2; plate.position.set(kx, 1.30, FZ + 0.032); g.add(plate)
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.0045, 0.0045, 0.055, 8), M.brassMat)
  shaft.rotation.x = Math.PI / 2; shaft.position.set(kx, 1.30, FZ + 0.06); g.add(shaft)
  const bow = new THREE.Mesh(new THREE.TorusGeometry(0.015, 0.005, 8, 18), M.brassMat)
  bow.position.set(kx, 1.30, FZ + 0.092); bow.castShadow = true; g.add(bow)
  wbox(0.009, 0.009, 0.014, M.brassMat, kx, 1.29, FZ + 0.068).castShadow = false
  wbox(0.009, 0.009, 0.014, M.brassMat, kx, 1.31, FZ + 0.076).castShadow = false

  aoBlob(W2 + 0.4, DP + 0.7, CX, ZN + DP / 2 + 0.15, 0.005, 0.9)
}
