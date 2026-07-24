// Build-Skript für die Rennradkasko-Auslege-Flyer.
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
const globalRoot = execSync('npm root -g').toString().trim();
const { chromium } = require(join(globalRoot, 'playwright'));

// Kurze Payloads -> QR-Code mit wenigen Modulen -> auch bei ~16-20 mm sicher scanbar.
const LINKS = {
  web: 'https://rennradkasko.de',
  wa:  'https://wa.me/4915224827997',   // öffnet direkt den WhatsApp-Chat mit 0152 24827997
};

// Zu bauende Varianten
const TARGETS = [
  { html: 'rennradkasko-flyer.html',    base: 'rennradkasko-flyer',    label: 'Wickelfalz DIN lang' },
  { html: 'rennradkasko-flyer-a5.html', base: 'rennradkasko-flyer-a5', label: 'Einbruchfalz A5' },
];

async function qrSvg(text) {
  let svg = await QRCode.toString(text, {
    type: 'svg', errorCorrectionLevel: 'M', margin: 2,
    color: { dark: '#0B0A0F', light: '#ffffff' },
  });
  svg = svg.replace(/\s(width|height)="[^"]*"/g, '');
  svg = svg.replace('<svg ', '<svg preserveAspectRatio="xMidYMid meet" ');
  return svg.replace(/\n/g, '');
}

function inject(html, name, svg) {
  const re = new RegExp(`(<!--QR_${name}_START-->)([\\s\\S]*?)(<!--QR_${name}_END-->)`, 'g');
  return html.replace(re, `$1${svg}$3`);
}

async function buildTarget(page, t, qrWeb, qrWa) {
  const htmlPath = join(__dirname, t.html);
  let html = await readFile(htmlPath, 'utf8');
  html = inject(html, 'WEB', qrWeb);
  html = inject(html, 'WA', qrWa);
  await writeFile(htmlPath, html, 'utf8');

  await page.goto('file://' + htmlPath, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);

  await page.evaluate(() => { document.documentElement.className = 'mode-druck'; });
  await page.pdf({
    path: join(__dirname, `${t.base}-druck.pdf`),
    width: '303mm', height: '216mm', printBackground: true, pageRanges: '1-2',
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  });

  await page.evaluate(() => { document.documentElement.className = 'mode-heim'; });
  await page.pdf({
    path: join(__dirname, `${t.base}-a4.pdf`),
    width: '297mm', height: '210mm', printBackground: true, pageRanges: '1-2',
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  });

  await page.evaluate(() => { document.documentElement.className = 'mode-druck'; });
  const sheets = await page.$$('.sheet');
  for (let i = 0; i < sheets.length; i++) {
    await sheets[i].screenshot({ path: join(__dirname, `preview-${t.base}-${i === 0 ? 'aussen' : 'innen'}.png`), scale: 'css' });
  }
  console.log(`✓ ${t.label}: ${t.base}-druck.pdf · ${t.base}-a4.pdf · Previews`);
}

async function main() {
  const qrWeb = await qrSvg(LINKS.web);
  const qrWa  = await qrSvg(LINKS.wa);
  console.log('✓ QR-Codes erzeugt (Website + direkter WhatsApp-Chat)');

  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const t of TARGETS) await buildTarget(page, t, qrWeb, qrWa);
  await browser.close();
  console.log('Fertig.');
}

main().catch((e) => { console.error(e); process.exit(1); });
