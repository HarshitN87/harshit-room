import * as THREE from 'three'
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js'
import { clothWeaveTex } from './materials.js'

/* Harshit chair, plush executive rebuild on the MVP pipeline: chrome
   5-star base with braked twin wheels, mechanism + levers, thick tufted
   seat cushion with welt piping, padded 2-panel back with lumbar pillow,
   wide headrest on chrome posts, loop arms with stitched pads.
   Faces +x toward the desk (same placement as before). */
export function buildChair(scene, ctx) {
  const { M, box, aoBlob } = ctx
  const fabric = new THREE.MeshStandardMaterial({ color: 0x23242a, roughness: 0.95, bumpMap: clothWeaveTex, bumpScale: 0.18 })
  const fabricSide = new THREE.MeshStandardMaterial({ color: 0x1b1c21, roughness: 0.95, bumpMap: clothWeaveTex, bumpScale: 0.15 })
  const weltMat = new THREE.MeshStandardMaterial({ color: 0x3a3b42, roughness: 0.8 })
  const stitchMat = new THREE.MeshStandardMaterial({ color: 0x8a8b93, roughness: 0.8 })
  const g = new THREE.Group(); g.name = 'chair'
  g.position.set(0.72, 0, 0.35); g.rotation.y = Math.PI / 2
  scene.add(g)
  function cbox(w, h, d, mat, x, y, z) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m
  }
  function crbox(w, h, d, r, mat, x, y, z) {
    const m = new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 4, r), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m
  }
  function ccyl(rt, rb, h, mat, x, y, z, seg = 14) {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg), mat)
    m.position.set(x, y, z); m.castShadow = true; g.add(m); return m
  }

  // chrome 5-star base + braked twin wheels
  ccyl(0.05, 0.06, 0.05, M.chromeMat, 0, 0.10, 0, 16)
  for (let i = 0; i < 5; i++) {
    const a = (i / 5) * Math.PI * 2 + 0.3
    const leg = cbox(0.30, 0.03, 0.055, M.chromeMat, Math.cos(a) * 0.18, 0.085, Math.sin(a) * 0.18)
    leg.rotation.y = -a
    const tip = new THREE.Mesh(new THREE.SphereGeometry(0.028, 12, 10), M.chromeMat)
    tip.position.set(Math.cos(a) * 0.325, 0.085, Math.sin(a) * 0.325); g.add(tip)
    const fx = Math.cos(a) * 0.33, fz = Math.sin(a) * 0.33
    const fork = cbox(0.035, 0.07, 0.11, M.blackPlasticMat, fx, 0.055, fz)
    fork.rotation.y = -a
    for (const s of [-1, 1]) {
      const off = new THREE.Vector3(-Math.sin(a), 0, Math.cos(a)).multiplyScalar(s * 0.030)
      const wh = ccyl(0.037, 0.037, 0.022, M.blackPlasticMat, fx + off.x, 0.037, fz + off.z, 18)
      wh.rotation.x = Math.PI / 2; wh.rotation.y = -a
      const hub = ccyl(0.013, 0.013, 0.024, M.chromeMat, fx + off.x, 0.037, fz + off.z, 10)
      hub.rotation.x = Math.PI / 2; hub.rotation.y = -a
      const brake = cbox(0.02, 0.012, 0.03, new THREE.MeshStandardMaterial({ color: 0xb03030, roughness: 0.6 }), fx + off.x, 0.068, fz + off.z)
      brake.rotation.y = -a
    }
  }
  // gas lift + telescopic covers + mechanism
  ccyl(0.026, 0.026, 0.22, M.chromeMat, 0, 0.23, 0)
  for (let bi = 0; bi < 3; bi++) ccyl(0.038 - bi * 0.003, 0.042 - bi * 0.003, 0.03, M.blackPlasticMat, 0, 0.145 + bi * 0.032, 0)
  ccyl(0.045, 0.05, 0.09, M.blackPlasticMat, 0, 0.12, 0)
  ccyl(0.04, 0.045, 0.07, M.blackPlasticMat, 0, 0.30, 0)
  crbox(0.30, 0.07, 0.28, 0.02, M.darkMetalMat, 0, 0.375, -0.02) // tilt mechanism
  ccyl(0.035, 0.035, 0.02, M.blackPlasticMat, 0, 0.345, 0.10, 12) // tension knob
  for (const s of [-1, 1]) {
    const lev = cbox(0.13, 0.012, 0.012, M.darkMetalMat, s * 0.20, 0.37, -0.10)
    lev.rotation.y = s * -0.35
    const grip = new THREE.Mesh(new THREE.SphereGeometry(0.014, 10, 8), M.blackPlasticMat)
    grip.position.set(s * 0.26, 0.37, -0.125); g.add(grip)
  }

  // thick seat cushion + welt piping + tufts + waterfall front
  crbox(0.56, 0.15, 0.54, 0.06, fabric, 0, 0.485, 0.02)
  crbox(0.50, 0.05, 0.10, 0.02, fabric, 0, 0.44, 0.28) // waterfall lip
  cbox(0.545, 0.018, 0.018, weltMat, 0, 0.44, 0.285).castShadow = false
  cbox(0.545, 0.018, 0.018, weltMat, 0, 0.44, -0.245).castShadow = false
  cbox(0.018, 0.018, 0.53, weltMat, -0.267, 0.44, 0.02).castShadow = false
  cbox(0.018, 0.018, 0.53, weltMat, 0.267, 0.44, 0.02).castShadow = false
  // double-needle stitch lines on the seat top
  for (const sz of [-0.16, 0.20]) {
    cbox(0.46, 0.004, 0.006, stitchMat, 0, 0.563, sz).castShadow = false
    cbox(0.46, 0.004, 0.006, stitchMat, 0, 0.563, sz + 0.018).castShadow = false
  }
  const tuft = new THREE.MeshStandardMaterial({ color: 0x101116, roughness: 0.9 })
  for (const [qx, qz] of [[-0.15, -0.08], [0.15, -0.08], [-0.15, 0.12], [0.15, 0.12]]) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.014, 10, 8), tuft)
    b.scale.set(1, 0.45, 1); b.position.set(qx, 0.562, qz); g.add(b)
  }
  // seat side bolsters
  for (const s of [-1, 1]) crbox(0.07, 0.09, 0.44, 0.03, fabricSide, s * 0.275, 0.50, 0.02)

  // loop arms: chrome supports + thick stitched pads
  for (const s of [-1, 1]) {
    const loopF = cbox(0.035, 0.24, 0.035, M.chromeMat, s * 0.30, 0.62, 0.16)
    loopF.rotation.x = 0.12
    const loopB = cbox(0.035, 0.26, 0.035, M.chromeMat, s * 0.30, 0.63, -0.14)
    loopB.rotation.x = -0.10
    crbox(0.09, 0.06, 0.36, 0.025, fabric, s * 0.30, 0.76, 0.02)
    cbox(0.07, 0.006, 0.30, stitchMat, s * 0.30, 0.792, 0.02).castShadow = false
    cbox(0.05, 0.03, 0.05, M.blackPlasticMat, s * 0.30, 0.52, 0.16) // height-adjust collar
    cbox(0.02, 0.014, 0.03, M.darkMetalMat, s * 0.335, 0.52, 0.16).rotation.y = s * 0.2 // paddle button
  }

  // backrest spine + padded panels + lumbar pillow + buttons
  cbox(0.06, 0.30, 0.05, M.blackPlasticMat, 0, 0.60, -0.28)
  const backG = new THREE.Group(); backG.position.set(0, 0.72, -0.30); backG.rotation.x = 0.10; g.add(backG)
  function bbox(w, h, d, mat, x, y, z) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; backG.add(m); return m
  }
  function brbox(w, h, d, r, mat, x, y, z) {
    const m = new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 4, r), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; backG.add(m); return m
  }
  brbox(0.54, 0.72, 0.10, 0.045, fabricSide, 0, 0.32, -0.02) // back shell
  brbox(0.48, 0.34, 0.10, 0.045, fabric, 0, 0.16, 0.03) // lumbar panel
  brbox(0.48, 0.32, 0.10, 0.045, fabric, 0, 0.50, 0.03) // upper panel
  bbox(0.46, 0.018, 0.018, weltMat, 0, 0.33, 0.075).castShadow = false // panel split welt
  for (const s of [-1, 1]) brbox(0.07, 0.62, 0.09, 0.03, fabricSide, s * 0.255, 0.33, 0.02) // side bolsters
  for (const [bx, by] of [[-0.13, 0.16], [0.13, 0.16], [-0.13, 0.50], [0.13, 0.50]]) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.013, 10, 8), tuft)
    b.scale.set(1, 1, 0.45); b.position.set(bx, by, 0.082); backG.add(b)
  }
  brbox(0.30, 0.12, 0.07, 0.03, fabric, 0, 0.10, 0.09) // lumbar pillow
  // headrest posts with slots + wide cushion
  for (const s of [-1, 1]) {
    bbox(0.03, 0.16, 0.025, M.chromeMat, s * 0.09, 0.75, -0.01)
    bbox(0.032, 0.02, 0.027, M.blackPlasticMat, s * 0.09, 0.70, -0.01).castShadow = false
  }
  brbox(0.32, 0.15, 0.09, 0.04, fabric, 0, 0.86, 0.0)
  bbox(0.28, 0.014, 0.014, weltMat, 0, 0.795, 0.045).castShadow = false
  bbox(0.24, 0.006, 0.006, stitchMat, 0, 0.885, 0.048).castShadow = false // headrest stitch

  aoBlob(1.0, 1.0, 0.72, 0.35, 0.005, 0.9)
}
