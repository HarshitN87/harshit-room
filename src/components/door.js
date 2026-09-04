import * as THREE from 'three'

/* North-wall door on the MVP pipeline: architrave, leaf ajar on 3 hinges,
   shaker insets, lever + rosettes (same fitting as before). */
export function buildDoor(scene, ctx, layout) {
  const { M, box, rbox } = ctx
  const { ZN } = layout
  const X0 = 0.5, X1 = 1.5, DH = 2.2, CX = (X0 + X1) / 2

  // architrave
  rbox(0.09, DH + 0.06, 0.16, 0.015, M.frameWoodMat, X0 - 0.045, DH / 2, ZN, scene).castShadow = false
  rbox(0.09, DH + 0.06, 0.16, 0.015, M.frameWoodMat, X1 + 0.045, DH / 2, ZN, scene).castShadow = false
  rbox(X1 - X0 + 0.18, 0.09, 0.16, 0.015, M.frameWoodMat, CX, DH + 0.045, ZN, scene).castShadow = false
  // inner jamb liners
  box(0.03, DH, 0.14, M.frameWoodMat, X0 + 0.015, DH / 2, ZN, scene).castShadow = false
  box(0.03, DH, 0.14, M.frameWoodMat, X1 - 0.015, DH / 2, ZN, scene).castShadow = false

  // leaf hinged at x=X1, opened into the room
  const leaf = new THREE.Group()
  leaf.position.set(X1, 0, ZN + 0.02)
  leaf.rotation.y = 0.5
  scene.add(leaf)
  function lbox(w, h, d, mat, x, y, z) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; leaf.add(m); return m
  }
  const LW = X1 - X0 - 0.04
  lbox(LW, DH - 0.06, 0.045, M.frameWoodMat, -LW / 2, DH / 2, 0)
  // shaker insets + rims
  for (const [iy, ih] of [[1.62, 0.62], [0.78, 0.8]]) {
    lbox(LW * 0.62, ih, 0.012, M.edgeBandMat, -LW / 2, iy, 0.024).castShadow = false
    lbox(LW * 0.70, ih + 0.07, 0.008, M.frameWoodMat, -LW / 2, iy, 0.022).castShadow = false
  }
  // lever + rosettes + keyhole
  const leverX = -LW + 0.12
  const rose = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.012, 16), M.chromeMat)
  rose.rotation.x = Math.PI / 2; rose.position.set(leverX, 1.02, 0.028); leaf.add(rose)
  const rose2 = rose.clone(); rose2.position.z = -0.028; leaf.add(rose2)
  const lever = new THREE.Mesh(new THREE.BoxGeometry(0.025, 0.03, 0.15), M.chromeMat)
  lever.position.set(leverX, 1.03, 0.10); lever.castShadow = true; leaf.add(lever)
  const knob = new THREE.Mesh(new THREE.SphereGeometry(0.02, 12, 10), M.chromeMat)
  knob.position.set(leverX, 1.03, 0.175); leaf.add(knob)
  // hinges on the jamb side
  for (const hy of [0.5, 1.1, 1.8]) {
    const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.09, 10), M.darkMetalMat)
    barrel.position.set(X1, hy, ZN + 0.02); barrel.castShadow = true; scene.add(barrel)
    box(0.05, 0.07, 0.008, M.darkMetalMat, X1 - 0.025, hy, ZN + 0.03, scene).castShadow = false
  }
  // bottom gap shadow
  const gap = new THREE.Mesh(new THREE.BoxGeometry(LW, 0.05, 0.05),
    new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.35, depthWrite: false }))
  gap.position.set(-LW / 2, 0.025, 0); leaf.add(gap)
}
