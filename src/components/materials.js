import * as THREE from 'three'

/* Shared canvas textures + materials for the room (extracted from main.js) */

export function canvasTex(size, draw, rx = 1, ry = 1, srgb = true) {
  const c = document.createElement('canvas')
  c.width = c.height = size
  draw(c.getContext('2d'), size)
  const t = new THREE.CanvasTexture(c)
  t.wrapS = t.wrapT = THREE.RepeatWrapping
  t.repeat.set(rx, ry)
  if (srgb) t.colorSpace = THREE.SRGBColorSpace
  t.anisotropy = 8
  return t
}

export function noiseOver(g, s, n = 900, alpha = 0.05) {
  for (let i = 0; i < n; i++) {
    g.fillStyle = Math.random() > 0.5 ? `rgba(255,255,255,${alpha})` : `rgba(0,0,0,${alpha})`
    g.fillRect(Math.random() * s, Math.random() * s, 2, 2)
  }
}

export const starTileTex = canvasTex(512, (g, s) => {
  g.fillStyle = '#cdc2b0'; g.fillRect(0, 0, s, s)
  for (let i = 0; i < 7; i++) {
    const px = Math.random() * s, py = Math.random() * s, pr = 60 + Math.random() * 130
    const mg = g.createRadialGradient(px, py, 4, px, py, pr)
    const warm = Math.random() > 0.5
    mg.addColorStop(0, warm ? 'rgba(160,130,95,0.10)' : 'rgba(110,110,125,0.10)')
    mg.addColorStop(1, 'rgba(0,0,0,0)')
    g.fillStyle = mg; g.fillRect(0, 0, s, s)
  }
  for (let i = 0; i < 5; i++) {
    const px = Math.random() * s, py = Math.random() * s, pr = 90 + Math.random() * 150
    const mg2 = g.createRadialGradient(px, py, 6, px, py, pr)
    mg2.addColorStop(0, Math.random() > 0.5 ? 'rgba(128,124,110,0.08)' : 'rgba(150,140,120,0.08)')
    mg2.addColorStop(1, 'rgba(0,0,0,0)')
    g.fillStyle = mg2; g.fillRect(0, 0, s, s)
  }
  const cx = s / 2, cy = s / 2, R = s * 0.47, r = s * 0.18
  const cols = ['#8a7a68', '#5d5a66', '#a89a86', '#6e6a72']
  for (let i = 0; i < 8; i++) {
    const a0 = (i / 8) * Math.PI * 2, a1 = ((i + 1) / 8) * Math.PI * 2, am = (a0 + a1) / 2
    g.fillStyle = cols[i % 4]
    g.beginPath()
    g.moveTo(cx, cy)
    g.lineTo(cx + Math.cos(a0) * R, cy + Math.sin(a0) * R)
    g.lineTo(cx + Math.cos(am) * r, cy + Math.sin(am) * r)
    g.lineTo(cx + Math.cos(a1) * R, cy + Math.sin(a1) * R)
    g.closePath(); g.fill()
    g.fillStyle = Math.random() > 0.5 ? 'rgba(255,240,220,0.07)' : 'rgba(40,30,20,0.08)'
    g.beginPath()
    g.moveTo(cx, cy)
    g.lineTo(cx + Math.cos(a0) * R, cy + Math.sin(a0) * R)
    g.lineTo(cx + Math.cos(am) * r, cy + Math.sin(am) * r)
    g.lineTo(cx + Math.cos(a1) * R, cy + Math.sin(a1) * R)
    g.closePath(); g.fill()
    g.strokeStyle = 'rgba(60,50,40,0.5)'; g.lineWidth = 3; g.stroke()
  }
  g.fillStyle = '#e9e1d2'
  g.beginPath(); g.moveTo(cx, cy - 26); g.lineTo(cx + 26, cy); g.lineTo(cx, cy + 26); g.lineTo(cx - 26, cy); g.closePath(); g.fill()
  g.strokeStyle = 'rgba(70,66,58,0.9)'; g.lineWidth = 12; g.strokeRect(0, 0, s, s)
  g.strokeStyle = 'rgba(255,255,255,0.25)'; g.lineWidth = 2; g.strokeRect(6, 6, s - 12, s - 12)
  g.strokeStyle = 'rgba(60,52,44,0.35)'; g.lineWidth = 1
  for (let i = 0; i < 7; i++) {
    let cx = Math.random() * s, cy = Math.random() * s
    g.beginPath(); g.moveTo(cx, cy)
    for (let k = 0; k < 4; k++) { cx += (Math.random() - 0.5) * 60; cy += (Math.random() - 0.5) * 60; g.lineTo(cx, cy) }
    g.stroke()
  }
  g.fillStyle = 'rgba(50,45,38,0.25)'
  for (let i = 0; i < 120; i++) {
    const e = Math.floor(Math.random() * 4), t = Math.random() * s
    const gx = e === 0 ? t : e === 1 ? s - 6 + Math.random() * 6 : e === 2 ? t : Math.random() * 6
    const gy = e === 0 ? Math.random() * 6 : e === 1 ? t : e === 2 ? s - 6 + Math.random() * 6 : t
    g.fillRect(gx, gy, 2, 2)
  }
  noiseOver(g, s, 1100, 0.05)
  for (let i = 0; i < 420; i++) {
    const edge = Math.floor(Math.random() * 4)
    const t = Math.random() * s, off = Math.random() * 12
    const gx = edge === 0 ? t : edge === 1 ? s - off : edge === 2 ? t : off
    const gy = edge === 0 ? off : edge === 1 ? t : edge === 2 ? s - off : t
    g.fillStyle = Math.random() > 0.4 ? 'rgba(50,45,38,0.35)' : 'rgba(255,250,240,0.3)'
    g.fillRect(gx, gy, 2, 2)
  }
}, 4, 3.4)

