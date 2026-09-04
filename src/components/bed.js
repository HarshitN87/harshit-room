import * as THREE from 'three'
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js'
import { sheetTex } from './materials.js'

/* Harshit bed, enlarged (1.8 x 2.4m) on the MVP pipeline: low walnut frame,
   mattress with piping + buttons, 2 sculpted slate pillows west,
   purple blanket with fold ridges + pleated east drape (same fitting). */
export function buildBed(scene, ctx) {
  const { M, box, rbox, aoBlob } = ctx
  const BW = 2.2, BL = 2.4 // width (x), length (z) — stretched east toward the chair
  const g = new THREE.Group(); g.name = 'bed'; g.position.set(-0.85, 0, 0.25); scene.add(g)
  function bbox(w, h, d, mat, x, y, z) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m
  }
  function brbox(w, h, d, r, mat, x, y, z) {
    const m = new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 3, r), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m
  }
  const HX = BW / 2, HZ = BL / 2

  // frame rails + legs + slats
  brbox(0.06, 0.3, BL, 0.015, M.woodMat, -HX + 0.03, 0.22, 0)
  brbox(0.06, 0.3, BL, 0.015, M.woodMat, HX - 0.03, 0.22, 0)
  brbox(BW, 0.3, 0.06, 0.015, M.woodMat, 0, 0.22, HZ - 0.03)
  brbox(BW, 0.3, 0.06, 0.015, M.woodMat, 0, 0.22, -HZ + 0.03)
  for (const [lx, lz] of [[-HX + 0.05, -HZ + 0.05], [HX - 0.05, -HZ + 0.05], [-HX + 0.05, HZ - 0.05], [HX - 0.05, HZ - 0.05]]) {
    brbox(0.07, 0.12, 0.07, 0.015, M.woodMat, lx, 0.06, lz)
    const collar = new THREE.Mesh(new THREE.BoxGeometry(0.085, 0.02, 0.085), M.frameWoodMat)
    collar.position.set(lx, 0.125, lz); collar.castShadow = true; g.add(collar)
    const ft = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.055, 0.02, 12), M.darkMetalMat)
    ft.position.set(lx, 0.01, lz); g.add(ft)
  }
  for (let i = 0; i < 6; i++) bbox(BW - 0.12, 0.03, 0.1, M.frameWoodMat, 0, 0.33, -HZ + 0.25 + i * (BL - 0.5) / 5).castShadow = false
  // mattress + piping + buttons
  const MW = BW - 0.06, ML = BL - 0.08
  brbox(MW, 0.18, ML, 0.05, M.sheetMat, 0, 0.45, 0)
  const welt = new THREE.MeshStandardMaterial({ color: 0xcfc6b2, roughness: 0.9 })
  bbox(MW, 0.02, 0.02, welt, 0, 0.45, ML / 2).castShadow = false
  bbox(MW, 0.02, 0.02, welt, 0, 0.45, -ML / 2).castShadow = false
  bbox(0.02, 0.02, ML, welt, -MW / 2, 0.45, 0).castShadow = false
  bbox(0.02, 0.02, ML, welt, MW / 2, 0.45, 0).castShadow = false
  // side rail cap moldings + mattress side tufts
  for (const s of [-1, 1]) bbox(0.075, 0.018, BL - 0.06, M.frameWoodMat, s * (HX - 0.03), 0.378, 0).castShadow = false
  for (const s of [-1, 1]) for (let j = 0; j < 4; j++) {
    const tb = new THREE.Mesh(new THREE.SphereGeometry(0.012, 10, 8), welt)
    tb.scale.set(0.5, 1, 1); tb.position.set(s * (MW / 2 + 0.002), 0.45, -0.75 + j * 0.5); g.add(tb)
  }
  // mattress top buttons
  for (let i = 0; i < 8; i++) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.013, 10, 8), welt)
    b.scale.set(1, 0.5, 1); b.position.set(-0.70 + (i % 4) * 0.47, 0.545, i < 4 ? -0.35 : 0.35); g.add(b)
  }

  // sculpted pillows (west end)
  function pillow(mat, z, ry = 0) {
    const grp = new THREE.Group()
    grp.position.set(-MW / 2 + 0.28, 0.62, z); grp.rotation.y = ry; grp.rotation.z = 0.22
    const geo = new RoundedBoxGeometry(0.36, 0.15, 0.58, 5, 0.065)
    const pp = geo.attributes.position
    const v = new THREE.Vector3()
    for (let i = 0; i < pp.count; i++) {
      v.fromBufferAttribute(pp, i)
      const nx = THREE.MathUtils.clamp(v.x / 0.18, -1, 1)
      const nz = THREE.MathUtils.clamp(v.z / 0.29, -1, 1)
      const bulge = Math.cos(nx * Math.PI * 0.5) * Math.cos(nz * Math.PI * 0.5)
      v.y += Math.sign(v.y) * bulge * 0.032 + Math.sin(v.x * 30 + z * 5) * 0.0025 * bulge
      pp.setXYZ(i, v.x, v.y, v.z)
    }
    geo.computeVertexNormals()
    const pmat = mat.clone(); pmat.bumpMap = sheetTex; pmat.bumpScale = 0.25
    const pm = new THREE.Mesh(geo, pmat)
    pm.castShadow = pm.receiveShadow = true; grp.add(pm)
    const flange = new THREE.Mesh(new RoundedBoxGeometry(0.42, 0.032, 0.64, 2, 0.014), pmat)
    flange.position.y = -0.05; flange.castShadow = true; grp.add(flange)
    const dimple = new THREE.Mesh(new THREE.SphereGeometry(0.018, 10, 8), pmat)
    dimple.scale.set(1, 0.4, 1); dimple.position.y = 0.095; grp.add(dimple)
    g.add(grp)
  }
  pillow(M.slateMat, -0.55, 0.06)
  pillow(M.slateMat, 0.55, -0.06)

  // purple blanket: wavy top + hem + fold ridges + pleated east drape
  {
    const bg = new THREE.PlaneGeometry(MW - 0.02, 1.9, 22, 18)
    const p = bg.attributes.position
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i), y = p.getY(i)
      p.setZ(i, Math.sin(x * 9) * 0.012 + Math.cos(y * 7 + x * 4) * 0.014 + Math.sin(x * 23 + y * 17) * 0.005)
    }
    bg.computeVertexNormals()
    const blanket = new THREE.Mesh(bg, M.purpleMat)
    blanket.rotation.x = -Math.PI / 2; blanket.position.set(0.03, 0.565, 0.2)
    blanket.castShadow = blanket.receiveShadow = true; g.add(blanket)
    const skirt = brbox(MW - 0.02, 0.06, 1.9, 0.02, M.purpleMat, 0.03, 0.53, 0.2)
    skirt.castShadow = true
    bbox(MW - 0.04, 0.012, 0.03, M.purpleMat, 0.03, 0.56, 1.12).castShadow = false // hem
  bbox(MW - 0.04, 0.008, 0.012, M.purpleMat, 0.03, 0.572, 1.06).castShadow = false // stitch line
    for (let i = 0; i < 7; i++) {
      const ridge = new THREE.Mesh(new THREE.CapsuleGeometry(0.016, MW - 0.2, 4, 10), M.purpleMat)
      ridge.rotation.z = Math.PI / 2; ridge.rotation.y = 0.03 * Math.sin(i * 2.1)
      ridge.position.set(0.03, 0.578 + 0.006 * Math.sin(i * 1.4), -0.55 + i * 0.25)
      ridge.castShadow = true; g.add(ridge)
    }
    // east drape + pleats
    const drape = new THREE.Mesh(new THREE.PlaneGeometry(1.9, 0.30, 18, 4), M.purpleMat)
    {
      const dp = drape.geometry.attributes.position
      for (let i = 0; i < dp.count; i++) dp.setZ(i, Math.sin(dp.getX(i) * 18) * 0.018)
      drape.geometry.computeVertexNormals()
    }
    drape.rotation.y = -Math.PI / 2; drape.position.set(MW / 2 + 0.005, 0.40, 0.2)
    drape.castShadow = drape.receiveShadow = true; g.add(drape)
    for (let i = 0; i < 6; i++) {
      const pleat = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.28, 0.07), M.purpleMat)
      pleat.position.set(MW / 2 + 0.01 + 0.008 * Math.sin(i * 1.8), 0.40, -0.5 + i * 0.28)
      pleat.castShadow = true; g.add(pleat)
    }
  }
  aoBlob(BW + 0.3, BL + 0.3, -0.85, 0.25, 0.005, 0.9)
}
