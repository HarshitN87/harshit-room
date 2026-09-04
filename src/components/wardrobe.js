import * as THREE from 'three'

/* Harshit wardrobe on the MVP pipeline: north-wall wooden unit, 2 columns,
   drawers + inset shaker doors, bar handles, lock with key (same fitting). */
export function buildWardrobe(scene, ctx, layout) {
  const { M, box, rbox, aoBlob } = ctx
  const { ZN } = layout
  const CX = -1.0, W2 = 1.6, DP = 0.5, HT = 2.6
  const FZ = ZN + DP // front face z ≈ -1.5

  const g = new THREE.Group(); g.name = 'wardrobe'; scene.add(g)
  function wbox(w, h, d, mat, x, y, z, r = 0.008) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m
  }
  function wrbox(w, h, d, rr, mat, x, y, z) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m
  }

  wrbox(W2, HT, DP, 0.02, M.woodMat, CX, HT / 2, ZN + DP / 2) // carcass
  wrbox(W2 + 0.08, 0.07, DP + 0.08, 0.02, M.frameWoodMat, CX, HT + 0.035, ZN + DP / 2) // crown
  wrbox(W2 - 0.04, 0.09, DP - 0.02, 0.015, M.frameWoodMat, CX, 0.045, ZN + DP / 2) // plinth
  wbox(W2 + 0.02, 0.012, 0.02, M.edgeBandMat, CX, 0.1, FZ + 0.002).castShadow = false
  // side trims
  for (const s of [-1, 1]) wbox(0.03, HT - 0.2, DP - 0.06, M.frameWoodMat, CX + s * (W2 / 2 - 0.015), HT / 2, ZN + DP / 2)

  const colW = W2 / 2
  for (const ci of [0, 1]) {
    const ccx = CX - W2 / 2 + colW / 2 + ci * colW
    // drawer + inset
    wrbox(colW - 0.06, 0.24, 0.03, 0.01, M.woodMat, ccx, 0.32, FZ + 0.008)
    wbox(colW - 0.20, 0.15, 0.012, M.frameWoodMat, ccx, 0.32, FZ + 0.012).castShadow = false
    // lower door + inset + bead
    wrbox(colW - 0.06, 1.25, 0.03, 0.01, M.woodMat, ccx, 1.10, FZ + 0.008)
    wbox(colW - 0.20, 1.05, 0.012, M.frameWoodMat, ccx, 1.10, FZ + 0.012).castShadow = false
    wbox(colW - 0.26, 0.95, 0.008, M.woodMat, ccx, 1.10, FZ + 0.014).castShadow = false
    // upper door + inset
    wrbox(colW - 0.06, 0.62, 0.03, 0.01, M.woodMat, ccx, 2.10, FZ + 0.008)
    wbox(colW - 0.20, 0.46, 0.012, M.frameWoodMat, ccx, 2.10, FZ + 0.012).castShadow = false
    // bar handles
    const hx = ccx + (ci === 0 ? colW / 2 - 0.12 : -(colW / 2 - 0.12))
    wbox(0.025, 0.16, 0.025, M.chromeMat, hx, 1.10, FZ + 0.05)
    for (const hy of [1.03, 1.17]) {
      const post = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.035, 8), M.darkMetalMat)
      post.rotation.x = Math.PI / 2; post.position.set(hx, hy, FZ + 0.03); g.add(post)
    }
    wbox(0.10, 0.025, 0.025, M.chromeMat, ccx, 2.10, FZ + 0.045)
  }
  // center gap bead + drawer gap shadows
  wbox(0.02, 2.2, 0.012, M.edgeBandMat, CX, 1.35, FZ + 0.006).castShadow = false
  wbox(W2 - 0.06, 0.014, 0.012, new THREE.MeshBasicMaterial({ color: 0x000000 }), CX, 0.47, FZ + 0.006).castShadow = false
  // lock + key in right column
  const kx = CX + colW - 0.22
  const plate = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.01, 12), M.chromeMat)
  plate.rotation.x = Math.PI / 2; plate.position.set(kx, 1.32, FZ + 0.03); g.add(plate)
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.004, 0.004, 0.05, 8), M.brassMat)
  shaft.rotation.x = Math.PI / 2; shaft.position.set(kx, 1.32, FZ + 0.055); g.add(shaft)
  const bow = new THREE.Mesh(new THREE.TorusGeometry(0.014, 0.0045, 8, 18), M.brassMat)
  bow.position.set(kx, 1.32, FZ + 0.085); g.add(bow)
  for (const [ty, tz] of [[1.312, 0.062], [1.328, 0.068]])
    wbox(0.008, 0.008, 0.012, M.brassMat, kx, ty, FZ + tz).castShadow = false

  aoBlob(W2 + 0.3, DP + 0.5, CX, ZN + DP / 2 + 0.1, 0.005, 0.9)
}