export const starTileRough = canvasTex(256, (g, s) => {
  g.fillStyle = '#b0b0b0'; g.fillRect(0, 0, s, s)
  g.fillStyle = '#8a8a8a'
  g.beginPath(); g.arc(s / 2, s / 2, s * 0.3, 0, Math.PI * 2); g.fill()
  g.fillStyle = 'rgba(255,255,255,0.10)'
  for (let i = 0; i < 8; i++) {
    const a0 = (i / 8) * Math.PI * 2
    g.beginPath(); g.moveTo(s / 2, s / 2)
    g.arc(s / 2, s / 2, s * 0.47, a0, a0 + Math.PI / 8); g.closePath(); g.fill()
  }
  g.strokeStyle = '#c8c8c8'; g.lineWidth = 14; g.strokeRect(0, 0, s, s)
  for (let i = 0; i < 6; i++) {
    const px = Math.random() * s, py = Math.random() * s, pr = 40 + Math.random() * 80
    const gz = g.createRadialGradient(px, py, 4, px, py, pr)
    gz.addColorStop(0, 'rgba(110,110,110,0.25)'); gz.addColorStop(1, 'rgba(110,110,110,0)')
    g.fillStyle = gz; g.fillRect(0, 0, s, s)
  }
  noiseOver(g, s, 800, 0.08)
}, 4, 3.4, false)

export const plasterTex = canvasTex(256, (g, s) => {
  g.fillStyle = '#808080'; g.fillRect(0, 0, s, s)
  noiseOver(g, s, 2200, 0.06)
  for (let i = 0; i < 40; i++) {
    g.fillStyle = 'rgba(255,255,255,0.04)'
    g.beginPath(); g.arc(Math.random() * s, Math.random() * s, 6 + Math.random() * 18, 0, Math.PI * 2); g.fill()
  }
  for (let i = 0; i < 26; i++) {
    g.fillStyle = Math.random() > 0.5 ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'
    g.beginPath(); g.arc(Math.random() * s, Math.random() * s, 20 + Math.random() * 26, 0, Math.PI * 2); g.fill()
  }
  for (let i = 0; i < 2600; i++) {
    g.fillStyle = Math.random() > 0.5 ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'
    g.fillRect(Math.random() * s, Math.random() * s, 1, 1)
  }
}, 2, 2, false)

export const brushedTex = canvasTex(512, (g, s) => {
  g.fillStyle = '#9aa0a3'; g.fillRect(0, 0, s, s)
  for (let i = 0; i < 1500; i++) {
    const x = Math.random() * s
    g.fillStyle = Math.random() > 0.5 ? 'rgba(255,255,255,0.035)' : 'rgba(0,0,0,0.045)'
    g.fillRect(x, 0, 1, s)
  }
  for (let i = 0; i < 9; i++) {
    const x = Math.random() * s, w = 8 + Math.random() * 26
    g.fillStyle = Math.random() > 0.5 ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.035)'
    g.fillRect(x, 0, w, s)
  }
  const sheen = g.createLinearGradient(0, 0, 0, s)
  sheen.addColorStop(0, 'rgba(255,255,255,0.06)'); sheen.addColorStop(0.5, 'rgba(255,255,255,0)'); sheen.addColorStop(1, 'rgba(0,0,0,0.06)')
  g.fillStyle = sheen; g.fillRect(0, 0, s, s)
  const smx = s * 0.62, smy = s * 0.4
  const sm = g.createRadialGradient(smx, smy, 4, smx, smy, 44)
  sm.addColorStop(0, 'rgba(20,22,26,0.10)'); sm.addColorStop(1, 'rgba(20,22,26,0)')
  g.fillStyle = sm; g.fillRect(0, 0, s, s)
  const sm2 = g.createRadialGradient(smx + 26, smy + 18, 2, smx + 26, smy + 18, 26)
  sm2.addColorStop(0, 'rgba(20,22,26,0.08)'); sm2.addColorStop(1, 'rgba(20,22,26,0)')
  g.fillStyle = sm2; g.fillRect(0, 0, s, s)
  noiseOver(g, s, 300, 0.03)
}, 1, 1)

