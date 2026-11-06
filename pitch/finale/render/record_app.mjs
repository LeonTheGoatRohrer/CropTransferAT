// Screen recording of the real website for the product part: field D, then its neighbour field E.
// The page runs the real analysis first; capture starts only when everything is loaded, so that no empty state is filmed.
// Each shot follows the narration. It is captured frame by frame while the page really scrolls and really reacts to clicks,
// so there are no dropped frames and it re-renders at any resolution (deviceScaleFactor).
// Usage: node record_app.mjs probe    review stills of every shot, ../export/app/probe_*.jpg
//        node record_app.mjs [--only=d_alarm,e_alarm]   ../export/app/<shot>.webm
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const out = path.resolve(here, '../export/app');
const toolDir = process.env.DG_PLAYWRIGHT || 'C:/Users/mario/Documents/HomeProjects/PreSlide/.claude/worktrees/finale-video-5min-84f3dd/deliverables/finale_video/tools';
const require = createRequire(path.join(toolDir, 'package.json'));
const { chromium } = require('playwright-core');
const CHROME = `${process.env.LOCALAPPDATA}/ms-playwright/chromium-1243/chrome-win64/chrome.exe`;
const URL = process.env.DG_WEB || 'http://localhost:5180';
const FPS = 25;
const probe = process.argv[2] === 'probe';
fs.mkdirSync(out, { recursive: true });

// y0, y1: page scroll during the shot. act: [second, async page => ...] a real interaction during the shot.
const tab = (name) => (p) => p.getByRole('tab', { name }).first().click();
const reveal = (p) => p.getByRole('button', { name: 'Ergebnis aufdecken' }).click();
const SHOTS = [
  { file: 'd_map', field: 'D', y0: 0, y1: 0, dur: 5.7, before: tab('Gemessener Ertrag'), act: [2.6, tab('Schwache Zonen')] },
  { file: 'd_curve', field: 'D', y0: 2265, y1: 2285, dur: 3.1 },
  { file: 'd_alarm', field: 'D', y0: 1098, y1: 1098, dur: 4.9, act: [1.5, reveal] },     // this scroll hides the half-cut eyebrow line
  { file: 'e_alarm', field: 'E', y0: 1098, y1: 1098, dur: 3.9, before: reveal },
  { file: 'e_map', field: 'E', y0: 0, y1: 0, dur: 4.3, before: tab('Schwache Zonen') },
];

async function openField(page, letter) {
  await page.goto(`${URL}/analyse`, { waitUntil: 'networkidle' });
  await page.locator('aside button').filter({ hasText: new RegExp(`^${letter}`) }).first().click();
  await page.getByRole('button', { name: 'Feld analysieren' }).click();
  await page.getByRole('button', { name: 'Ganzes Ergebnis' }).waitFor({ timeout: 90000 });
  await page.waitForTimeout(800);
  // Scroll once through the whole page so that every chart that animates in view has finished: no half-drawn states on film.
  const h = await page.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < h; y += 500) { await page.evaluate((v) => window.scrollTo({ top: v, behavior: 'instant' }), y); await page.waitForTimeout(250); }
  await page.waitForTimeout(800);
}
const scroll = (page, y) => page.evaluate((v) => window.scrollTo({ top: v, behavior: 'instant' }), y);

const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, reducedMotion: 'reduce', locale: 'de-AT' });
const page = await ctx.newPage();
page.on('pageerror', (e) => console.error('PAGE ERROR', e.message));

const only = process.argv.find((a) => a.startsWith('--only='))?.slice(7).split(',');
for (const s of SHOTS) {
  if (only && !only.includes(s.file)) continue;
  await openField(page, s.field);                         // a fresh analysis per shot: every reveal button starts closed
  await scroll(page, s.y0);
  await page.waitForTimeout(1500);
  if (s.before) await s.before(page).catch((e) => console.error('before', s.file, e.message));
  await scroll(page, s.y0);
  await page.waitForTimeout(s.y0 === 0 ? 3500 : 900);     // map tiles need time; nothing is captured before they are there
  if (probe) {
    await page.screenshot({ path: path.join(out, `probe_${s.file}_a.jpg`), type: 'jpeg', quality: 80 });
    if (s.act) { await s.act[1](page).catch((e) => console.error('act', s.file, e.message)); await page.waitForTimeout(1500); await scroll(page, s.y1); }
    await page.screenshot({ path: path.join(out, `probe_${s.file}_b.jpg`), type: 'jpeg', quality: 80 });
    continue;
  }
  const file = path.join(out, `${s.file}.webm`);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '22', '-cpu-used', '5', '-row-mt', '1', '-pix_fmt', 'yuv420p', file], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.round(s.dur * FPS);
  let acted = false;
  for (let i = 0; i < n; i++) {
    const k = i / (n - 1), e = k * k * (3 - 2 * k);
    await scroll(page, s.y0 + (s.y1 - s.y0) * e);
    if (s.act && !acted && i / FPS >= s.act[0]) { await s.act[1](page).catch((er) => console.error('act', s.file, er.message)); acted = true; await page.waitForTimeout(400); await scroll(page, s.y0 + (s.y1 - s.y0) * e); }
    const jpg = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(jpg)) await new Promise((r) => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  console.log('recorded', s.file);
}
await browser.close();
