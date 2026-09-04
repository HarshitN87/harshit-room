import * as THREE from 'three'
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js'
import { aoTex } from './materials.js'

/* Mesh factories bound to a scene (same signatures as the old main.js helpers) */
export const makeHelpers = (scene) => {
  function box(w, h, d, mat, x, y, z, parent = scene) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true
    parent.add(m); return m
  }
  function rbox(w, h, d, r, mat, x, y, z, parent = scene) {
    const geo = new RoundedBoxGeometry(w, h, d, 3, Math.min(r, Math.min(w, h, d) / 2.01))
    const m = new THREE.Mesh(geo, mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true
    parent.add(m); return m
  }
  function aoBlob(w, d, x, z, y = 0.005, opacity = 1) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d),
      new THREE.MeshBasicMaterial({ map: aoTex, transparent: true, depthWrite: false, opacity }))
    m.rotation.x = -Math.PI / 2; m.position.set(x, y, z)
    scene.add(m); return m
  }
  return { box, rbox, aoBlob }
}