export const brushedRough = canvasTex(256, (g, s) => {
  g.fillStyle = '#6e6e6e'; g.fillRect(0, 0, s, s)
  for (let i = 0; i < 900; i++) {
    const x = Math.random() * s
    g.fillStyle = Math.random() > 0.5 ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.08)'
    g.fillRect(x, 0, 1, s)
  }
}, 1, 1, false)

export const woodTex = canvasTex(512, (g, s) => {
  const grad = g.createLinearGradient(0, 0, s, 0)
  grad.addColorStop(0, '#c19058'); grad.addColorStop(0.45, '#d9b078'); grad.addColorStop(1, '#b3814e')
  g.fillStyle = grad; g.fillRect(0, 0, s, s)
  g.strokeStyle = 'rgba(90,55,25,0.5)'
  for (let i = 0; i < 12; i++) {
    g.lineWidth = 1.5 + Math.random() * 2.5
    g.beginPath()
    g.moveTo(0, 18 + i * 42)
    g.bezierCurveTo(s * 0.3, 24 + i * 42, s * 0.65, 10 + i * 42, s, 20 + i * 42)
    g.stroke()
  }
  for (let i = 0; i < 350; i++) {
    const px = Math.random() * s, py = Math.random() * s, len = 4 + Math.random() * 14
    g.strokeStyle = Math.random() > 0.35 ? 'rgba(80,48,22,0.28)' : 'rgba(255,230,190,0.22)'
    g.lineWidth = 1
    g.beginPath(); g.moveTo(px, py); g.lineTo(px + len, py + (Math.random() - 0.5) * 3); g.stroke()
  }
  for (let i = 0; i < 60; i++) {
    const rx = Math.random() * s, ry = Math.random() * s, rl = 10 + Math.random() * 26
    g.strokeStyle = 'rgba(255,228,180,0.10)'; g.lineWidth = 2 + Math.random() * 2
    g.beginPath(); g.moveTo(rx, ry); g.lineTo(rx + rl, ry + (Math.random() - 0.5) * 2); g.stroke()
  }
  g.fillStyle = 'rgba(255,235,200,0.06)'; g.fillRect(0, 3, s, s / 2 - 3)
  g.fillStyle = 'rgba(60,30,10,0.07)'; g.fillRect(0, s / 2 + 2, s, s * 0.28 - 2)
  g.fillStyle = 'rgba(255,235,200,0.05)'; g.fillRect(0, s * 0.78 + 2, s, s * 0.22 - 2)
  g.fillStyle = 'rgba(60,35,15,0.55)'
  g.fillRect(0, 0, s, 3); g.fillRect(0, s / 2, s, 2); g.fillRect(0, s * 0.78, s, 2)
  g.fillStyle = 'rgba(60,35,15,0.4)'
  g.fillRect(0, s * 0.3, s, 1.5); g.fillRect(0, s * 0.62, s, 1.5)
  // subtle cathedral grain swirls (no harsh target knots)
  for (const [kx, ky] of [[0.3 * s, 0.25 * s], [0.7 * s, 0.7 * s], [0.45 * s, 0.9 * s]]) {
    for (let r = 3; r < 20; r += 3) {
      g.strokeStyle = `rgba(70,40,18,${0.28 - r * 0.01})`; g.lineWidth = 1.4
      g.beginPath(); g.ellipse(kx, ky, r * 1.5, r * 0.75, 0.35, 0, Math.PI * 2); g.stroke()
    }
    g.fillStyle = 'rgba(50,28,12,0.55)'
    g.beginPath(); g.ellipse(kx, ky, 2.6, 1.6, 0.35, 0, Math.PI * 2); g.fill()
  }
  // long pore streaks
  for (let i = 0; i < 90; i++) {
    const py = Math.random() * s, px = Math.random() * s, len = 20 + Math.random() * 60
    g.strokeStyle = Math.random() > 0.4 ? 'rgba(80,48,22,0.16)' : 'rgba(255,230,190,0.12)'
    g.lineWidth = 0.8
    g.beginPath(); g.moveTo(px, py); g.lineTo(px + len, py + (Math.random() - 0.5) * 4); g.stroke()
  }
  noiseOver(g, s, 600, 0.04)
})

