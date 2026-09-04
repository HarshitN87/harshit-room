import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

/* Bruno-Simon-grade viewer for the baked room diorama.
   - Baked 4K GLB stays the visual truth (unlit, toneMapped=false)
   - Thin dynamic layer on top: dust motes, breathing glow lights,
     camera focus presets, polished loader + UI. No new furniture. */

const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b0c10);
scene.fog = new THREE.Fog(0x0b0c10, 18, 34);

const aspect = window.innerWidth / window.innerHeight;
const frustumSize = 4.5;
const camera = new THREE.OrthographicCamera(
  -frustumSize * aspect, frustumSize * aspect,
  frustumSize, -frustumSize, 0.1, 100
);
const HOME_POS = new THREE.Vector3(6, 6, 6);
const HOME_TGT = new THREE.Vector3(0, 0.4, 0);
camera.position.copy(HOME_POS);
camera.lookAt(HOME_TGT);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.maxPolarAngle = Math.PI / 2 - 0.05;
controls.minZoom = 0.6;
controls.maxZoom = 4;
controls.target.copy(HOME_TGT);

// Soft fill so back-faces never go pitch black (baked texture does the rest)
scene.add(new THREE.AmbientLight(0xffffff, 0.18));

// Living-glow rig: very low intensities, only to make emissives breathe
const lampGlow = new THREE.PointLight(0xffd9a0, 4, 4, 2);
lampGlow.position.set(0.4, 1.6, -0.9);
scene.add(lampGlow);
const screenGlow = new THREE.PointLight(0x4db8ff, 2.2, 3, 2);
screenGlow.position.set(0.1, 1.2, -0.6);
scene.add(screenGlow);
const ledGlow = new THREE.PointLight(0xff2f6d, 1.6, 5, 2);
ledGlow.position.set(0, 0.6, 1.6);
scene.add(ledGlow);
const ceilingGlow = new THREE.PointLight(0xffe6b0, 3, 6, 2);
ceilingGlow.position.set(-1.5, 2.5, -0.5);
scene.add(ceilingGlow);

// Floating dust motes (atmosphere only, Bruno-style)
const MOTES = 220;
const moteGeo = new THREE.BufferGeometry();
const motePos = new Float32Array(MOTES * 3);
const moteSeed = new Float32Array(MOTES);
for (let i = 0; i < MOTES; i++) {
  motePos[i * 3] = (Math.random() - 0.5) * 6;
  motePos[i * 3 + 1] = Math.random() * 3.2;
  motePos[i * 3 + 2] = (Math.random() - 0.5) * 6;
  moteSeed[i] = Math.random() * Math.PI * 2;
}
moteGeo.setAttribute('position', new THREE.BufferAttribute(motePos, 3));
const moteMat = new THREE.PointsMaterial({
  color: 0xbfd9ff, size: 0.02, transparent: true, opacity: 0.35,
  depthWrite: false, sizeAttenuation: true
});
const motes = new THREE.Points(moteGeo, moteMat);
scene.add(motes);

// Loader
const loader = new GLTFLoader();
const loaderPercent = document.getElementById('loader-percent');
const loaderBar = document.getElementById('loader-bar');
const loaderOverlay = document.getElementById('loader');

let roomModel = null;
let autoRotate = false;
let focusTween = null;

loader.load(
  '/room_baked_combined.glb',
  (gltf) => {
    roomModel = gltf.scene;
    const maxAnisotropy = renderer.capabilities.getMaxAnisotropy();
    roomModel.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = false;
        child.receiveShadow = false;
        if (child.material) {
          child.material.toneMapped = false;
          if (child.material.map) {
            child.material.map.anisotropy = maxAnisotropy;
            child.material.map.minFilter = THREE.LinearMipmapLinearFilter;
            child.material.map.magFilter = THREE.LinearFilter;
            child.material.map.needsUpdate = true;
          }
        }
      }
    });
    roomModel.position.set(0, 0, 0);
    scene.add(roomModel);
    loaderOverlay.style.opacity = '0';
    setTimeout(() => { loaderOverlay.style.display = 'none'; }, 650);
    document.getElementById('ui-container')?.classList.add('ready');
  },
  (xhr) => {
    if (xhr.total > 0) {
      const percent = Math.round((xhr.loaded / xhr.total) * 100);
      loaderPercent.textContent = `LOADING 3D ROOM — ${percent}%`;
      if (loaderBar) loaderBar.style.width = `${percent}%`;
    }
  },
  (error) => {
    console.error('Error loading GLB:', error);
    loaderPercent.textContent = 'ERROR LOADING MODEL — run `npm run dev` and keep public/room_baked_combined.glb in place';
  }
);

