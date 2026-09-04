import * as THREE from 'three'
import { glowTex } from './materials.js'

/* Harshit room shell on the MVP pipeline: 4x4x3 dollhouse, west wall with
   window opening, north wall with door opening, starburst tile floor,
   skirting, ceiling pendant near window, LED strip, red bucket.
   (TV / fan / almirah from the MVP are NOT ported — different room.) */
export function buildShell(scene, ctx) {
  const { M, box, rbox, aoBlob, W, D, H } = ctx

  const ground = new THREE.Mesh(new THREE.CircleGeometry(14, 48),
    new THREE.MeshStandardMaterial({ color: 0x23252e, roughness: 1 }))
  ground.rotation.x = -Math.PI / 2; ground.position.y = -0.41; ground.receiveShadow = true
  scene.add(ground)

  const floor = new THREE.Mesh(new THREE.BoxGeometry(W, 0.12, D),
    new THREE.MeshPhysicalMaterial({ map: M.starTileTex, roughnessMap: M.starTileRough, roughness: 0.65, metalness: 0.04, clearcoat: 0.14, clearcoatRoughness: 0.55 }))
  floor.position.y = -0.06; floor.receiveShadow = true
  scene.add(floor)
  rbox(W + 0.5, 0.26, D + 0.5, 0.03, new THREE.MeshStandardMaterial({ color: 0x2b2e3a, roughness: 0.85 }), 0, -0.25, 0)
  box(W + 0.54, 0.04, D + 0.54, new THREE.MeshStandardMaterial({ color: 0x3d4152, roughness: 0.7 }), 0, -0.1, 0)

  const T = 0.12 // wall thickness
  const XW = -W / 2, ZN = -D / 2

  /* ---- west wall (x=XW) with window hole: z -1.2..0.2, y 0.8..2.3 ---- */
  const winZ0 = -0.8, winZ1 = 1.0, winY0 = 0.7, winY1 = 2.4
  const winCZ = (winZ0 + winZ1) / 2, winW = winZ1 - winZ0
  rbox(T, H, (winZ0 + D / 2), 0.015, M.wallMat, XW, H / 2, (-D / 2 + winZ0) / 2, scene).castShadow = false
  rbox(T, H, (D / 2 - winZ1), 0.015, M.wallMat, XW, H / 2, ((winZ1 + D / 2) / 2), scene).castShadow = false
  rbox(T, winY0, winW, 0.015, M.wallMat, XW, winY0 / 2, winCZ, scene).castShadow = false
  rbox(T, H - winY1, winW, 0.015, M.wallMat, XW, (winY1 + H) / 2, winCZ, scene).castShadow = false
  // reveal liners
  box(T + 0.02, 0.03, winW, M.skirtMat, XW, winY0 + 0.015, winCZ, scene).castShadow = false
  box(T + 0.02, 0.03, winW, M.skirtMat, XW, winY1 - 0.015, winCZ, scene).castShadow = false

  /* ---- north wall (z=ZN) with door hole: x 0.5..1.5, y 0..2.2 ---- */
  const doorX0 = 0.5, doorX1 = 1.5, doorH = 2.2
  rbox(doorX0 + W / 2, H, T, 0.015, M.wallMat, (-W / 2 + doorX0) / 2, H / 2, ZN, scene).castShadow = false
  rbox(W / 2 - doorX1, H, T, 0.015, M.wallMat, ((doorX1 + W / 2) / 2), H / 2, ZN, scene).castShadow = false
  rbox(doorX1 - doorX0, H - doorH, T, 0.015, M.wallMat, (doorX0 + doorX1) / 2, (doorH + H) / 2, ZN, scene).castShadow = false

  /* ---- skirting + top trim ---- */
  rbox(0.16, 0.1, D, 0.015, M.skirtMat, XW + 0.06, 0.05, 0, scene).castShadow = false
  rbox(W, 0.1, 0.16, 0.015, M.skirtMat, 0, 0.05, ZN + 0.06, scene).castShadow = false
  box(W, 0.06, 0.14, M.skirtMat, 0, H - 0.03, ZN, scene).castShadow = false
  box(0.14, 0.06, D, M.skirtMat, XW, H - 0.03, 0, scene).castShadow = false
  // contact-shadow gradient where walls meet floor
  {
    const c = document.createElement('canvas'); c.width = 4; c.height = 64
    const g2 = c.getContext('2d')
    const gr = g2.createLinearGradient(0, 0, 0, 64)
    gr.addColorStop(0, 'rgba(0,0,0,0.32)'); gr.addColorStop(1, 'rgba(0,0,0,0)')
    g2.fillStyle = gr; g2.fillRect(0, 0, 4, 64)
    const stripTex = new THREE.CanvasTexture(c)
    const stripMat = new THREE.MeshBasicMaterial({ map: stripTex, transparent: true, depthWrite: false, opacity: 0.5 })
    const s1 = new THREE.Mesh(new THREE.PlaneGeometry(W, 0.22), stripMat)
    s1.position.set(0, 0.11, ZN + 0.145); scene.add(s1)
    const s2 = new THREE.Mesh(new THREE.PlaneGeometry(D, 0.22), stripMat)
    s2.rotation.y = Math.PI / 2; s2.position.set(XW + 0.145, 0.11, 0); scene.add(s2)
  }

  /* ---- ceiling pendant near window (same fitting as before) ---- */
  const pendG = new THREE.Group()
  pendG.name = 'ceilingPendant'
  pendG.position.set(-1.5, 0, 0.1)
  scene.add(pendG)
  function ppart(geo, mat, x, y, z) {
    const m = new THREE.Mesh(geo, mat)
    m.position.set(x, y, z); m.castShadow = true; pendG.add(m); return m
  }
  ppart(new THREE.CylinderGeometry(0.05, 0.06, 0.03, 16), M.skirtMat, 0, H - 0.015, 0)
  ppart(new THREE.CylinderGeometry(0.008, 0.008, 0.24, 8), M.darkMetalMat, 0, H - 0.15, 0)
  ppart(new THREE.CylinderGeometry(0.035, 0.042, 0.06, 16), M.skirtMat, 0, 2.70, 0)
  ppart(new THREE.TorusGeometry(0.037, 0.006, 8, 20), M.chromeMat, 0, 2.672, 0).rotation.x = Math.PI / 2
  const bulbGeo = new THREE.SphereGeometry(0.055, 20, 16)
  bulbGeo.scale(1, 1.25, 1)
  const bulbMesh = ppart(bulbGeo, M.warmBulbMat, 0, 2.60, 0)
  const filament = ppart(new THREE.TorusGeometry(0.02, 0.005, 6, 14),
    new THREE.MeshBasicMaterial({ color: 0xfff4c2 }), 0, 2.60, 0)
  filament.rotation.x = Math.PI / 2
  const bulbGlow = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: 0xffcf7a, transparent: true, opacity: 0.45, depthWrite: false }))
  bulbGlow.scale.set(0.7, 0.7, 1); bulbGlow.position.set(0, 2.60, 0); pendG.add(bulbGlow)

  /* ---- LED strip along north wall (same fitting) ---- */
  const ledG = new THREE.Group(); ledG.position.set(-0.75, 2.97, ZN + 0.30); scene.add(ledG)
  function lpart(w, h, d, mat, x, y, z) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)
    m.position.set(x, y, z); ledG.add(m); return m
  }
  lpart(2.0, 0.03, 0.03, M.darkMetalMat, 0, 0, 0)
  lpart(2.0, 0.012, 0.008, new THREE.MeshStandardMaterial({ color: 0xf3e3c2, roughness: 0.6 }), 0, 0.012, 0.012)
  for (let i = 0; i < 24; i++)
    lpart(0.035, 0.014, 0.01, i % 3 ? M.pinkLedMat : M.cyanLedMat, -0.92 + i * 0.08, 0.012, 0.014).castShadow = false
  lpart(0.04, 0.035, 0.035, M.blackPlasticMat, -1.0, 0, 0)
  lpart(0.04, 0.035, 0.035, M.blackPlasticMat, 1.0, 0, 0)
  const ledGlow = new THREE.PointLight(0xff2f6d, 2.5, 5, 1.9)
  ledGlow.position.set(-0.75, 2.85, ZN + 0.7); scene.add(ledGlow)

  /* ---- red bucket east of wardrobe (same fitting) ---- */
  const bkG = new THREE.Group(); bkG.position.set(0.8, 0, -1.0); scene.add(bkG)
  function bpart(geo, mat, x, y, z) {
    const m = new THREE.Mesh(geo, mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; bkG.add(m); return m
  }
  bpart(new THREE.CylinderGeometry(0.14, 0.115, 0.28, 24, 1, true), new THREE.MeshStandardMaterial({ color: 0xd91f1f, roughness: 0.42, side: THREE.DoubleSide }), 0, 0.15, 0)
  bpart(new THREE.CylinderGeometry(0.115, 0.115, 0.012, 24), M.redBucketMat, 0, 0.016, 0)
  const rim = bpart(new THREE.TorusGeometry(0.14, 0.009, 8, 28), M.redBucketMat, 0, 0.29, 0)
  rim.rotation.x = Math.PI / 2
  for (let i = 0; i < 12; i++) {
    const a = (i / 12) * Math.PI * 2
    const rib = bpart(new THREE.BoxGeometry(0.012, 0.12, 0.012), M.redBucketMat, Math.cos(a) * 0.142, 0.15, Math.sin(a) * 0.142)
    rib.rotation.y = -a
  }
  bpart(new THREE.CylinderGeometry(0.125, 0.125, 0.006, 24), new THREE.MeshStandardMaterial({ color: 0x3d0808, roughness: 1 }), 0, 0.035, 0).castShadow = false
  aoBlob(0.45, 0.45, 0.8, -1.0, 0.005, 0.9)

  // floating rose mount (open dollhouse top, MVP trick) for pendant wire
  {
    const rose = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.11, 0.04, 20), M.ceilMat)
    rose.position.set(-1.5, H + 0.06, 0.1); scene.add(rose)
  }

  return { bulbMesh, bulbGlow, ledGlow, winZ0, winZ1, winY0, winY1, winCZ, XW, ZN }
}