export const sheetTex = canvasTex(512, (g, s) => {
  g.fillStyle = '#f4f1e8'; g.fillRect(0, 0, s, s)
  g.strokeStyle = 'rgba(180,175,160,0.35)'; g.lineWidth = 2
  const step = 42
  for (let x = -s; x < s * 2; x += step) {
    g.beginPath(); g.moveTo(x, 0); g.lineTo(x + s, s); g.stroke()
    g.beginPath(); g.moveTo(x + s, 0); g.lineTo(x, s); g.stroke()
  }
  g.fillStyle = 'rgba(150,145,130,0.5)'
  for (let y = 10; y < s; y += 24) for (let x = 10; x < s; x += 24) {
    g.beginPath(); g.arc(x + ((y / 24) % 2) * 12, y, 1.6, 0, Math.PI * 2); g.fill()
  }
  g.strokeStyle = 'rgba(140,130,115,0.6)'; g.lineWidth = 1.5
  g.setLineDash([6, 4])
  for (const hy of [26, s - 26]) { g.beginPath(); g.moveTo(0, hy); g.lineTo(s, hy); g.stroke() }
  g.setLineDash([])
  noiseOver(g, s, 1400, 0.035)
  g.fillStyle = 'rgba(120,115,100,0.10)'
  for (let y = 0; y < s; y += 4) g.fillRect(0, y, s, 1)
  for (let x = 0; x < s; x += 4) g.fillRect(x, 0, 1, s)
}, 2, 2)

export const portraitTex = canvasTex(256, (g, s) => {
  const h = s * 1.25
  g.fillStyle = '#b3552e'; g.fillRect(0, 0, s, h)
  g.fillStyle = 'rgba(255,220,170,0.25)'; g.fillRect(0, 0, s, h * 0.3)
  g.fillStyle = '#2b2b33'; g.fillRect(s * 0.2, h * 0.55, s * 0.6, h * 0.45)
  g.fillStyle = '#1c1c22'; g.fillRect(s * 0.2, h * 0.55, s * 0.06, h * 0.45)
  g.fillStyle = '#f2ede2'; g.fillRect(s * 0.44, h * 0.55, s * 0.12, h * 0.45)
  g.fillStyle = '#d9a37e'
  g.beginPath(); g.ellipse(s / 2, h * 0.42, s * 0.13, s * 0.15, 0, 0, Math.PI * 2); g.fill()
  g.fillStyle = 'rgba(0,0,0,0.15)'
  g.beginPath(); g.ellipse(s / 2 - 20, h * 0.4, 4, 6, 0, 0, Math.PI * 2); g.fill()
  g.beginPath(); g.ellipse(s / 2 + 20, h * 0.4, 4, 6, 0, 0, Math.PI * 2); g.fill()
  g.fillStyle = '#f4f1e8'
  g.beginPath(); g.ellipse(s / 2, h * 0.26, s * 0.2, s * 0.15, 0, Math.PI, 0); g.fill()
  g.strokeStyle = 'rgba(0,0,0,0.2)'; g.lineWidth = 2
  for (let i = -2; i <= 2; i++) { g.beginPath(); g.arc(s / 2, h * 0.3, 30 + Math.abs(i) * 6, Math.PI * 1.15, Math.PI * 1.85); g.stroke() }
  g.fillStyle = '#f4f1e8'; g.fillRect(s * 0.3, h * 0.24, s * 0.4, s * 0.05)
  g.fillStyle = '#e8e8e8'
  g.beginPath(); g.moveTo(s * 0.38, h * 0.48); g.lineTo(s * 0.62, h * 0.48); g.lineTo(s / 2, h * 0.66); g.closePath(); g.fill()
})

