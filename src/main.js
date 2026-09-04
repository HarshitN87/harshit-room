import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js'
import * as M from './components/materials.js'
import { laptopScreenTex, glowTex } from './components/materials.js'
import { makeHelpers } from './components/helpers.js'
import { buildShell } from './components/shell.js'
import { buildWindowWall } from './components/windowWall.js'
import { buildDoor } from './components/door.js'
import { buildWardrobe } from './components/wardrobe.js'
import { buildBed } from './components/bed.js'
import { buildDesk } from './components/desk.js'
import { buildChair } from './components/chair.js'

/* Harshit Room in 3D on the room-3d-mvp pipeline: fully procedural,
   no Blender bake step. Same furniture as before, Bruno-style light rig,
   day/night mix, clickable lamp + laptop screen + pendant. */

const canvas = document.getElementById('scene')
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true })
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
renderer.setSize(window.innerWidth, window.innerHeight)
renderer.shadowMap.enabled = true
renderer.shadowMap.type = THREE.PCFSoftShadowMap
renderer.outputColorSpace = THREE.SRGBColorSpace
renderer.toneMapping = THREE.ACESFilmicToneMapping
renderer.toneMappingExposure = 1.05

const scene = new THREE.Scene()
const DAY_BG = new THREE.Color(0x2a2e3a)
const NIGHT_BG = new THREE.Color(0x0e1016)
scene.background = DAY_BG.clone()
scene.fog = new THREE.Fog(scene.background.clone(), 16, 32)

/* soft studio reflections so chrome/glass read correctly (low intensity keeps night mood) */
{
  const pmrem = new THREE.PMREMGenerator(renderer)
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture
  scene.environmentIntensity = 0.22
}

const W = 4, D = 4, H = 3

const camera = new THREE.PerspectiveCamera(35, window.innerWidth / window.innerHeight, 0.1, 100)
camera.position.set(7.6, 5.6, 7.0)

const controls = new OrbitControls(camera, renderer.domElement)
controls.target.set(-0.2, 0.8, -0.2)
window.__room = { scene, camera, controls, W, D, H }
controls.enableDamping = true
controls.dampingFactor = 0.06
controls.minDistance = 1.2
controls.maxDistance = 12
controls.minPolarAngle = 0.15
controls.maxPolarAngle = 1.45
controls.enablePan = false
controls.autoRotate = true
controls.autoRotateSpeed = 0.55
renderer.domElement.addEventListener('pointerdown', () => { controls.autoRotate = false }, { once: true })

/* ============================== lights =================================== */
const hemi = new THREE.HemisphereLight(0xfff6e8, 0x3a3f52, 0.95)
scene.add(hemi)
const sun = new THREE.DirectionalLight(0xfff1d6, 1.7)
sun.position.set(4, 6.5, 3)
sun.castShadow = true
sun.shadow.mapSize.set(2048, 2048)
sun.shadow.bias = -0.0004
sun.shadow.normalBias = 0.02
Object.assign(sun.shadow.camera, { left: -6, right: 6, top: 6, bottom: -6, near: 1, far: 20 })
scene.add(sun)
const fill = new THREE.DirectionalLight(0xbfd4ff, 0.45)
fill.position.set(-5, 3.5, 4)
scene.add(fill)
const warm = new THREE.PointLight(0xffd9a0, 3, 10, 1.8)
warm.position.set(0.25, 1.9, 0.1)
scene.add(warm)
const pinkWash = new THREE.PointLight(0xff5c9a, 4, 7, 1.9)
pinkWash.position.set(-0.3, 1.9, 1.1)
scene.add(pinkWash)
const cyanWash = new THREE.PointLight(0x5cc8ff, 3, 7, 1.9)
cyanWash.position.set(1.2, 1.7, 0.6)
scene.add(cyanWash)
const ceilingGlow = new THREE.PointLight(0xffe0ae, 4, 6, 1.9)
ceilingGlow.position.set(-1.5, 2.45, 0.1)
scene.add(ceilingGlow)
scene.add(new THREE.AmbientLight(0xffffff, 0.15))

/* ====================== compose the room components ====================== */
const { box, rbox, aoBlob } = makeHelpers(scene)
const ctx = { M, box, rbox, aoBlob, W, D, H }
const shell = buildShell(scene, ctx)
const win = buildWindowWall(scene, ctx, shell)
buildDoor(scene, ctx, shell)
buildWardrobe(scene, ctx, shell)
buildBed(scene, ctx)
const desk = buildDesk(scene, ctx)
buildChair(scene, ctx)

