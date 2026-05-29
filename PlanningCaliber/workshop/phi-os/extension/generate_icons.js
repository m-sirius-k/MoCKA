// generate_icons.js — PHI OS アイコン生成スクリプト
// Node.js で実行: node generate_icons.js
// 依存: canvas (npm install canvas)
// canvas が使えない場合は手動でicon16/48/128.pngを用意してください

const fs   = require('fs');
const path = require('path');

function createIconBuffer(size) {
  try {
    const { createCanvas } = require('canvas');
    const canvas = createCanvas(size, size);
    const ctx    = canvas.getContext('2d');

    // Background
    ctx.fillStyle = '#0a0e1a';
    ctx.beginPath();
    ctx.roundRect(0, 0, size, size, size * 0.18);
    ctx.fill();

    // Border
    ctx.strokeStyle = '#1e3a5f';
    ctx.lineWidth   = Math.max(1, size * 0.04);
    ctx.beginPath();
    ctx.roundRect(
      ctx.lineWidth / 2, ctx.lineWidth / 2,
      size - ctx.lineWidth, size - ctx.lineWidth,
      size * 0.16
    );
    ctx.stroke();

    // Phi symbol (Φ)
    ctx.fillStyle   = '#38bdf8';
    ctx.textAlign   = 'center';
    ctx.textBaseline = 'middle';
    ctx.font        = `bold ${size * 0.6}px serif`;
    ctx.fillText('Φ', size / 2, size / 2 + size * 0.03);

    return canvas.toBuffer('image/png');
  } catch (e) {
    console.warn('canvas not available, creating placeholder:', e.message);
    return null;
  }
}

const iconsDir = path.join(__dirname, 'icons');
if (!fs.existsSync(iconsDir)) fs.mkdirSync(iconsDir);

[16, 48, 128].forEach(size => {
  const outPath = path.join(iconsDir, `icon${size}.png`);
  if (fs.existsSync(outPath)) {
    console.log(`  icon${size}.png already exists, skipping`);
    return;
  }
  const buf = createIconBuffer(size);
  if (buf) {
    fs.writeFileSync(outPath, buf);
    console.log(`  Created icon${size}.png`);
  } else {
    // canvas不使用時: 最小限の1px PNGプレースホルダーを作成
    const minimal = Buffer.from([
      0x89,0x50,0x4E,0x47,0x0D,0x0A,0x1A,0x0A,0x00,0x00,0x00,0x0D,0x49,0x48,0x44,0x52,
      0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x01,0x08,0x02,0x00,0x00,0x00,0x90,0x77,0x53,
      0xDE,0x00,0x00,0x00,0x0C,0x49,0x44,0x41,0x54,0x08,0xD7,0x63,0x38,0xBD,0xF8,0x00,
      0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
      0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x03,0x00,0x38,
      0xBD,0xF8,0xFF,0x00,0x00,0x00,0x00,0x49,0x45,0x4E,0x44,0xAE,0x42,0x60,0x82,
    ]);
    fs.writeFileSync(outPath, minimal);
    console.log(`  Created placeholder icon${size}.png (run with canvas for real icons)`);
  }
});

console.log('Done.');