export function tvScreenTex(on) {
  return canvasTex(256, (g) => {
    if (!on) {
      g.fillStyle = '#07080d'; g.fillRect(0, 0, 256, 180)
      const gr = g.createLinearGradient(0, 0, 256, 180)
      gr.addColorStop(0, 'rgba(255,255,255,0.16)'); gr.addColorStop(0.4, 'rgba(255,255,255,0.03)'); gr.addColorStop(1, 'rgba(255,255,255,0)')
      g.fillStyle = gr; g.fillRect(0, 0, 256, 180)
    } else {
      const gr = g.createLinearGradient(0, 0, 256, 180)
      gr.addColorStop(0, '#123a5e'); gr.addColorStop(0.55, '#1e7fa8'); gr.addColorStop(1, '#9fe8ff')
      g.fillStyle = gr; g.fillRect(0, 0, 256, 180)
      g.fillStyle = 'rgba(0,0,0,0.45)'; g.fillRect(0, 0, 256, 30)
      g.fillStyle = '#fff'; g.font = 'bold 15px sans-serif'; g.fillText('21:47', 12, 21)
      g.fillStyle = '#ffd76a'; g.beginPath(); g.arc(226, 15, 9, 0, Math.PI * 2); g.fill()
      for (let i = 0; i < 5; i++) {
        g.fillStyle = ['#ff6b6b', '#ffd93d', '#6bcb77', '#4d96ff', '#b983ff'][i]
        g.beginPath()
        if (g.roundRect) g.roundRect(14 + i * 48, 70, 36, 36, 9); else g.rect(14 + i * 48, 70, 36, 36)
        g.fill()
      }
      g.fillStyle = 'rgba(255,255,255,0.9)'; g.fillRect(14, 125, 150, 9); g.fillRect(14, 140, 90, 8)
    }
  })
}

export const aoTex = canvasTex(128, (g, s) => {
  const gr = g.createRadialGradient(s / 2, s / 2, 8, s / 2, s / 2, s / 2)
  gr.addColorStop(0, 'rgba(0,0,0,0.42)'); gr.addColorStop(0.7, 'rgba(0,0,0,0.18)'); gr.addColorStop(1, 'rgba(0,0,0,0)')
  g.fillStyle = gr; g.fillRect(0, 0, s, s)
})

export const glowTex = canvasTex(128, (g, s) => {
  const gr = g.createRadialGradient(s / 2, s / 2, 4, s / 2, s / 2, s / 2)
  gr.addColorStop(0, 'rgba(255,225,160,0.9)'); gr.addColorStop(1, 'rgba(255,225,160,0)')
  g.fillStyle = gr; g.fillRect(0, 0, s, s)
})

export const ventTex = canvasTex(128, (g, s) => {
  g.fillStyle = '#3c4044'; g.fillRect(0, 0, s, s)
  g.fillStyle = 'rgba(0,0,0,0.6)'
  for (let y = 10; y < s; y += 12) g.fillRect(10, y, s - 20, 4)
}, 2, 1)

export const knitTex = canvasTex(256, (g, s) => {
  g.fillStyle = '#cdb89b'; g.fillRect(0, 0, s, s)
  // soft waffle weave — subtle, no harsh stripes
  for (let y = 0; y < s; y += 10) for (let x = 0; x < s; x += 10) {
    const hl = ((x + y) / 10) % 2 === 0
    g.fillStyle = hl ? 'rgba(255,245,225,0.10)' : 'rgba(80,60,40,0.10)'
    g.fillRect(x + 1, y + 1, 8, 8)
    g.fillStyle = hl ? 'rgba(80,60,40,0.08)' : 'rgba(255,245,225,0.07)'
    g.fillRect(x, y + 9, 10, 1); g.fillRect(x + 9, y, 1, 10)
  }
  // fine thread lines
  for (let i = 0; i < 500; i++) {
    g.fillStyle = Math.random() > 0.5 ? 'rgba(255,250,240,0.05)' : 'rgba(70,50,30,0.05)'
    g.fillRect(Math.random() * s, Math.random() * s, 3 + Math.random() * 5, 1)
  }
  noiseOver(g, s, 500, 0.03)
}, 3, 3)

export const clothWeaveTex = canvasTex(128, (g, s) => {
  g.fillStyle = '#808080'; g.fillRect(0, 0, s, s)
  for (let y = 0; y < s; y += 3) { g.fillStyle = 'rgba(255,255,255,0.16)'; g.fillRect(0, y, s, 1) }
  for (let x = 0; x < s; x += 3) { g.fillStyle = 'rgba(0,0,0,0.16)'; g.fillRect(x, 0, 1, s) }
  for (let i = 0; i < 44; i++) {
    g.fillStyle = Math.random() > 0.4 ? 'rgba(255,255,255,0.28)' : 'rgba(0,0,0,0.22)'
    g.fillRect(Math.random() * s, Math.random() * s, 3 + Math.random() * 6, 1)
  }
}, 4, 4, false)