/* ==================== dust motes (Bruno atmosphere) ====================== */
const DUST = 220
const dustGeo = new THREE.BufferGeometry()
const dpos = new Float32Array(DUST * 3)
const dseed = new Float32Array(DUST)
for (let i = 0; i < DUST; i++) {
  dpos[i * 3] = (Math.random() - 0.5) * W
  dpos[i * 3 + 1] = Math.random() * H
  dpos[i * 3 + 2] = (Math.random() - 0.5) * D
  dseed[i] = Math.random() * 100
}
dustGeo.setAttribute('position', new THREE.BufferAttribute(dpos, 3))
const dust = new THREE.Points(dustGeo, new THREE.PointsMaterial({
  map: glowTex, color: 0xffe9c4, size: 0.035, transparent: true, opacity: 0.35,
  depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true
}))
scene.add(dust)

/* ================= night mix (Bruno uNightMix homage) ==================== */
let lampOn = true
let screenOn = true
let lightOn = true
let nightMix = 0.85
const sunDay = 1.7, hemiDay = 0.95
function applyNightMix(v) {
  nightMix = THREE.MathUtils.clamp(v, 0, 1)
  scene.background.copy(DAY_BG).lerp(NIGHT_BG, nightMix)
  scene.fog.color.copy(scene.background)
  sun.intensity = sunDay * (1 - nightMix * 0.85)
  hemi.intensity = hemiDay * (1 - nightMix * 0.6)
  fill.intensity = 0.45 * (1 - nightMix * 0.4)
  if (lightOn) ceilingGlow.intensity = 4 * (0.3 + nightMix * 0.85)
  pinkWash.intensity = 1.2 + nightMix * 4.2
  cyanWash.intensity = 0.8 + nightMix * 2.2
  if (lampOn) desk.lampGlow.intensity = 0.8 + nightMix * 3.0
  if (screenOn) desk.screenGlow.intensity = 0.5 + nightMix * 1.6
  shell.ledGlow.intensity = 0.8 + nightMix * 3.0
  win.nightGlass.material.opacity = 0.55 + nightMix * 0.35
}
window.setNightMix = applyNightMix
applyNightMix(0.85)

/* ============================== interaction ============================== */
const ray = new THREE.Raycaster(), ptr = new THREE.Vector2()
const toast = document.getElementById('toast')
let toastTimer = 0
function showToast(msg) {
  toast.textContent = msg; toast.classList.remove('hidden')
  clearTimeout(toastTimer); toastTimer = setTimeout(() => toast.classList.add('hidden'), 1400)
}
function setLamp(on, silent) {
  lampOn = on
  desk.lampBulbMat.emissiveIntensity = on ? 2.4 : 0.05
  desk.lampSprite.material.opacity = on ? 0.5 : 0.04
  desk.lampGlow.intensity = on ? (0.8 + nightMix * 3.0) : 0
  if (!silent) showToast(on ? 'Lamp on' : 'Lamp off')
}
function setScreen(on, silent) {
  screenOn = on
  desk.laptopScreen.material.map = laptopScreenTex(on)
  desk.laptopScreen.material.emissiveMap = on ? desk.laptopScreen.material.map : null
  desk.laptopScreen.material.emissiveIntensity = on ? 0.85 : 0
  desk.laptopScreen.material.needsUpdate = true
  desk.screenGlow.intensity = on ? (0.5 + nightMix * 1.6) : 0
  if (!silent) showToast(on ? 'Laptop on' : 'Laptop off')
}
function setLight(on) {
  lightOn = on
  applyNightMix(nightMix)
  M.warmBulbMat.emissiveIntensity = on ? 2.4 : 0.05
  shell.bulbGlow.material.opacity = on ? 0.45 : 0.04
  if (!on) ceilingGlow.intensity = 0
  showToast(on ? 'Pendant on' : 'Pendant off')
}
const clickables = [desk.lampBulb, desk.laptopScreen, shell.bulbMesh]
function pick(e) {
  ptr.x = (e.clientX / window.innerWidth) * 2 - 1
  ptr.y = -(e.clientY / window.innerHeight) * 2 + 1
  ray.setFromCamera(ptr, camera)
  const hit = ray.intersectObjects(clickables, false)[0]
  return hit ? hit.object : null
}
renderer.domElement.addEventListener('pointermove', (e) => {
  const o = pick(e)
  renderer.domElement.style.cursor = o ? 'pointer' : 'grab'
})
renderer.domElement.addEventListener('click', (e) => {
  const o = pick(e)
  if (o === desk.lampBulb) setLamp(!lampOn)
  else if (o === desk.laptopScreen) setScreen(!screenOn)
  else if (o === shell.bulbMesh) setLight(!lightOn)
})
document.getElementById('chip-lamp').onclick = () => setLamp(!lampOn)
document.getElementById('chip-screen').onclick = () => setScreen(!screenOn)
document.getElementById('chip-light').onclick = () => setLight(!lightOn)
document.getElementById('chip-daynight').onclick = (e) => {
  const to = nightMix > 0.5 ? 0.15 : 0.9
  applyNightMix(to)
  e.currentTarget.textContent = nightMix > 0.5 ? '☀️ Day' : '🌙 Night'
  showToast(nightMix > 0.5 ? 'Night mode' : 'Day mode')
}

