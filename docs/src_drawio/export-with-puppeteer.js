const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function convertDrawioToSvg() {
  const scriptDir = __dirname;
  const drawioFiles = fs.readdirSync(scriptDir)
    .filter(f => f.endsWith('.drawio'));
  
  if (drawioFiles.length === 0) {
    console.log('✗ .drawio ファイルが見つかりません');
    process.exit(1);
  }
  
  console.log(`\n📊 ${drawioFiles.length} 個のファイルをエクスポート中...\n`);
  
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  for (const file of drawioFiles) {
    const filePath = path.join(scriptDir, file);
    const outputFile = path.join(scriptDir, path.parse(file).name + '.svg');
    
    try {
      console.log(`処理中: ${file}`);
      
      // ファイルの内容を読み込み
      const xmlContent = fs.readFileSync(filePath, 'utf-8');
      
      // Base64 エンコード
      const data = Buffer.from(xmlContent).toString('base64');
      
      // draw.io の app URL でファイルを開く
      const url = `https://app.diagrams.net/?splash=0&dev=1&mode=0`;
      
      // ページへアクセス
      await page.goto(url, { waitUntil: 'networkidle0', timeout: 60000 }).catch(() => {});
      
      // XML をエディタに読み込む
      await page.evaluate((xmlData) => {
        try {
          if (window.mxEditor && window.mxEditor.graph) {
            const doc = mxUtils.parseXml(xmlData);
            window.mxEditor.graph.getModel().clear();
            const codec = new mxCodec(doc);
            codec.decode(doc.documentElement, window.mxEditor.graph.getModel());
            window.mxEditor.graph.refresh();
          }
        } catch (e) {
          console.log('Load error:', e);
        }
      }, xmlContent);
      
      // 待機
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // SVG としてエクスポート
      const result = await page.evaluate(() => {
        try {
          // canvas の SVG を取得
          const canvas = document.querySelector('canvas');
          if (canvas) {
            const parent = canvas.parentElement;
            const svgElements = parent.querySelectorAll('svg');
            if (svgElements.length > 0) {
              const svg = svgElements[svgElements.length - 1];
              return new XMLSerializer().serializeToString(svg);
            }
          }
        } catch (e) {
          console.log('Error:', e);
        }
        return null;
      });
      
      if (result) {
        fs.writeFileSync(outputFile, result, 'utf-8');
        console.log(`✓ 完了: ${path.parse(outputFile).name}.svg\n`);
      } else {
        console.log(`✗ SVG 取得失敗\n`);
      }
      
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
  console.error(err);
  process.exit(1);
});