/* ------------------------------ materials ------------------------------- */
export const wallMat = new THREE.MeshStandardMaterial({ color: 0xf2efe8, roughness: 0.95, bumpMap: plasterTex, bumpScale: 0.6 })
export const ceilMat = new THREE.MeshStandardMaterial({ color: 0xf7f4ec, roughness: 1 })
export const skirtMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.55 })
export const bedFrameMat = new THREE.MeshStandardMaterial({ color: 0x3a241a, roughness: 0.5 })
export const sheetMat = new THREE.MeshStandardMaterial({ map: sheetTex, bumpMap: sheetTex, bumpScale: 0.15, roughness: 0.92 })
export const blanketMat = new THREE.MeshStandardMaterial({ map: knitTex, roughness: 0.96 })
export const accentMat = new THREE.MeshStandardMaterial({ color: 0xb3552e, roughness: 0.9 })
export const greyMetalMat = new THREE.MeshStandardMaterial({ map: brushedTex, roughnessMap: brushedRough, color: 0xbfc4c7, roughness: 1.0, metalness: 0.55 })
export const chromeMat = new THREE.MeshStandardMaterial({ color: 0xd7dde2, roughness: 0.16, metalness: 0.95 })
export const darkMetalMat = new THREE.MeshStandardMaterial({ color: 0x3c4044, roughness: 0.5, metalness: 0.4 })
export const woodMat = new THREE.MeshStandardMaterial({ map: woodTex, roughness: 0.48 })
export const frameWoodMat = new THREE.MeshStandardMaterial({ color: 0x4a2c17, roughness: 0.45 })
export const edgeBandMat = new THREE.MeshStandardMaterial({ color: 0x2e1a0d, roughness: 0.5 })
export const mintMat = new THREE.MeshStandardMaterial({ color: 0xa8ccc9, roughness: 0.85, bumpMap: clothWeaveTex, bumpScale: 0.12, side: THREE.DoubleSide })
export const pinkMat = new THREE.MeshStandardMaterial({ color: 0xe8cfcf, roughness: 0.85, bumpMap: clothWeaveTex, bumpScale: 0.12, side: THREE.DoubleSide })
export const navyMat = new THREE.MeshStandardMaterial({ color: 0x232c4e, roughness: 0.65 })
export const oliveMat = new THREE.MeshStandardMaterial({ color: 0x6b7256, roughness: 1, bumpMap: clothWeaveTex, bumpScale: 0.12 })
export const paleBlueMat = new THREE.MeshStandardMaterial({ color: 0xb9cdd6, roughness: 1, bumpMap: clothWeaveTex, bumpScale: 0.12 })
export const whiteClothMat = new THREE.MeshStandardMaterial({ color: 0xece7db, roughness: 1, bumpMap: clothWeaveTex, bumpScale: 0.12 })
export const mustardMat = new THREE.MeshStandardMaterial({ color: 0xd9a441, roughness: 1, bumpMap: clothWeaveTex, bumpScale: 0.12 })
export const roseMat = new THREE.MeshStandardMaterial({ color: 0xc98a8a, roughness: 1, bumpMap: clothWeaveTex, bumpScale: 0.12 })
export const glassMat = new THREE.MeshStandardMaterial({ color: 0x9fb6c9, roughness: 0.08, metalness: 0.4, transparent: true, opacity: 0.45 })

