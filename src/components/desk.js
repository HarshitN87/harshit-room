import * as THREE from 'three'
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js'
import { laptopScreenTex, glowTex } from './materials.js'

/* Harshit study desk on the MVP pipeline: walnut desk with drawers +
   tray + modesty, glowing laptop with code UI + 50 keys, mouse,
   articulated lamp (clickable), bottle, charger, books, mug, pens.
   Group faces -x toward the chair (same arrangement as before). */
export function buildDesk(scene, ctx) {
  const { M, box, rbox, aoBlob } = ctx
  const g = new THREE.Group(); g.name = 'desk'
  g.position.set(1.55, 0, 0.3); g.rotation.y = -Math.PI / 2
  scene.add(g)
  function dbox(w, h, d, mat, x, y, z) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m
  }
  function drbox(w, h, d, r, mat, x, y, z) {
    const m = new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 3, r), mat)
    m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; g.add(m); return m
  }
  const TOP = 0.735

  drbox(1.5, 0.035, 0.6, 0.01, M.woodMat, 0, TOP, 0) // top
  dbox(1.5, 0.018, 0.012, M.edgeBandMat, 0, TOP, 0.295).castShadow = false // front edge
  // cable grommet
  const grom = new THREE.Mesh(new THREE.TorusGeometry(0.028, 0.005, 8, 20), M.darkMetalMat)
  grom.rotation.x = Math.PI / 2; grom.position.set(0.42, TOP + 0.018, -0.18); g.add(grom)
  dbox(0.048, 0.004, 0.048, new THREE.MeshBasicMaterial({ color: 0x000000 }), 0.42, TOP + 0.017, -0.18).castShadow = false
  // side panels + feet + modesty + notch
  for (const s of [-1, 1]) {
    drbox(0.03, 0.70, 0.56, 0.008, M.woodMat, s * 0.735, 0.36, 0)
    dbox(0.04, 0.025, 0.5, M.darkMetalMat, s * 0.735, 0.013, 0)
  }
  dbox(1.42, 0.42, 0.03, M.woodMat, 0, 0.51, -0.265)
  dbox(0.36, 0.05, 0.032, new THREE.MeshBasicMaterial({ color: 0x000000 }), 0, 0.66, -0.265).castShadow = false
  // keyboard tray + rails + lip
  dbox(0.9, 0.02, 0.4, M.woodMat, -0.1, 0.66, 0.28)
  for (const s of [-1, 1]) dbox(0.025, 0.025, 0.4, M.darkMetalMat, -0.1 + s * 0.44, 0.66, 0.28)
  dbox(0.9, 0.03, 0.015, M.woodMat, -0.1, 0.668, 0.475)
  // keyboard tray felt liner + under-desk cable tray with drooping cable
  dbox(0.86, 0.004, 0.36, new THREE.MeshStandardMaterial({ color: 0x1e3a2f, roughness: 1 }), -0.1, 0.672, 0.28).castShadow = false
  dbox(0.7, 0.05, 0.08, M.darkMetalMat, 0.1, 0.68, -0.24)
  const dropCable = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([
    new THREE.Vector3(0.25, 0.68, -0.24), new THREE.Vector3(0.28, 0.45, -0.26),
    new THREE.Vector3(0.22, 0.2, -0.25), new THREE.Vector3(0.30, 0.02, -0.22)
  ]), 20, 0.005, 6), M.blackPlasticMat)
  g.add(dropCable)
  // footrest shelf + grips + riser
  dbox(0.95, 0.02, 0.44, M.woodMat, -0.1, 0.11, 0)
  for (let i = 0; i < 4; i++) dbox(0.88, 0.006, 0.025, M.blackPlasticMat, -0.1, 0.122, -0.15 + i * 0.1).castShadow = false
  dbox(0.95, 0.1, 0.02, M.woodMat, -0.1, 0.05, -0.21)
  // drawers box (right end) + gaps + drawer + cabinet
  dbox(0.36, 0.68, 0.54, M.woodMat, 0.55, 0.37, -0.01)
  dbox(0.35, 0.012, 0.5, new THREE.MeshBasicMaterial({ color: 0x000000 }), 0.55, 0.545, 0.02).castShadow = false
  drbox(0.33, 0.16, 0.02, 0.008, M.woodMat, 0.55, 0.63, 0.265)
  dbox(0.26, 0.11, 0.012, M.frameWoodMat, 0.55, 0.63, 0.272).castShadow = false
  dbox(0.10, 0.014, 0.014, M.chromeMat, 0.55, 0.63, 0.29)
  const lockPin = new THREE.Mesh(new THREE.CylinderGeometry(0.009, 0.009, 0.01, 10), M.chromeMat)
  lockPin.rotation.x = Math.PI / 2; lockPin.position.set(0.68, 0.68, 0.272); g.add(lockPin)
  drbox(0.33, 0.42, 0.02, 0.008, M.woodMat, 0.55, 0.28, 0.265)
  dbox(0.26, 0.34, 0.012, M.frameWoodMat, 0.55, 0.28, 0.272).castShadow = false
  dbox(0.014, 0.10, 0.014, M.chromeMat, 0.42, 0.28, 0.29)

  // desk mat
  dbox(0.42, 0.006, 0.52, M.blackPlasticMat, -0.12, TOP + 0.02, 0.02).castShadow = false
  dbox(0.40, 0.002, 0.008, M.greyMetalMat, -0.12, TOP + 0.023, -0.23).castShadow = false
  dbox(0.40, 0.002, 0.008, M.greyMetalMat, -0.12, TOP + 0.023, 0.27).castShadow = false

  /* ---- laptop (faces +z local, toward chair side) ---- */
  const lap = new THREE.Group(); lap.position.set(-0.15, TOP + 0.023, -0.02); g.add(lap)
  function lbox(w, h, d, mat, x, y, z, parent = lap) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat)
    m.position.set(x, y, z); m.castShadow = true; parent.add(m); return m
  }
  lbox(0.32, 0.018, 0.23, M.blackPlasticMat, 0, 0.009, 0.02)
  lbox(0.24, 0.002, 0.09, M.darkMetalMat, 0, 0.019, -0.03).castShadow = false // KB recess
  for (let r = 0; r < 5; r++) for (let c = 0; c < 10; c++) {
    if (r === 4 && c >= 3 && c <= 6) continue
    const accent = (r + c) % 8 === 0
    lbox(0.02, 0.004, 0.014,
      new THREE.MeshStandardMaterial({ color: accent ? 0xf2661a : 0x2a2a2e, roughness: 0.6 }),
      -0.108 + c * 0.024, 0.021, -0.062 + r * 0.019).castShadow = false
  }
  lbox(0.10, 0.004, 0.014, new THREE.MeshStandardMaterial({ color: 0x2a2a2e, roughness: 0.6 }), 0.012, 0.021, 0.033).castShadow = false
  // speaker grilles flanking the keyboard
  for (const s of [-1, 1]) {
    lbox(0.018, 0.002, 0.10, M.darkMetalMat, s * 0.135, 0.019, 0.005).castShadow = false
    for (let r = 0; r < 5; r++) lbox(0.014, 0.001, 0.004, new THREE.MeshBasicMaterial({ color: 0x000000 }), s * 0.135, 0.020, -0.032 + r * 0.018).castShadow = false
  }
  lbox(0.11, 0.002, 0.065, M.greyMetalMat, 0, 0.019, 0.085).castShadow = false // touchpad
  // hinges + screen
  for (const s of [-1, 1]) {
    const h = new THREE.Mesh(new THREE.CylinderGeometry(0.009, 0.009, 0.035, 10), M.darkMetalMat)
    h.rotation.z = Math.PI / 2; h.position.set(s * 0.13, 0.02, -0.095); lap.add(h)
  }
  const scrG = new THREE.Group(); scrG.position.set(0, 0.02, -0.095); scrG.rotation.x = -0.32; lap.add(scrG)
  const lid = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.22, 0.012), M.blackPlasticMat)
  lid.position.set(0, 0.11, 0); lid.castShadow = true; scrG.add(lid)
  const logo = new THREE.Mesh(new THREE.CircleGeometry(0.012, 20),
    new THREE.MeshStandardMaterial({ color: 0x111111, emissive: 0x9fd8ff, emissiveIntensity: 1.2, roughness: 0.4 }))
  logo.position.set(0, 0.11, -0.007); logo.rotation.y = Math.PI; scrG.add(logo)
  const screenMat = new THREE.MeshStandardMaterial({ map: laptopScreenTex(true), emissive: 0xffffff, emissiveMap: laptopScreenTex(true), emissiveIntensity: 0.85, roughness: 0.3, color: 0x111111 })
  const laptopScreen = new THREE.Mesh(new THREE.PlaneGeometry(0.29, 0.19), screenMat)
  laptopScreen.position.set(0, 0.11, 0.007); scrG.add(laptopScreen)
  const cam = new THREE.Mesh(new THREE.SphereGeometry(0.0035, 8, 6), M.blackPlasticMat)
  cam.position.set(0, 0.212, 0.007); scrG.add(cam)
  const screenGlow = new THREE.PointLight(0x4db8ff, 1.6, 1.6, 2)
  screenGlow.position.set(-0.15, TOP + 0.35, 0.25); g.add(screenGlow)

  /* ---- mouse ---- */
  const mouse = new THREE.Group(); mouse.position.set(0.14, TOP + 0.023, 0.06); g.add(mouse)
  const mb = new THREE.Mesh(new RoundedBoxGeometry(0.055, 0.03, 0.09, 3, 0.012), M.blackPlasticMat)
  mb.castShadow = true; mouse.add(mb)
  const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.012, 10), M.greyMetalMat)
  wheel.rotation.z = Math.PI / 2; wheel.position.set(0, 0.016, 0.02); mouse.add(wheel)
  const sensor = new THREE.Mesh(new THREE.CylinderGeometry(0.007, 0.007, 0.003, 10), M.cyanLedMat)
  sensor.position.set(0, -0.014, -0.01); mouse.add(sensor)

  /* ---- articulated lamp (clickable) ---- */
  const lamp = new THREE.Group(); lamp.position.set(0.38, TOP + 0.023, -0.20); g.add(lamp)
  function ab(geo, mat, x, y, z) {
    const m = new THREE.Mesh(geo, mat)
    m.position.set(x, y, z); m.castShadow = true; lamp.add(m); return m
  }
  ab(new THREE.CylinderGeometry(0.055, 0.06, 0.02, 20), M.blackPlasticMat, 0, 0.01, 0)
  ab(new THREE.CylinderGeometry(0.012, 0.012, 0.03, 10), M.darkMetalMat, 0, 0.03, 0)
  const lowArm = ab(new THREE.CylinderGeometry(0.008, 0.008, 0.24, 10), M.chromeMat, 0.02, 0.15, 0)
  lowArm.rotation.z = -0.3
  ab(new THREE.SphereGeometry(0.014, 12, 10), M.blackPlasticMat, 0.055, 0.26, 0)
  const upArm = ab(new THREE.CylinderGeometry(0.008, 0.008, 0.22, 10), M.chromeMat, 0.0, 0.36, 0)
  upArm.rotation.z = 0.55
  // spring + cable
  const spring = ab(new THREE.CylinderGeometry(0.012, 0.012, 0.15, 8), M.darkMetalMat, 0.032, 0.15, 0.012)
  spring.rotation.z = -0.3
  for (const cy of [0.10, 0.20]) {
    const clip = new THREE.Mesh(new THREE.TorusGeometry(0.010, 0.003, 6, 12), M.blackPlasticMat)
    clip.position.set(0.032 - (0.15 - cy) * 0.29, cy, 0.012); clip.rotation.y = Math.PI / 2; clip.rotation.z = -0.3; lamp.add(clip)
  }
  const cableCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(-0.03, 0.01, -0.03), new THREE.Vector3(0.05, 0.14, -0.03),
    new THREE.Vector3(0.03, 0.30, -0.02), new THREE.Vector3(-0.06, 0.44, 0.0)
  ])
  lamp.add(new THREE.Mesh(new THREE.TubeGeometry(cableCurve, 20, 0.0035, 6), M.blackPlasticMat))
  const shade = ab(new THREE.CylinderGeometry(0.028, 0.062, 0.07, 20, 1, true),
    new THREE.MeshStandardMaterial({ color: 0x17181c, roughness: 0.5, side: THREE.DoubleSide }), -0.085, 0.44, 0.01)
  shade.rotation.z = 0.9
  const shadeInner = new THREE.Mesh(new THREE.CylinderGeometry(0.026, 0.058, 0.05, 20, 1, true),
    new THREE.MeshStandardMaterial({ color: 0xf3e3c2, emissive: 0xffc98a, emissiveIntensity: 0.4, side: THREE.BackSide }))
  shadeInner.position.copy(shade.position); shadeInner.rotation.copy(shade.rotation); lamp.add(shadeInner)
  const lampBulbMat = M.warmBulbMat.clone()
  const lampBulb = new THREE.Mesh(new THREE.SphereGeometry(0.02, 14, 12), lampBulbMat)
  lampBulb.position.set(-0.10, 0.425, 0.01); lamp.add(lampBulb)
  const lampSprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: 0xffcf7a, transparent: true, opacity: 0.5, depthWrite: false }))
  lampSprite.scale.set(0.4, 0.4, 1); lampSprite.position.copy(lampBulb.position); lamp.add(lampSprite)
  const lampGlow = new THREE.PointLight(0xffc98a, 3.2, 2.6, 2)
  lampGlow.position.set(0.38 - 0.12, TOP + 0.45, -0.20 + 0.05); g.add(lampGlow)
  const rocker = new THREE.Mesh(new THREE.BoxGeometry(0.018, 0.008, 0.012), M.cyanLedMat)
  rocker.position.set(0.03, 0.022, 0.045); lamp.add(rocker)

  /* ---- bottle ---- */
  const bot = new THREE.Group(); bot.position.set(0.60, TOP + 0.023, -0.20); g.add(bot)
  function tmb(geo, mat, x, y, z) {
    const m = new THREE.Mesh(geo, mat)
    m.position.set(x, y, z); m.castShadow = true; bot.add(m); return m
  }
  tmb(new THREE.CylinderGeometry(0.04, 0.04, 0.18, 20), new THREE.MeshStandardMaterial({ color: 0xd8c95a, roughness: 0.1, transparent: true, opacity: 0.55 }), 0, 0.09, 0)
  tmb(new THREE.CylinderGeometry(0.034, 0.034, 0.11, 16), M.waterMat, 0, 0.065, 0).castShadow = false
  tmb(new THREE.CylinderGeometry(0.0415, 0.0415, 0.06, 20, 1, true), M.labelMat, 0, 0.09, 0)
  for (let ti = 0; ti < 3; ti++)
    tmb(new THREE.BoxGeometry(0.002, 0.008, 0.012), M.skirtMat, 0.036, 0.05 + ti * 0.02, 0.02).castShadow = false
  tmb(new THREE.CylinderGeometry(0.022, 0.03, 0.025, 14), new THREE.MeshStandardMaterial({ color: 0xd8c95a, roughness: 0.1, transparent: true, opacity: 0.55 }), 0, 0.19, 0)
  tmb(new THREE.CylinderGeometry(0.025, 0.025, 0.024, 16), M.darkMetalMat, 0, 0.21, 0)
  for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2
    tmb(new THREE.BoxGeometry(0.004, 0.02, 0.004), M.chromeMat, Math.cos(a) * 0.025, 0.21, Math.sin(a) * 0.025).castShadow = false
  }

  /* ---- charger + cable ---- */
  dbox(0.06, 0.03, 0.09, M.skirtMat, -0.62, TOP + 0.038, -0.20)
  dbox(0.062, 0.004, 0.092, M.edgeBandMat, -0.62, TOP + 0.038, -0.20).castShadow = false
  const chLed = new THREE.Mesh(new THREE.BoxGeometry(0.004, 0.008, 0.008), M.cyanLedMat)
  chLed.position.set(-0.588, TOP + 0.04, -0.20); g.add(chLed)
  const chCable = new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3([
    new THREE.Vector3(-0.62, TOP + 0.025, -0.15), new THREE.Vector3(-0.55, TOP + 0.025, -0.02),
    new THREE.Vector3(-0.40, TOP + 0.025, 0.0), new THREE.Vector3(-0.31, TOP + 0.03, -0.02)
  ]), 20, 0.004, 6), M.blackPlasticMat)
  g.add(chCable)

  /* ---- books ---- */
  const bookCols = [0xb03030, 0x1f9e9e, 0xe6b800]
  bookCols.forEach((col, i) => {
    const w = 0.22 - i * 0.02, d = 0.16 - i * 0.01, h = 0.035
    const bk = dbox(w, h, d, new THREE.MeshStandardMaterial({ color: col, roughness: 0.75 }), -0.52, TOP + 0.04 + i * 0.037, -0.16)
    bk.rotation.y = [0.15, -0.08, 0.04][i]
    const pg = dbox(w * 0.92, h * 0.6, d * 0.96, M.bookPageMat, bk.position.x, bk.position.y, bk.position.z)
    pg.rotation.y = bk.rotation.y; pg.castShadow = false
    for (const by of [-0.008, 0.008]) {
      const sband = dbox(w * 1.005, h * 0.16, d * 1.01, M.bookPageMat, bk.position.x, bk.position.y + by, bk.position.z)
      sband.rotation.y = bk.rotation.y; sband.castShadow = false
    }
    const band = dbox(w * 0.3, h * 1.02, d * 1.01, M.bookPageMat, bk.position.x, bk.position.y, bk.position.z)
    band.rotation.y = bk.rotation.y; band.castShadow = false
  })

  /* ---- mug + coffee + pens ---- */
  const mug = new THREE.Group(); mug.position.set(-0.30, TOP + 0.023, 0.14); g.add(mug)
  function mmb(geo, mat, x, y, z) {
    const m = new THREE.Mesh(geo, mat)
    m.position.set(x, y, z); m.castShadow = true; mug.add(m); return m
  }
  mmb(new THREE.CylinderGeometry(0.028, 0.024, 0.055, 18), M.creamCeramicMat, 0, 0.028, 0)
  const mugLip = new THREE.Mesh(new THREE.TorusGeometry(0.027, 0.0028, 8, 24), M.creamCeramicMat)
  mugLip.rotation.x = Math.PI / 2; mugLip.position.set(0, 0.055, 0); mug.add(mugLip)
  mmb(new THREE.CylinderGeometry(0.023, 0.023, 0.004, 18), M.coffeeMat, 0, 0.048, 0).castShadow = false
  const handle = mmb(new THREE.TorusGeometry(0.016, 0.0045, 8, 18), M.creamCeramicMat, -0.032, 0.03, 0)
  handle.rotation.y = Math.PI / 2
  mmb(new THREE.CylinderGeometry(0.042, 0.042, 0.004, 18), M.woodMat, 0, 0.002, 0).castShadow = false // coaster
  const holder = new THREE.Group(); holder.position.set(0.16, TOP + 0.023, 0.15); g.add(holder)
  function hmb(geo, mat, x, y, z) {
    const m = new THREE.Mesh(geo, mat)
    m.position.set(x, y, z); m.castShadow = true; holder.add(m); return m
  }
  hmb(new THREE.CylinderGeometry(0.026, 0.023, 0.065, 16), M.blackPlasticMat, 0, 0.033, 0)
  hmb(new THREE.CylinderGeometry(0.021, 0.021, 0.004, 16), new THREE.MeshBasicMaterial({ color: 0x000000 }), 0, 0.062, 0).castShadow = false
  const penCols = [0x1a66cc, 0xcc1a33]
  penCols.forEach((col, i) => {
    const pen = hmb(new THREE.CylinderGeometry(0.0045, 0.0045, 0.11, 10),
      new THREE.MeshStandardMaterial({ color: col, roughness: 0.5 }), i === 0 ? -0.008 : 0.009, 0.10, i === 0 ? -0.006 : 0.007)
    pen.rotation.set(i === 0 ? 0.2 : -0.22, 0, i === 0 ? 0.1 : -0.12)
    hmb(new THREE.CylinderGeometry(0.006, 0.006, 0.012, 8), M.blackPlasticMat, pen.position.x, 0.152, pen.position.z).rotation.copy(pen.rotation)
    hmb(new THREE.CylinderGeometry(0.002, 0.004, 0.014, 8), M.chromeMat, pen.position.x, 0.045, pen.position.z).rotation.copy(pen.rotation)
  })

  aoBlob(1.0, 2.0, 1.55, 0.3, 0.005, 0.9)
  return { lampBulb, lampBulbMat, lampSprite, lampGlow, laptopScreen, screenMat, screenGlow }
}
