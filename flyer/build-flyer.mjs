// Build-Skript für den Rennradkasko-Auslege-Flyer.
// 1. Erzeugt QR-Codes offline (kein externer Dienst) und schreibt sie ins HTML.
// 2. Rendert die druckfertigen PDFs (Druckerei + Heimdruck) via Headless-Chromium.
//
// Aufruf:  node build-flyer.mjs
// Voraussetzung: qrcode (lokal via npm) + Playwright (global vorhanden).

import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { execSync } from 'node:child_process';
import { createRequire } from 'node:module';
import QRCode from 'qrcode';

const require = createRequire(import.meta.url);
const __dirname = dirname(fileURLToPath(import.meta.url));

// Playwright liegt global – über npm root -g auflösen.
const globalRoot = execSync('npm root -g').toString().trim();
const { chromium } = require(join(globalRoot, 'playwright'));

const HTML = join(__dirname, 'rennradkasko-flyer.html');

const LINKS = {
  web: 'https://rennradkasko.de',
  wa:  'https://wa.me/4915224827997?text=Hi%20Ludwig%2C%20ich%20interessiere%20mich%20f%C3%BCr%20die%20Fahrradkasko.',
};

// ---- QR-Code als scharfes SVG erzeugen (schwarz auf weiß = beste Scan-Sicherheit) ----
async function qrSvg(text) {
  let svg = await QRCode.toString(text, {
    type: 'svg',
    errorCorrectionLevel: 'Q',
    margin: 1,
    color: { dark: '#0B0A0F', light: '#ffffff' },
  });
  // feste Größen entfernen, damit CSS die Größe bestimmt
  svg = svg.replace(/\s(width|height)="[^"]*"/g, '');
  svg = svg.replace('<svg ', '<svg preserveAspectRatio="xMidYMid meet" ');
  return svg.replace(/\n/g, '');
}

function inject(html, name, svg) {
  const re = new RegExp(`(<!--QR_${name}_START-->)([\\s\\S]*?)(<!--QR_${name}_END-->)`, 'g');
  return html.replace(re, `$1${svg}$3`);
}

async function main() {
  // 1) QR-Codes ins HTML schreiben (idempotent)
  const qrWeb = await qrSvg(LINKS.web);
  const qrWa  = await qrSvg(LINKS.wa);
  let html = await readFile(HTML, 'utf8');
  html = inject(html, 'WEB', qrWeb);
  html = inject(html, 'WA', qrWa);
  await writeFile(HTML, html, 'utf8');
  console.log('✓ QR-Codes erzeugt und ins HTML eingebettet');

  // 2) PDFs rendern
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + HTML, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);

  // Druckerei-Version: 303×216 mm (A4 quer + 3 mm Beschnitt), Schnitt-/Falzmarken
  await page.evaluate(() => { document.documentElement.className = 'mode-druck'; });
  await page.pdf({
    path: join(__dirname, 'rennradkasko-flyer-druck.pdf'),
    width: '303mm', height: '216mm', printBackground: true, pageRanges: '1-2',
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  });
  console.log('✓ rennradkasko-flyer-druck.pdf (Druckerei, mit Beschnitt & Marken)');

  // Heimdruck-Version: exakt A4 quer, kein Beschnitt, dezente Falzmarken
  await page.evaluate(() => { document.documentElement.className = 'mode-heim'; });
  await page.pdf({
    path: join(__dirname, 'rennradkasko-flyer-a4.pdf'),
    width: '297mm', height: '210mm', printBackground: true, pageRanges: '1-2',
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  });
  console.log('✓ rennradkasko-flyer-a4.pdf (Heimdruck, A4 quer)');

  // Vorschau-PNGs zur Sichtkontrolle
  await page.evaluate(() => { document.documentElement.className = 'mode-druck'; });
  const sheets = await page.$$('.sheet');
  const names = ['aussen', 'innen'];
  for (let i = 0; i < sheets.length; i++) {
    await sheets[i].screenshot({ path: join(__dirname, `preview-${names[i]}.png`), scale: 'css' });
  }
  console.log('✓ preview-aussen.png / preview-innen.png');

  await browser.close();
}

main().catch((e) => { console.error(e); process.exit(1); });