/* ---------- cozy / clutter mats (used by cozyDetails + extraDetails) ---------- */
export const rugTex = canvasTex(512, (g, s) => {
  g.fillStyle = '#a8432e'; g.fillRect(0, 0, s, s)
  // mottled base
  for (let i = 0; i < 26; i++) {
    const px = Math.random() * s, py = Math.random() * s, pr = 40 + Math.random() * 110
    const mg = g.createRadialGradient(px, py, 4, px, py, pr)
    mg.addColorStop(0, Math.random() > 0.5 ? 'rgba(255,200,150,0.07)' : 'rgba(60,20,10,0.09)')
    mg.addColorStop(1, 'rgba(0,0,0,0)')
    g.fillStyle = mg; g.fillRect(0, 0, s, s)
  }
  // cream double border
  g.strokeStyle = '#e8dcc4'; g.lineWidth = 14; g.strokeRect(18, 18, s - 36, s - 36)
  g.strokeStyle = '#7a2e1e'; g.lineWidth = 5; g.strokeRect(34, 34, s - 68, s - 68)
  g.strokeStyle = '#e8dcc4'; g.lineWidth = 3; g.strokeRect(46, 46, s - 92, s - 92)
  // diamond lattice
  g.strokeStyle = 'rgba(232,220,196,0.55)'; g.lineWidth = 3
  const step = 64
  for (let x = 64; x < s - 40; x += step) for (let y = 64; y < s - 40; y += step) {
    g.beginPath(); g.moveTo(x, y - 18); g.lineTo(x + 18, y); g.lineTo(x, y + 18); g.lineTo(x - 18, y); g.closePath(); g.stroke()
    g.fillStyle = 'rgba(232,220,196,0.5)'
    g.beginPath(); g.arc(x, y, 3.5, 0, Math.PI * 2); g.fill()
  }
  // center medallion
  g.strokeStyle = '#e8dcc4'; g.lineWidth = 5
  g.beginPath(); g.moveTo(s/2, s/2 - 52); g.lineTo(s/2 + 52, s/2); g.lineTo(s/2, s/2 + 52); g.lineTo(s/2 - 52, s/2); g.closePath(); g.stroke()
  g.strokeStyle = 'rgba(232,220,196,0.7)'; g.lineWidth = 2.5
  g.beginPath(); g.moveTo(s/2, s/2 - 34); g.lineTo(s/2 + 34, s/2); g.lineTo(s/2, s/2 + 34); g.lineTo(s/2 - 34, s/2); g.closePath(); g.stroke()
  noiseOver(g, s, 1500, 0.05)
  // pile streaks
  for (let i = 0; i < 700; i++) {
    g.fillStyle = Math.random() > 0.5 ? 'rgba(255,220,180,0.05)' : 'rgba(40,15,8,0.06)'
    g.fillRect(Math.random() * s, Math.random() * s, 4 + Math.random() * 6, 1)
  }
}, 1, 1)
export const rugMat = new THREE.MeshStandardMaterial({ map: rugTex, roughness: 0.98, bumpMap: clothWeaveTex, bumpScale: 0.2 })
export const terracottaMat = new THREE.MeshStandardMaterial({ color: 0xb56545, roughness: 0.85, bumpMap: plasterTex, bumpScale: 0.2 })
export const soilMat = new THREE.MeshStandardMaterial({ color: 0x2e2119, roughness: 1 })
export const leafMat = new THREE.MeshStandardMaterial({ color: 0x2f6b3a, roughness: 0.7, side: THREE.DoubleSide })
export const leafMat2 = new THREE.MeshStandardMaterial({ color: 0x4a8a4d, roughness: 0.7, side: THREE.DoubleSide })
export const creamCeramicMat = new THREE.MeshStandardMaterial({ color: 0xefe8da, roughness: 0.35 })
export const blackPlasticMat = new THREE.MeshStandardMaterial({ color: 0x17181c, roughness: 0.55 })
export const brassMat = new THREE.MeshStandardMaterial({ color: 0xc9a24a, roughness: 0.3, metalness: 0.85 })
export const bookPageMat = new THREE.MeshStandardMaterial({ color: 0xf0ead8, roughness: 0.9 })
export const lampshadeMat = new THREE.MeshStandardMaterial({ color: 0xf3e3c2, roughness: 0.9, emissive: 0xffc98a, emissiveIntensity: 0.25, side: THREE.DoubleSide })
export const cushionTealMat = new THREE.MeshStandardMaterial({ color: 0x3f7a7a, roughness: 0.95, bumpMap: clothWeaveTex, bumpScale: 0.15 })
export const cushionRustMat = new THREE.MeshStandardMaterial({ color: 0xc06a35, roughness: 0.95, bumpMap: clothWeaveTex, bumpScale: 0.15 })
export const throwStripeTex = canvasTex(256, (g, s) => {
  const cols = ['#b3552e', '#e8dcc4', '#2e4a6b', '#d9a441', '#7a2e1e']
  const w = s / cols.length
  cols.forEach((c, i) => { g.fillStyle = c; g.fillRect(i * w, 0, w, s) })
  g.fillStyle = 'rgba(255,255,255,0.08)'
  for (let y = 0; y < s; y += 4) g.fillRect(0, y, s, 1)
  noiseOver(g, s, 600, 0.04)
}, 2, 1)
export const throwMat = new THREE.MeshStandardMaterial({ map: throwStripeTex, roughness: 0.97, bumpMap: clothWeaveTex, bumpScale: 0.15, side: THREE.DoubleSide })
export function posterTex(draw) { return canvasTex(256, draw) }
export const woodDarkMat = new THREE.MeshStandardMaterial({ map: woodTex, color: 0x9a7350, roughness: 0.55 })

