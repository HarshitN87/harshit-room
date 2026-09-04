import * as THREE from 'three'
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js'
import { sheetTex } from './materials.js'

/* Harshit bed on the MVP pipeline: low walnut frame (no headboard),
   mattress with piping + buttons, 2 sculpted slate pillows west,
   purple blanket with fold ridges + pleated east drape (same fitting). */
export function buildBed(scene, ctx) {
  const { M, box, rbox, aoBlob } = ctx
  const g = new THREE.Group(); g.name = 'bed'; g.position.set(-1.2, 0, 0.1); scene.add(g)
  function bbox(w, h, d, mat, x, y, z) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m
  }
  function brbox(w, h, d, r, mat, x, y, z) {
    const m = new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 3, r), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m
  }

  // frame rails + legs + slats
  brbox(0.06, 0.3, 2.0, 0.015, M.woodMat, -0.72, 0.22, 0)
  brbox(0.06, 0.3, 2.0, 0.015, M.woodMat, 0.72, 0.22, 0)
  brbox(1.5, 0.3, 0.06, 0.015, M.woodMat, 0, 0.22, 0.97)
  brbox(1.5, 0.3, 0.06, 0.015, M.woodMat, 0, 0.22, -0.97)
  for (const [lx, lz] of [[-0.7, -0.92], [0.7, -0.92], [-0.7, 0.92], [0.7, 0.92]]) {
    brbox(0.07, 0.12, 0.07, 0.015, M.woodMat, lx, 0.06, lz)
    const ft = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.055, 0.02, 12), M.darkMetalMat)
    ft.position.set(lx, 0.01, lz); g.add(ft)
  }
  for (let i = 0; i < 5; i++) bbox(1.38, 0.03, 0.1, M.frameWoodMat, 0, 0.33, -0.72 + i * 0.36).castShadow = false
  // mattress + piping + buttons
  brbox(1.44, 0.18, 1.92, 0.05, M.sheetMat, 0, 0.45, 0)
  const welt = new THREE.MeshStandardMaterial({ color: 0xcfc6b2, roughness: 0.9 })
  bbox(1.44, 0.02, 0.02, welt, 0, 0.45, 0.955).castShadow = false
  bbox(1.44, 0.02, 0.02, welt, 0, 0.45, -0.955).castShadow = false
  bbox(0.02, 0.02, 1.92, welt, -0.715, 0.45, 0).castShadow = false
  bbox(0.02, 0.02, 1.92, welt, 0.715, 0.45, 0).castShadow = false
  for (let i = 0; i < 6; i++) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.013, 10, 8), welt)
    b.scale.set(1, 0.5, 1); b.position.set(-0.45 + (i % 3) * 0.45, 0.545, i < 3 ? -0.3 : 0.3); g.add(b)
  }

  // sculpted pillows (west end)
  function pillow(mat, z, ry = 0) {
    const grp = new THREE.Group()
    grp.position.set(-0.42, 0.62, z); grp.rotation.y = ry; grp.rotation.z = 0.22
    const geo = new RoundedBoxGeometry(0.34, 0.15, 0.55, 5, 0.065)
    const pp = geo.attributes.position
    const v = new THREE.Vector3()
    for (let i = 0; i < pp.count; i++) {
      v.fromBufferAttribute(pp, i)
      const nx = THREE.MathUtils.clamp(v.x / 0.17, -1, 1)
      const nz = THREE.MathUtils.clamp(v.z / 0.275, -1, 1)
      const bulge = Math.cos(nx * Math.PI * 0.5) * Math.cos(nz * Math.PI * 0.5)
      v.y += Math.sign(v.y) * bulge * 0.032 + Math.sin(v.x * 30 + z * 5) * 0.0025 * bulge
      pp.setXYZ(i, v.x, v.y, v.z)
    }
    geo.computeVertexNormals()
    const pmat = mat.clone(); pmat.bumpMap = sheetTex; pmat.bumpScale = 0.25
    const pm = new THREE.Mesh(geo, pmat)
    pm.castShadow = pm.receiveShadow = true; grp.add(pm)
    const flange = new THREE.Mesh(new RoundedBoxGeometry(0.40, 0.032, 0.61, 2, 0.014), pmat)
    flange.position.y = -0.05; flange.castShadow = true; grp.add(flange)
    const dimple = new THREE.Mesh(new THREE.SphereGeometry(0.018, 10, 8), pmat)
    dimple.scale.set(1, 0.4, 1); dimple.position.y = 0.095; grp.add(dimple)
    g.add(grp)
  }
  pillow(M.slateMat, -0.42, 0.06)
  pillow(M.slateMat, 0.42, -0.06)

  // purple blanket: wavy top + hem + fold ridges + pleated east drape
  {
    const bg = new THREE.PlaneGeometry(1.42, 1.5, 22, 18)
    const p = bg.attributes.position
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i), y = p.getY(i)
      p.setZ(i, Math.sin(x * 9) * 0.012 + Math.cos(y * 7 + x * 4) * 0.014 + Math.sin(x * 23 + y * 17) * 0.005)
    }
    bg.computeVertexNormals()
    const blanket = new THREE.Mesh(bg, M.purpleMat)
    blanket.rotation.x = -Math.PI / 2; blanket.position.set(0.02, 0.565, 0.18)
    blanket.castShadow = blanket.receiveShadow = true; g.add(blanket)
    const skirt = brbox(1.42, 0.06, 1.5, 0.02, M.purpleMat, 0.02, 0.53, 0.18)
    skirt.castShadow = true
    bbox(1.40, 0.012, 0.03, M.purpleMat, 0.02, 0.56, 0.90).castShadow = false // hem
    for (let i = 0; i < 6; i++) {
      const ridge = new THREE.Mesh(new THREE.CapsuleGeometry(0.016, 1.3, 4, 10), M.purpleMat)
      ridge.rotation.z = Math.PI / 2; ridge.rotation.y = 0.03 * Math.sin(i * 2.1)
      ridge.position.set(0.02, 0.578 + 0.006 * Math.sin(i * 1.4), -0.42 + i * 0.24)
      ridge.castShadow = true; g.add(ridge)
    }
    // east drape + pleats
    const drape = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 0.30, 18, 4), M.purpleMat)
    {
      const dp = drape.geometry.attributes.position
      for (let i = 0; i < dp.count; i++) {
        const x = dp.getX(i)
        dp.setZ(i, Math.sin(x * 18) * 0.018)
      }
      drape.geometry.computeVertexNormals()
    }
    drape.rotation.y = -Math.PI / 2; drape.position.set(0.745, 0.40, 0.18)
    drape.castShadow = drape.receiveShadow = true; g.add(drape)
    for (let i = 0; i < 5; i++) {
      const pleat = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.28, 0.07), M.purpleMat)
      pleat.position.set(0.75 + 0.008 * Math.sin(i * 1.8), 0.40, -0.38 + i * 0.28)
      pleat.castShadow = true; g.add(pleat)
    }
  }
  aoBlob(1.8, 2.3, -1.2, 0.1, 0.005, 0.9)
}
