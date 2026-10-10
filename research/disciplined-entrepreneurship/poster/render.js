// Рендер poster-ru.svg → PDF (A1) и PNG-превью. Запуск: node render.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
(async () => {
  const svg = fs.readFileSync(path.join(__dirname, 'poster-ru.svg'), 'utf8');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1190, height: 1684 }, deviceScaleFactor: 2 });
  await page.setContent(`<html><body style="margin:0">${svg.replace('<svg ', '<svg style="display:block;width:100vw;height:100vh" ')}</body></html>`);
  await page.screenshot({ path: path.join(__dirname, 'poster-ru-preview.png') });
  await page.pdf({ path: path.join(__dirname, 'poster-ru.pdf'), width: '594mm', height: '841mm', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  await browser.close();
})();
