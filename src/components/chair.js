import * as THREE from 'three'
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js'

/* Harshit office chair on the MVP pipeline: 5-star base with twin wheels,
   gas lift, cushioned seat, arms, mesh back with ribs + headrest.
   Faces +x toward the desk (same placement as before). */
export function buildChair(scene, ctx) {
  const { M, box, aoBlob } = ctx
  const g = new THREE.Group(); g.name = 'chair'
  g.position.set(0.1, 0, 0.35); g.rotation.y = Math.PI / 2
  scene.add(g)
  function cbox(w, h, d, mat, x, y, z) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m
  }
  function crbox(w, h, d, r, mat, x, y, z) {
    const m = new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 3, r), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m
  }
  function ccyl(rt, rb, h, mat, x, y, z, seg = 14) {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg), mat)
    m.position.set(x, y, z); m.castShadow = true; g.add(m); return m
  }

  cbox(0.11, 0.05, 0.11, M.blackPlasticMat, 0, 0.09, 0) // hub
  ccyl(0.035, 0.035, 0.014, M.greyMetalMat, 0, 0.118, 0) // hub cap
  for (let i = 0; i < 5; i++) {
    const a = (i / 5) * Math.PI * 2
    const leg = cbox(0.27, 0.035, 0.05, M.blackPlasticMat, Math.cos(a) * 0.17, 0.085, Math.sin(a) * 0.17)
    leg.rotation.y = -a
    const fx = Math.cos(a) * 0.30, fz = Math.sin(a) * 0.30
    const fork = cbox(0.04, 0.06, 0.10, M.blackPlasticMat, fx, 0.06, fz)
    fork.rotation.y = -a
    for (const s of [-1, 1]) {
      const off = new THREE.Vector3(-Math.sin(a), 0, Math.cos(a)).multiplyScalar(s * 0.028)
      const wh = ccyl(0.035, 0.035, 0.02, M.blackPlasticMat, fx + off.x, 0.035, fz + off.z, 16)
      wh.rotation.x = Math.PI / 2; wh.rotation.y = -a
      const hub = ccyl(0.012, 0.012, 0.022, M.greyMetalMat, fx + off.x, 0.035, fz + off.z, 10)
      hub.rotation.x = Math.PI / 2; hub.rotation.y = -a
    }
  }
  ccyl(0.028, 0.028, 0.20, M.chromeMat, 0, 0.22, 0) // gas lift
  ccyl(0.033, 0.033, 0.025, M.darkMetalMat, 0, 0.30, 0)
  ccyl(0.033, 0.033, 0.025, M.darkMetalMat, 0, 0.15, 0)
  ccyl(0.045, 0.05, 0.10, M.blackPlasticMat, 0, 0.10, 0) // sheath
  // seat + piping + quilt dimples
  crbox(0.52, 0.09, 0.50, 0.035, M.blackPlasticMat, 0, 0.40, 0.02)
  cbox(0.50, 0.018, 0.018, M.greyMetalMat, 0, 0.40, 0.265).castShadow = false
  cbox(0.50, 0.018, 0.018, M.greyMetalMat, 0, 0.40, -0.225).castShadow = false
  for (const [qx, qz] of [[-0.14, -0.06], [0.14, -0.06], [-0.14, 0.12], [0.14, 0.12]])
    ccyl(0.012, 0.012, 0.008, M.blackPlasticMat, qx, 0.448, qz, 10).castShadow = false
  cbox(0.52, 0.05, 0.05, M.blackPlasticMat, 0, 0.42, 0.26) // front bolster
  // tilt lever + knob
  const lever = cbox(0.16, 0.014, 0.014, M.darkMetalMat, 0.20, 0.35, -0.12)
  lever.rotation.y = 0.3
  const knob = new THREE.Mesh(new THREE.SphereGeometry(0.018, 12, 10), M.blackPlasticMat)
  knob.position.set(0.27, 0.35, -0.16); g.add(knob)
  // arms
  for (const s of [-1, 1]) {
    cbox(0.035, 0.20, 0.035, M.blackPlasticMat, s * 0.26, 0.55, 0.03)
    crbox(0.07, 0.035, 0.30, 0.015, M.blackPlasticMat, s * 0.26, 0.66, 0.05)
    for (const sz of [-0.05, 0.15]) ccyl(0.006, 0.006, 0.006, M.darkMetalMat, s * 0.26, 0.68, sz, 8).castShadow = false
  }
  // backrest: spine + frame + mesh + ribs + lumbar + headrest
  cbox(0.05, 0.22, 0.04, M.blackPlasticMat, 0, 0.55, -0.26)
  cbox(0.035, 0.62, 0.035, M.blackPlasticMat, -0.24, 0.95, -0.27)
  cbox(0.035, 0.62, 0.035, M.blackPlasticMat, 0.24, 0.95, -0.27)
  cbox(0.51, 0.035, 0.035, M.blackPlasticMat, 0, 1.25, -0.27)
  cbox(0.51, 0.035, 0.035, M.blackPlasticMat, 0, 0.65, -0.27)
  const mesh = cbox(0.45, 0.57, 0.015, M.meshMat, 0, 0.95, -0.27)
  mesh.castShadow = false
  for (let i = 0; i < 5; i++) cbox(0.43, 0.022, 0.02, M.blackPlasticMat, 0, 0.73 + i * 0.11, -0.265).castShadow = false
  crbox(0.30, 0.13, 0.04, 0.015, M.blackPlasticMat, 0, 0.82, -0.25)
  for (const s of [-1, 1]) cbox(0.025, 0.07, 0.025, M.darkMetalMat, s * 0.09, 1.30, -0.27)
  crbox(0.30, 0.13, 0.06, 0.025, M.blackPlasticMat, 0, 1.38, -0.27)

  aoBlob(0.9, 0.9, 0.1, 0.35, 0.005, 0.9)
}
