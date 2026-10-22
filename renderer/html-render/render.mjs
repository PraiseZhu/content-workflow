// usage: node render.mjs page.html [width=1200] [--scale=2]
// -> page.png (full-page long image) + page.pdf (A4, backgrounds kept)
import { chromium } from 'playwright-core';
import path from 'node:path';
const [file, w = '1200'] = process.argv.slice(2).filter(a => !a.startsWith('--'));
const scale = Number((process.argv.find(a => a.startsWith('--scale=')) || '--scale=2').split('=')[1]);
if (!file) { console.error('usage: node render.mjs page.html [width]'); process.exit(1); }
const abs = path.resolve(file), base = abs.replace(/\.html?$/, '');
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome', args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: Number(w), height: 800 }, deviceScaleFactor: scale });
const errors = [];
page.on('pageerror', e => errors.push(String(e)));
page.on('requestfailed', r => errors.push('failed: ' + r.url()));
await page.goto('file://' + abs, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);
await page.screenshot({ path: base + '.png', fullPage: true });
await page.pdf({ path: base + '.pdf', format: 'A4', printBackground: true });
await browser.close();
console.log(JSON.stringify({ png: base + '.png', pdf: base + '.pdf', errors }));
