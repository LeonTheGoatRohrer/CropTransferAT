// Render the motion-graphics scenes frame by frame: Canvas 2D in headless Chromium, every frame a pure function of time,
// drawn in a 1920x1080 design space. The same code renders 540p for the prototype and 1080p/4K for the final.
// Usage: node render_mg.mjs <width> scene:duration[,scene:duration...] [--still=t] [--anon]
// playwright-core is taken from DG_PLAYWRIGHT (a folder with its node_modules); it is not a dependency of this repository.
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const out = path.resolve(here, '../export');
const mg = path.join(out, 'mg');
const fonts = path.resolve(here, '../.cache/fonts');
const toolDir = process.env.DG_PLAYWRIGHT || 'C:/Users/mario/Documents/HomeProjects/PreSlide/.claude/worktrees/finale-video-5min-84f3dd/deliverables/finale_video/tools';
const require = createRequire(path.join(toolDir, 'package.json'));
const { chromium } = require('playwright-core');
const CHROME = `${process.env.LOCALAPPDATA}/ms-playwright/chromium-1243/chrome-win64/chrome.exe`;

const width = Number(process.argv[2]);
const height = Math.round(width * 9 / 16);
const scenes = process.argv[3].split(',').map((s) => s.split(':')).map(([n, d]) => [n, Number(d)]);
const stillArg = process.argv.find((a) => a.startsWith('--still='));
const still = stillArg ? stillArg.slice(8).split('|').map(Number) : null;
const anon = process.argv.includes('--anon');
const FPS = 25;

const face = (fam, file) => `@font-face{font-family:"${fam}";src:url(${pathToFileURL(path.join(fonts, file)).href});font-weight:100 900}`;
const imgs = [['freeze1', 'freeze1.png'], ['freeze2', 'freeze2.png'], ['map', 'map_ortho.jpg'], ['sat', 'sat.png']].map(([n, f]) => [n, path.join(mg, f)]).filter(([, f]) => fs.existsSync(f));
const html = `<!doctype html><meta charset="utf-8"><style>
${face('Bricolage', 'bricolage-grotesque-latin-wght-normal.ttf')}
${face('Instrument', 'instrument-sans-latin-wght-normal.ttf')}
${face('JetBrains', 'jetbrains-mono-latin-wght-normal.ttf')}
html,body{margin:0;background:#000}canvas{display:block}</style>
<span style="font-family:Bricolage;font-weight:600">.</span><span style="font-family:Instrument">.</span><span style="font-family:JetBrains">.</span>
<canvas id="c" width="${width}" height="${height}"></canvas>
<script>window.ANON=${anon};window.IMG={};${imgs.map(([n, f]) => `IMG.${n}=new Image();IMG.${n}.src=${JSON.stringify(pathToFileURL(f).href)};`).join('')}</script>
<script src="${pathToFileURL(path.join(mg, 'data.js')).href}"></script>
<script src="${pathToFileURL(path.join(mg, 'timeline.js')).href}"></script>
<script src="${pathToFileURL(path.join(here, 'scenes.js')).href}"></script>`;
const pageFile = path.join(mg, 'index.html');
fs.writeFileSync(pageFile, html);

const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ['--allow-file-access-from-files'] });
const page = await browser.newPage({ viewport: { width, height } });
page.on('pageerror', (e) => { console.error('PAGE ERROR', e.message); process.exit(1); });
await page.goto(pathToFileURL(pageFile).href);
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(500);

const clips = path.join(out, 'mgclips');
fs.mkdirSync(clips, { recursive: true });
for (const [name, dur] of scenes) {
  const suffix = anon ? '_anon' : '';
  if (still) {                                  // --still takes fractions of the scene: review frames without rendering it all
    for (const f of still) {
      await page.evaluate(([n, s, d]) => window.drawScene(n, s, d), [name, f * dur, dur]);
      await page.screenshot({ path: path.join(clips, `s_${name}${suffix}_${f}.jpg`), type: 'jpeg', quality: 85 });
    }
    continue;
  }
  const file = path.join(clips, `${name}${suffix}.mp4`);
  const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', file], { stdio: ['pipe', 'inherit', 'inherit'] });
  const frames = Math.round(dur * FPS);
  for (let i = 0; i < frames; i++) {
    await page.evaluate(([n, t, d]) => window.drawScene(n, t, d), [name, i / FPS, dur]);
    const jpg = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(jpg)) await new Promise((r) => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  console.log('rendered', name + suffix, dur);
}
await browser.close();
