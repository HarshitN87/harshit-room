import * as THREE from 'three'

/* West-wall window, enlarged to align with the bed, on the MVP pipeline:
   frame, night glass, muntins, latch, sill, rod with rings, THREE curtains —
   green outer pair + pink middle (same three curtains). */
export function buildWindowWall(scene, ctx, layout) {
  const { M, box, rbox } = ctx
  const { XW, winCZ } = layout

  const winG = new THREE.Group()
  winG.position.set(XW, 0, winCZ)
  winG.rotation.y = Math.PI / 2 // local +z faces into the room (+x)
  scene.add(winG)
  function wbox(w, h, d, mat, x, y, z, parent = winG) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; parent.add(m); return m
  }
  function wrbox(w, h, d, r, mat, x, y, z, parent = winG) {
    return rbox(w, h, d, r, mat, x, y, z, parent)
  }

  const CY = 1.55
  // dark opening + glass (1.74 x 1.64)
  wrbox(1.84, 1.74, 0.05, 0.01, new THREE.MeshStandardMaterial({ color: 0x14161d, roughness: 0.9 }), 0, CY, 0, winG).castShadow = false
  const nightGlass = new THREE.Mesh(new THREE.PlaneGeometry(1.74, 1.64),
    new THREE.MeshStandardMaterial({ color: 0x0a1428, roughness: 0.55, metalness: 0.05, transparent: true, opacity: 0.94 }))
  nightGlass.position.set(0, CY, 0.028); winG.add(nightGlass)
  // moon + skyline outside
  {
    const c = document.createElement('canvas'); c.width = c.height = 128
    const g = c.getContext('2d')
    const lg = g.createLinearGradient(0, 128, 128, 0)
    lg.addColorStop(0.35, 'rgba(180,210,255,0)'); lg.addColorStop(0.5, 'rgba(180,210,255,0.35)'); lg.addColorStop(0.65, 'rgba(180,210,255,0)')
    g.fillStyle = lg; g.fillRect(0, 0, 128, 128)
    g.fillStyle = '#f4ead0'; g.beginPath(); g.arc(100, 26, 9, 0, Math.PI * 2); g.fill()
    g.fillStyle = 'rgba(255,255,255,0.85)'
    for (let i = 0; i < 22; i++) g.fillRect(Math.random() * 128, Math.random() * 55, 1, 1)
    g.fillStyle = '#0b1220'
    for (const [bx, bw, bh] of [[0, 22, 34], [24, 18, 46], [46, 24, 30], [72, 18, 42], [94, 20, 36], [112, 16, 28]]) g.fillRect(bx, 128 - bh, bw, bh)
    const t = new THREE.CanvasTexture(c)
    const streak = new THREE.Mesh(new THREE.PlaneGeometry(1.74, 1.64),
      new THREE.MeshBasicMaterial({ map: t, transparent: true, opacity: 0.55, depthWrite: false }))
    streak.position.set(0, CY, 0.031); winG.add(streak)
  }
  // frame + muntins (6 panes: 2 vertical + 1 horizontal) + architrave
  for (const [w, h, x, y] of [[1.96, 0.08, 0, CY + 0.91], [1.96, 0.08, 0, CY - 0.91], [0.08, 1.9, -0.94, CY], [0.08, 1.9, 0.94, CY]])
    wrbox(w, h, 0.1, 0.015, M.skirtMat, x, y, 0.02, winG)
  for (const mx of [-0.30, 0.30]) wrbox(0.04, 1.7, 0.05, 0.01, M.skirtMat, mx, CY, 0.025, winG).castShadow = false
  wbox(1.8, 0.04, 0.05, M.skirtMat, 0, CY, 0.025, winG).castShadow = false
  for (const sx of [-0.96, 0.96]) wbox(0.05, 1.98, 0.06, M.skirtMat, sx, CY, 0.01, winG).castShadow = false
  // latch
  wbox(0.03, 0.14, 0.04, M.darkMetalMat, 0.03, CY + 0.05, 0.06, winG)
  // sill nose + apron
  wrbox(2.06, 0.05, 0.22, 0.01, M.skirtMat, 0, 0.655, 0.1, winG).receiveShadow = true
  wbox(1.9, 0.07, 0.03, M.skirtMat, 0, 0.60, 0.02, winG).castShadow = false

  // rod + finials + brackets live in world space (along z)
  const rod = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 2.6, 12), M.darkMetalMat)
  rod.rotation.x = Math.PI / 2; rod.position.set(XW + 0.28, 2.56, winCZ); rod.castShadow = true; scene.add(rod)
  for (const s of [-1, 1]) {
    const f = new THREE.Mesh(new THREE.SphereGeometry(0.042, 16, 12), M.darkMetalMat)
    f.position.set(XW + 0.28, 2.56, winCZ + s * 1.3); f.castShadow = true; scene.add(f)
    const b = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.04, 0.04), M.darkMetalMat)
    b.position.set(XW + 0.14, 2.56, winCZ + s * 0.9); scene.add(b)
  }

  const curtains = []
  function curtain(mat, zc, w = 0.72, phase = 0) {
    const m = mat.clone()
    const geo = new THREE.PlaneGeometry(w, 1.9, 40, 6)
    geo.userData.base = geo.attributes.position.array.slice()
    geo.userData.phase = phase
    const mesh = new THREE.Mesh(geo, m)
    mesh.rotation.y = Math.PI / 2 // face into room
    mesh.position.set(XW + 0.28, 1.5, zc)
    mesh.castShadow = mesh.receiveShadow = true
    scene.add(mesh); curtains.push(mesh)
    const hem = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.035, w * 0.96), m)
    hem.position.set(XW + 0.28, 0.56, zc); scene.add(hem)
    const tape = new THREE.Mesh(new THREE.BoxGeometry(0.025, 0.07, w * 0.98), m)
    tape.position.set(XW + 0.28, 2.43, zc); tape.castShadow = true; scene.add(tape)
    for (let r = 0; r < 4; r++) {
      const ring = new THREE.Mesh(new THREE.TorusGeometry(0.032, 0.009, 8, 16), M.chromeMat)
      ring.position.set(XW + 0.28, 2.54, zc - w / 2 + 0.08 + r * (w - 0.16) / 3)
      ring.castShadow = true; scene.add(ring)
    }
    return mesh
  }
  curtain(M.tealCurtainMat, winCZ - 0.75, 0.72, 0) // green, left
  curtain(M.pinkCurtainMat, winCZ + 0.0, 0.72, 2.1) // pink, middle
  curtain(M.tealCurtainMat, winCZ + 0.75, 0.72, 4.2) // green, right

  function waveCurtains(t, wind) {
    for (const c of curtains) {
      const pos = c.geometry.attributes.position
      const base = c.geometry.userData.base
      const ph = c.geometry.userData.phase
      for (let i = 0; i < pos.count; i++) {
        const bx = base[i * 3], by = base[i * 3 + 1]
        const v = (0.95 - by) / 1.9
        const sway = Math.sin(t * (0.8 + wind * 2.2) + ph + by * 2.0) * (0.012 + wind * 0.05) * (0.3 + v)
        const fold = Math.sin(bx * 22 + ph) * 0.045 + Math.sin(bx * 7 + ph) * 0.03
        pos.setZ(i, fold * (1 + wind * 0.4) + sway)
        pos.setX(i, bx + Math.sin(t * 0.6 + ph + by) * wind * 0.03 * v)
      }
      pos.needsUpdate = true
      c.geometry.computeVertexNormals()
    }
  }
  return { curtains, waveCurtains, nightGlass }
}