// Camera focus presets (viewer UX only — camera moves, model untouched)
const PRESETS = {
  home: { pos: [6, 6, 6], tgt: [0, 0.4, 0] },
  desk: { pos: [3.4, 3.2, 3.4], tgt: [0.5, 0.8, -0.4] },
  bed: { pos: [-4.2, 3.4, 3.2], tgt: [-1.2, 0.4, -0.3] },
  wardrobe: { pos: [1.8, 3.0, 5.2], tgt: [-1.0, 1.2, 1.4] },
  window: { pos: [-5.2, 2.6, 1.6], tgt: [-1.9, 1.4, -0.5] }
};
function flyTo(name) {
  const p = PRESETS[name];
  if (!p) return;
  focusTween = {
    t: 0,
    fromPos: camera.position.clone(),
    toPos: new THREE.Vector3(...p.pos),
    fromTgt: controls.target.clone(),
    toTgt: new THREE.Vector3(...p.tgt)
  };
  document.querySelectorAll('[data-focus]').forEach((b) =>
    b.classList.toggle('active', b.dataset.focus === name));
}
document.querySelectorAll('[data-focus]').forEach((b) =>
  b.addEventListener('click', () => flyTo(b.dataset.focus)));
document.getElementById('btn-rotate')?.addEventListener('click', (e) => {
  autoRotate = !autoRotate;
  e.currentTarget.classList.toggle('active', autoRotate);
});
document.getElementById('btn-reset')?.addEventListener('click', () => flyTo('home'));

window.addEventListener('resize', () => {
  const na = window.innerWidth / window.innerHeight;
  camera.left = -frustumSize * na;
  camera.right = frustumSize * na;
  camera.top = frustumSize;
  camera.bottom = -frustumSize;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

const clock = new THREE.Clock();
const easeInOut = (t) => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

function animate() {
  requestAnimationFrame(animate);
  const delta = Math.min(clock.getDelta(), 0.05);
  const time = clock.elapsedTime;

  if (focusTween) {
    focusTween.t += delta / 1.1;
    const k = easeInOut(Math.min(focusTween.t, 1));
    camera.position.lerpVectors(focusTween.fromPos, focusTween.toPos, k);
    controls.target.lerpVectors(focusTween.fromTgt, focusTween.toTgt, k);
    if (focusTween.t >= 1) focusTween = null;
  } else if (autoRotate && !reduceMotion) {
    const r = camera.position.clone().sub(controls.target);
    const angle = delta * 0.25;
    const cos = Math.cos(angle), sin = Math.sin(angle);
    const x = r.x * cos - r.z * sin, z = r.x * sin + r.z * cos;
    camera.position.set(controls.target.x + x, camera.position.y, controls.target.z + z);
  }

  // breathing glows — subtle, never fights the bake
  if (!reduceMotion) {
    lampGlow.intensity = 4 + Math.sin(time * 2.1) * 0.35;
    screenGlow.intensity = 2.2 + Math.sin(time * 1.3 + 1) * 0.3;
    ledGlow.intensity = 1.6 + Math.sin(time * 0.9 + 2) * 0.25;
    ceilingGlow.intensity = 3 + Math.sin(time * 1.7) * 0.2;
    const p = moteGeo.attributes.position.array;
    for (let i = 0; i < MOTES; i++) {
      p[i * 3 + 1] += Math.sin(time * 0.4 + moteSeed[i]) * 0.0006 + 0.0009;
      p[i * 3] += Math.cos(time * 0.25 + moteSeed[i]) * 0.0005;
      if (p[i * 3 + 1] > 3.4) p[i * 3 + 1] = 0;
    }
    moteGeo.attributes.position.needsUpdate = true;
  }

  controls.update();
  renderer.render(scene, camera);
}
animate();
