#!/usr/bin/env node
/**
 * draw.io ファイルを SVG にエクスポート
 * Puppeteer + draw.io オンラインエディタを使用
 */

const fs = require('fs');
const path = require('path');

async function convertDrawioToSvg() {
  const puppeteer = require('puppeteer');
  const scriptDir = __dirname;
  const drawioFiles = fs.readdirSync(scriptDir)
    .filter(f => f.endsWith('.drawio'));
  
  if (drawioFiles.length === 0) {
    console.log('✗ .drawio ファイルが見つかりません');
    process.exit(1);
  }
  
  console.log(`\n📊 ${drawioFiles.length} 個のファイルをエクスポート中...\n`);
  
  const browser = await puppeteer.launch({ headless: true });
  
  for (const file of drawioFiles) {
    const filePath = path.join(scriptDir, file);
    const outputFile = path.join(scriptDir, path.parse(file).name + '.svg');
    
    try {
      const page = await browser.newPage();
      console.log(`処理中: ${file}`);
      
      //ファイルの内容を読み込み
      const xmlContent = fs.readFileSync(filePath, 'utf-8');
      
      // オンラインエディタでファイル打開
      const url = 'https://app.diagrams.net/';
      await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
      
      // XML をアップロード
      await page.evaluate((xml) => {
        try {
          // 既存の XML をクリア
          if (window.mxEditor && window.mxEditor.graph) {
            const doc = mxUtils.parseXml(xml);
            const codec = new mxCodec(doc);
            codec.decode(doc.documentElement, window.mxEditor.graph.getModel());
            window.mxEditor.graph.refresh();
          }
        } catch (e) {
          console.log('Error:', e.message);
        }
      }, xmlContent);
      
      // 待機
      await new Promise(r => setTimeout(r, 3000));
      
      // エクスポート実行
      const svg = await page.evaluate(() => {
        try {
          // SVG コンテナを取得
          const svg = document.querySelector('svg[class*="container"]') || 
                      document.querySelector('svg');
          if (svg) {
            return new XMLSerializer().serializeToString(svg);
          }
        } catch (e) {
          console.log('Serialize error:', e);
        }
        return null;
      });
      
      if (svg) {
        fs.writeFileSync(outputFile, `<?xml version="1.0" encoding="UTF-8"?>\n${svg}`, 'utf-8');
        console.log(`✓ 完了: ${path.parse(outputFile).name}.svg\n`);
      } else {
        console.log(`⚠ 警告: SVG 取得失敗\n`);
      }
      
      await page.close();
      
    } catch (error) {
      console.log(`✗ エラー: ${file}`);
      console.log(`  ${error.message}\n`);
    }
  }
  
  await browser.close();
  console.log('✓ エクスポート処理完了！');
  process.exit(0);
}

convertDrawioToSvg().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
