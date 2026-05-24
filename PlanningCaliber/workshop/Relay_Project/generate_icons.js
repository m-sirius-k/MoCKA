'use strict';
// Relay v4.0 — generate_icons.js
// Run once with: node generate_icons.js
// Creates icons/icon16.png, icons/icon48.png, icons/icon128.png

const fs   = require('fs');
const zlib = require('zlib');
const path = require('path');

// ─── CRC32 ────────────────────────────────────────────────────────────────────

const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i;
    for (let j = 0; j < 8; j++) {
      c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
    }
    t[i] = c;
  }
  return t;
})();

function crc32(buf) {
  let c = 0xFFFFFFFF;
  for (let i = 0; i < buf.length; i++) {
    c = CRC_TABLE[(c ^ buf[i]) & 0xFF] ^ (c >>> 8);
  }
  return (c ^ 0xFFFFFFFF) >>> 0;
}

// ─── PNG Encoder ──────────────────────────────────────────────────────────────

function pngChunk(type, data) {
  const tb  = Buffer.from(type, 'ascii');
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([tb, data])), 0);
  return Buffer.concat([len, tb, data, crc]);
}

function encodePNG(pixels, size) {
  // RGBA (color type 6), 4 bytes per pixel
  const PNG_SIG = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(size, 0);
  ihdr.writeUInt32BE(size, 4);
  ihdr[8]  = 8; // bit depth
  ihdr[9]  = 6; // RGBA
  ihdr[10] = 0; // deflate
  ihdr[11] = 0; // filter
  ihdr[12] = 0; // no interlace

  // Raw scanlines: filter_byte + RGBA per pixel
  const raw = Buffer.alloc(size * (size * 4 + 1));
  for (let y = 0; y < size; y++) {
    raw[y * (size * 4 + 1)] = 0; // filter: None
    for (let x = 0; x < size; x++) {
      const pidx = (y * size + x) * 4;
      const ridx = y * (size * 4 + 1) + 1 + x * 4;
      raw[ridx]     = pixels[pidx];
      raw[ridx + 1] = pixels[pidx + 1];
      raw[ridx + 2] = pixels[pidx + 2];
      raw[ridx + 3] = pixels[pidx + 3];
    }
  }

  const compressed = zlib.deflateSync(raw, { level: 9 });
  return Buffer.concat([
    PNG_SIG,
    pngChunk('IHDR', ihdr),
    pngChunk('IDAT', compressed),
    pngChunk('IEND', Buffer.alloc(0)),
  ]);
}

// ─── Icon Renderer ────────────────────────────────────────────────────────────

// "R" glyph — 5 columns × 7 rows bitmap
const R_GLYPH = [
  [1,1,1,1,0],
  [1,0,0,0,1],
  [1,0,0,0,1],
  [1,1,1,1,0],
  [1,1,0,0,0],
  [1,0,1,0,0],
  [1,0,0,1,0],
];

const GLYPH_W = 5;
const GLYPH_H = 7;

// Colors (RGBA)
const C = {
  transparent: [0, 0, 0, 0],
  bg:          [10, 14, 26, 255],       // #0a0e1a
  ring:        [30, 58, 95, 255],       // #1e3a5f
  ringOuter:   [20, 40, 72, 255],       // subtle outer ring
  glyph:       [56, 189, 248, 255],     // #38bdf8 accent
  glowInner:   [16, 24, 48, 255],       // slightly lighter bg for inner circle
};

function createIcon(size) {
  const pixels = new Uint8Array(size * size * 4);

  const cx     = (size - 1) / 2;
  const cy     = (size - 1) / 2;
  const rOuter = size * 0.46;
  const rRing  = rOuter - Math.max(1, size * 0.04);
  const rInner = rOuter - Math.max(2, size * 0.08);

  // Glyph scale and offset
  const scale  = Math.max(1, Math.floor(size * 0.55 / GLYPH_W));
  const gw     = GLYPH_W * scale;
  const gh     = GLYPH_H * scale;
  const gxOff  = Math.round((size - gw) / 2);
  const gyOff  = Math.round((size - gh) / 2);

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const pidx = (y * size + x) * 4;
      const dx   = x - cx;
      const dy   = y - cy;
      const dist = Math.sqrt(dx * dx + dy * dy);

      let color;

      if (dist > rOuter) {
        color = C.transparent;
      } else if (dist > rRing) {
        color = C.ring;
      } else if (dist > rInner) {
        color = C.ringOuter;
      } else {
        // Inside circle — check if this pixel is part of the "R"
        const gx = x - gxOff;
        const gy = y - gyOff;
        const col = Math.floor(gx / scale);
        const row = Math.floor(gy / scale);

        if (row >= 0 && row < GLYPH_H && col >= 0 && col < GLYPH_W && R_GLYPH[row][col]) {
          color = C.glyph;
        } else {
          color = C.bg;
        }
      }

      pixels[pidx]     = color[0];
      pixels[pidx + 1] = color[1];
      pixels[pidx + 2] = color[2];
      pixels[pidx + 3] = color[3];
    }
  }

  return encodePNG(pixels, size);
}

// ─── Main ─────────────────────────────────────────────────────────────────────

const iconDir = path.join(__dirname, 'icons');
if (!fs.existsSync(iconDir)) {
  fs.mkdirSync(iconDir, { recursive: true });
}

for (const size of [16, 48, 128]) {
  const png      = createIcon(size);
  const outPath  = path.join(iconDir, `icon${size}.png`);
  fs.writeFileSync(outPath, png);
  console.log(`[Relay] Created ${outPath} (${png.length} bytes)`);
}

console.log('[Relay] Icons generated successfully.');