/* ================================= loop ================================== */
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
})
const camStart = camera.position.clone(), camEnd = new THREE.Vector3(4.8, 3.4, 5.0)
let intro = 0
window.__snapView = (px, py, pz, tx, ty, tz) => {
  intro = 1
  controls.autoRotate = false
  camera.position.set(px, py, pz)
  controls.target.set(tx, ty, tz)
  camera.lookAt(controls.target)
  controls.update()
}
/* named snap presets via ?snap=chair|wardrobe|door|bed|desk (verification) */
{
  const q = new URLSearchParams(location.search)
  const VIEWS = {
    chair: [2.2, 1.4, 2.0, 0.35, 0.6, 0.35],
    wardrobe: [-0.75, 1.7, 2.4, -0.75, 1.3, -1.5],
    door: [1.0, 1.3, 1.3, 0.9, 1.0, -1.5],
    bin: [0.75, 1.0, 0.3, 0.8, 0.15, -1.0],
    bed: [1.8, 2.2, 3.1, -1.2, 0.5, 0.2],
    desk: [0.2, 1.7, 2.4, 1.15, 0.65, 0.1]
  }
  if (q.has('snap') && VIEWS[q.get('snap')]) window.__snapView(...VIEWS[q.get('snap')])
}
const clock = new THREE.Clock()
let firstFrame = true
renderer.setAnimationLoop(() => {
  const dt = Math.min(clock.getDelta(), 0.05), t = clock.elapsedTime
  if (intro < 1) {
    intro = Math.min(1, intro + dt / 2.4)
    const k = 1 - Math.pow(1 - intro, 3)
    camera.position.lerpVectors(camStart, camEnd, k)
  }
  win.waveCurtains(t, 0.35)
  if (screenOn) desk.screenGlow.intensity = (0.5 + nightMix * 1.6) * (1 + Math.sin(t * 2.2) * 0.06)
  if (lampOn) desk.lampGlow.intensity = (0.8 + nightMix * 3.0) * (1 + Math.sin(t * 7.7) * 0.02)
  const dp = dust.geometry.attributes.position
  for (let i = 0; i < DUST; i++) {
    dp.array[i * 3 + 1] += Math.sin(t * 0.5 + dseed[i]) * 0.0006 + 0.0004
    dp.array[i * 3] += Math.cos(t * 0.3 + dseed[i]) * 0.0005
    if (dp.array[i * 3 + 1] > H) dp.array[i * 3 + 1] = 0
    if (dp.array[i * 3] > W / 2) dp.array[i * 3] = -W / 2
  }
  dp.needsUpdate = true
  dust.material.opacity = 0.22 + nightMix * 0.25
  controls.update()
  renderer.render(scene, camera)
  if (firstFrame) {
    firstFrame = false
    document.getElementById('loader').classList.add('done')
    canvas.classList.add('ready')
  }
})

requestAnimationFrame(() => requestAnimationFrame(() => {
  const l = document.getElementById('loader')
  const s = document.getElementById('scene')
  if (l) l.classList.add('done')
  if (s) s.classList.add('ready')
}))