/* ----------------- harshit-room mats (same furniture, deeper craft) ------ */
export const slateMat = new THREE.MeshStandardMaterial({ color: 0x6b8494, roughness: 0.92, bumpMap: clothWeaveTex, bumpScale: 0.15 })
export const purpleMat = new THREE.MeshStandardMaterial({ color: 0x591a8c, roughness: 0.92, bumpMap: clothWeaveTex, bumpScale: 0.15, side: THREE.DoubleSide })
export const pinkCurtainMat = new THREE.MeshStandardMaterial({ color: 0xeb849e, roughness: 0.88, bumpMap: clothWeaveTex, bumpScale: 0.12, side: THREE.DoubleSide })
export const tealCurtainMat = new THREE.MeshStandardMaterial({ color: 0x2e949e, roughness: 0.88, bumpMap: clothWeaveTex, bumpScale: 0.12, side: THREE.DoubleSide })
export const redBucketMat = new THREE.MeshStandardMaterial({ color: 0xd91f1f, roughness: 0.42 })
export const coffeeMat = new THREE.MeshStandardMaterial({ color: 0x2a1408, roughness: 0.18 })
export const waterMat = new THREE.MeshStandardMaterial({ color: 0x59a6d6, roughness: 0.06, transparent: true, opacity: 0.75 })
export const labelMat = new THREE.MeshStandardMaterial({ color: 0xefe9da, roughness: 0.7 })
export const meshMat = new THREE.MeshStandardMaterial({ color: 0x1a1b1f, roughness: 0.9, bumpMap: clothWeaveTex, bumpScale: 0.3 })
export const pinkLedMat = new THREE.MeshStandardMaterial({ color: 0xff4d6d, emissive: 0xff0f4d, emissiveIntensity: 3.2, roughness: 0.4 })
export const cyanLedMat = new THREE.MeshStandardMaterial({ color: 0x66e0ff, emissive: 0x00c8ff, emissiveIntensity: 3.0, roughness: 0.4 })
export const warmBulbMat = new THREE.MeshStandardMaterial({ color: 0xfff3d9, emissive: 0xffc46b, emissiveIntensity: 2.4, roughness: 0.25 })
export const screenOffMat = new THREE.MeshStandardMaterial({ color: 0x05070c, roughness: 0.25, metalness: 0.1 })

export function laptopScreenTex(on) {
  return canvasTex(256, (g) => {
    if (!on) {
      g.fillStyle = '#07080d'; g.fillRect(0, 0, 256, 180)
      const gr = g.createLinearGradient(0, 0, 256, 180)
      gr.addColorStop(0, 'rgba(255,255,255,0.14)'); gr.addColorStop(0.4, 'rgba(255,255,255,0.03)'); gr.addColorStop(1, 'rgba(255,255,255,0)')
      g.fillStyle = gr; g.fillRect(0, 0, 256, 180)
    } else {
      const gr = g.createLinearGradient(0, 0, 256, 180)
      gr.addColorStop(0, '#0d2137'); gr.addColorStop(0.55, '#14506e'); gr.addColorStop(1, '#7fd4f2')
      g.fillStyle = gr; g.fillRect(0, 0, 256, 180)
      g.fillStyle = 'rgba(0,0,0,0.5)'; g.fillRect(0, 0, 256, 26)
      g.fillStyle = '#ff5f57'; g.beginPath(); g.arc(14, 13, 5, 0, Math.PI * 2); g.fill()
      g.fillStyle = '#febc2e'; g.beginPath(); g.arc(28, 13, 5, 0, Math.PI * 2); g.fill()
      g.fillStyle = '#28c840'; g.beginPath(); g.arc(42, 13, 5, 0, Math.PI * 2); g.fill()
      g.fillStyle = '#fff'; g.font = 'bold 12px monospace'; g.fillText('~/harshit-room', 60, 17)
      const cols = ['#7ee787', '#79c0ff', '#ffa657', '#d2a8ff', '#ff7b72']
      for (let r = 0; r < 7; r++) {
        let x = 14
        const segs = 2 + ((r * 7) % 3)
        for (let sgm = 0; sgm < segs; sgm++) {
          const w = 24 + ((r * 31 + sgm * 17) % 60)
          g.fillStyle = cols[(r + sgm) % cols.length]
          if (g.roundRect) g.roundRect(x, 40 + r * 18, w, 9, 4); else g.rect(x, 40 + r * 18, w, 9)
          g.fill()
          x += w + 8
          if (x > 230) break
        }
      }
    }
  })
}
