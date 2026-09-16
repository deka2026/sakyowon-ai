// skimcamp-shorts : student JSON -> 9:16 30s HyperFrames composition
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { join, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = dirname(fileURLToPath(import.meta.url));
// Per-composition timings. 30s shorts and 60s longer pieces share one template;
// the title and end cards keep a fixed length so only the montage stretches.
function timings(dur) {
  const total = Number(dur) || 30;
  const titleEnd = total >= 50 ? 4.6 : 4.2;
  const endCard = total >= 50 ? 4.2 : 3.4;
  return { total, titleEnd, endStart: Math.round((total - endCard) * 100) / 100 };
}

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const r2 = (n) => Math.round(n * 100) / 100;

function buildShots(shots, TITLE_END, END_START) {
  const span = END_START - TITLE_END;
  const n = shots.length;
  const each = span / n;
  return shots.map((s, i) => ({
    ...s,
    start: r2(TITLE_END + i * each),
    dur: r2(each + (i < n - 1 ? 0.06 : 0)),
    idx: i,
  }));
}

function bubbleLayout(i) {
  const sides = ['left', 'right'];
  const tops = [0.155, 0.695, 0.135, 0.715, 0.175, 0.675];
  return { side: sides[i % 2], top: tops[i % tops.length] };
}

function buildBubbles(messages, TITLE_END, END_START) {
  const span = END_START - TITLE_END;
  const n = messages.length;
  const slot = span / n;
  return messages.map((m, i) => {
    const text = typeof m === 'string' ? m : m.text;
    const lay = bubbleLayout(i);
    const start = r2(TITLE_END + i * slot + 0.35);
    const dur = r2(Math.min(slot - 0.55, 3.6));
    return { text, start, dur, ...lay, idx: i };
  });
}

function mediaTag(s) {
  const focus = s.focus || '50% 45%';
  if (s.type === 'vid') {
    const ms = s.mediaStart != null ? ` data-media-start="${s.mediaStart}"` : '';
    return `  <video id="sv${s.idx}" class="clip vid" src="${esc(s.src)}" data-start="${s.start}" data-duration="${s.dur}"${ms} data-track-index="0" style="object-position:${focus}" muted playsinline></video>`;
  }
  return `  <div class="clip shot" id="shot${s.idx}" data-start="${s.start}" data-duration="${s.dur}" data-track-index="0">
    <img class="kb" id="kb${s.idx}" src="${esc(s.src)}" style="object-position:${focus}" alt="">
  </div>`;
}

export function buildHtml(d) {
  const { total: TOTAL, titleEnd: TITLE_END, endStart: END_START } = timings(d.duration);
  const shots = buildShots(d.shots, TITLE_END, END_START);
  const bubbles = buildBubbles(d.messages, TITLE_END, END_START);
  const id = `sc-${d.slug}`;

  const shotHtml = shots.map(mediaTag).join('\n');

  const bubbleHtml = bubbles.map((b) => `  <div class="clip bubble ${b.side}" id="bb${b.idx}" data-start="${b.start}" data-duration="${b.dur}" data-track-index="2" style="top:${(b.top * 100).toFixed(1)}%">
    <div class="bubble-in"><span>${esc(b.text)}</span></div>
  </div>`).join('\n');

  const kbTweens = shots.filter((s) => s.type !== 'vid').map((s) => {
    const mode = s.idx % 3;
    if (mode === 0) return `  tl.fromTo("#kb${s.idx}", { scale: 1.0, xPercent: 0 }, { scale: 1.13, duration: ${r2(s.dur + 0.2)}, ease: "none" }, ${s.start});`;
    if (mode === 1) return `  tl.fromTo("#kb${s.idx}", { scale: 1.15, xPercent: 0 }, { scale: 1.02, duration: ${r2(s.dur + 0.2)}, ease: "none" }, ${s.start});`;
    return `  tl.fromTo("#kb${s.idx}", { scale: 1.12, xPercent: -2.2 }, { scale: 1.12, xPercent: 2.2, duration: ${r2(s.dur + 0.2)}, ease: "none" }, ${s.start});`;
  }).join('\n');

  const bubbleTweens = bubbles.map((b) => {
    const rot = b.side === 'left' ? -2.2 : 2.2;
    const inner = `#bb${b.idx} .bubble-in`;
    return `  tl.fromTo("${inner}", { scale: 0.55, rotate: ${r2(rot * 3)}, autoAlpha: 0 }, { scale: 1, rotate: ${rot}, autoAlpha: 1, duration: 0.46, ease: "back.out(2.2)" }, ${b.start});
  tl.to("${inner}", { scale: 0.9, autoAlpha: 0, duration: 0.3, ease: "power2.in" }, ${r2(b.start + b.dur - 0.34)});
  tl.set("${inner}", { autoAlpha: 0 }, ${r2(b.start + b.dur - 0.02)});`;
  }).join('\n');

  const grainSvg = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3'/></filter><rect width='120' height='120' filter='url(%23n)'/></svg>";

  return `<!doctype html>
<!-- ${esc(d.name)} / ${esc(d.camp)} -->
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080, height=1920">
<script src="assets/vendor/gsap.min.js"></script>
<style>
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #10323F; }
@font-face { font-family: "BlackHanSans"; src: url("assets/fonts/BlackHanSans-Regular.ttf") format("truetype"); font-weight: 400; font-display: block; }
@font-face { font-family: "Jua"; src: url("assets/fonts/Jua-Regular.ttf") format("truetype"); font-weight: 400; font-display: block; }

:root {
  --sand: #FDF4E3;
  --ink: #10323F;
  --coral: #FF6A45;
  --teal: #14A0A6;
  --sun: #FFC24B;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
#${id} {
  position: relative;
  width: 1080px; height: 1920px;
  overflow: hidden;
  background: var(--ink);
  font-family: "Jua", sans-serif;
  -webkit-font-smoothing: antialiased;
}

.shot, .vid { position: absolute; inset: 0; width: 1080px; height: 1920px; }
.shot { overflow: hidden; }
.kb { position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; display: block; }
.vid { object-fit: cover; }

.vignette {
  position: absolute; inset: 0;
  background:
    radial-gradient(120% 78% at 50% 42%, rgba(0,0,0,0) 44%, rgba(6,26,34,0.42) 100%),
    linear-gradient(to bottom, rgba(6,26,34,0.50) 0%, rgba(6,26,34,0) 22%, rgba(6,26,34,0) 60%, rgba(6,26,34,0.68) 100%);
  pointer-events: none;
}
.grain {
  position: absolute; inset: 0; opacity: 0.05; mix-blend-mode: overlay;
  background-image: url("${grainSvg}");
}
.watermark {
  position: absolute; top: 66px; left: 58px;
  display: flex; align-items: center; gap: 16px;
  padding: 15px 30px 15px 22px;
  background: rgba(253,244,227,0.93);
  border: 4px solid var(--ink);
  border-radius: 999px;
  box-shadow: 8px 8px 0 rgba(16,50,63,0.35);
}
.watermark .dot { width: 26px; height: 26px; border-radius: 50%; background: var(--coral); border: 3px solid var(--ink); }
.watermark .wm-text { font-size: 30px; color: var(--ink); letter-spacing: -0.5px; }
.progress-track { position: absolute; left: 0; right: 0; bottom: 0; height: 12px; background: rgba(16,50,63,0.35); }
.progress-bar { position: absolute; left: 0; top: 0; height: 100%; width: 100%; background: var(--coral); transform-origin: 0 50%; }

.title-wrap { position: absolute; left: 64px; right: 64px; bottom: 200px; }
.camp-pill {
  display: inline-flex; align-items: center;
  padding: 14px 32px; margin-bottom: 26px;
  background: var(--sun); color: var(--ink);
  border: 5px solid var(--ink); border-radius: 999px;
  font-size: 36px; letter-spacing: -0.5px;
  box-shadow: 9px 9px 0 rgba(16,50,63,0.45);
}
.name-line { display: block; }
.name {
  display: block;
  font-family: "BlackHanSans", sans-serif;
  font-size: 168px; line-height: 1.04; color: var(--sand);
  letter-spacing: -3px;
  text-shadow: 0 10px 40px rgba(0,0,0,0.55), 7px 7px 0 rgba(255,106,69,0.92);
}
.name .suffix { font-size: 74px; color: var(--sun); margin-left: 16px; letter-spacing: -1px; }
.subtitle {
  display: block;
  margin-top: 22px; font-size: 50px; color: var(--sand);
  text-shadow: 0 6px 24px rgba(0,0,0,0.6);
}
.rule { height: 10px; background: var(--coral); border-radius: 6px; margin-top: 30px; transform-origin: 0 50%; }

.bubble { position: absolute; max-width: 720px; }
.bubble.left { left: 66px; }
.bubble.right { right: 66px; }
.bubble-in {
  position: relative;
  background: var(--sand);
  border: 7px solid var(--ink);
  border-radius: 46px;
  padding: 32px 44px;
  box-shadow: 12px 12px 0 rgba(16,50,63,0.42);
}
.bubble-in span { display: block; font-size: 54px; line-height: 1.34; color: var(--ink); letter-spacing: -1.2px; word-break: keep-all; overflow-wrap: break-word; }
.bubble-in::after {
  content: ""; position: absolute; bottom: -34px; width: 0; height: 0;
  border-left: 26px solid transparent; border-right: 26px solid transparent;
  border-top: 34px solid var(--ink);
}
.bubble.left .bubble-in::after { left: 76px; }
.bubble.right .bubble-in::after { right: 76px; }

.end-veil {
  position: absolute; inset: 0;
  background:
    linear-gradient(to bottom, rgba(8,34,44,0.30) 0%, rgba(8,34,44,0.22) 38%, rgba(8,34,44,0.80) 68%, rgba(8,34,44,0.93) 100%);
}
.end-wrap { position: absolute; left: 0; right: 0; bottom: 210px; text-align: center; padding: 0 70px; }
.end-badge {
  display: inline-block; padding: 16px 40px; margin-bottom: 28px;
  background: var(--coral); color: var(--sand);
  border: 6px solid var(--sand); border-radius: 999px;
  font-size: 44px; letter-spacing: -0.5px;
}
.end-title {
  display: block;
  font-family: "BlackHanSans", sans-serif; font-size: 120px; line-height: 1.12;
  color: var(--sand); letter-spacing: -3px; text-shadow: 0 10px 40px rgba(0,0,0,0.6);
}
.end-name { display: block; margin-top: 26px; font-size: 80px; color: var(--sun); letter-spacing: -1.5px; }
.end-camp { display: block; margin-top: 34px; font-size: 40px; color: rgba(253,244,227,0.92); }
</style>
</head>
<body>
<div id="${id}" data-composition-id="${id}" data-duration="${TOTAL}" data-fps="30" data-width="1080" data-height="1920">

  <div class="clip shot" id="heroShot" data-start="0" data-duration="${r2(TITLE_END + 0.06)}" data-track-index="0">
    <img class="kb" id="heroImg" src="${esc(d.hero.src)}" style="object-position:${d.hero.focus || '50% 32%'}" alt="">
  </div>

${shotHtml}

  <div class="clip shot" id="endShot" data-start="${END_START}" data-duration="${r2(TOTAL - END_START)}" data-track-index="0">
    <img class="kb" id="endImg" src="${esc(d.cert.src)}" style="object-position:${d.cert.focus || '50% 40%'}" alt="">
  </div>

  <div class="vignette"></div>
  <div class="grain"></div>

  <div class="clip title-wrap" id="titleCard" data-start="0" data-duration="${TITLE_END}" data-track-index="3">
    <div class="camp-pill" id="tPill">${esc(d.datePill || d.date || d.camp)}</div>
    <div class="name-line"><span class="name" id="tName">${esc(d.name)}<span class="suffix">${esc(d.suffix || '학생')}</span></span></div>
    <span class="subtitle" id="tSub">${esc(d.subtitle || '나의 첫 스킴보드 도전기')}</span>
    <div class="rule" id="tRule"></div>
  </div>

${bubbleHtml}

  <div class="clip" id="endCard" data-start="${END_START}" data-duration="${r2(TOTAL - END_START)}" data-track-index="3">
    <div class="end-veil"></div>
    <div class="end-wrap">
      <div class="end-badge" id="eBadge">${esc(d.endBadge || '수료를 축하합니다')}</div>
      <span class="end-title" id="eTitle">${esc(d.endTitle || '해냈다!')}</span>
      <span class="end-name" id="eName">${esc(d.endName || d.name + ' ' + (d.suffix || '학생'))}</span>
      <span class="end-camp" id="eCamp">${esc(d.camp)}${d.date ? ' · ' + esc(d.date) : ''}</span>
    </div>
  </div>

  <div class="watermark"><span class="dot"></span><span class="wm-text">${esc(d.camp)}</span></div>
  <div class="progress-track"><div class="progress-bar" id="pBar"></div></div>
</div>

<script>
(function () {
  const tl = gsap.timeline({ paused: true });

  tl.fromTo("#pBar", { scaleX: 0 }, { scaleX: 1, duration: ${TOTAL}, ease: "none" }, 0);

  tl.fromTo("#heroImg", { scale: 1.16 }, { scale: 1.0, duration: ${r2(TITLE_END + 0.3)}, ease: "none" }, 0);
  tl.fromTo("#tPill", { yPercent: 60, autoAlpha: 0 }, { yPercent: 0, autoAlpha: 1, duration: 0.5, ease: "back.out(1.8)" }, 0.25);
  tl.fromTo("#tName", { yPercent: 46, autoAlpha: 0 }, { yPercent: 0, autoAlpha: 1, duration: 0.62, ease: "expo.out" }, 0.42);
  tl.fromTo("#tSub", { xPercent: -8, autoAlpha: 0 }, { xPercent: 0, autoAlpha: 1, duration: 0.55, ease: "power3.out" }, 0.72);
  tl.fromTo("#tRule", { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: "power4.out" }, 0.88);
  tl.to("#tPill", { yPercent: -14, autoAlpha: 0, duration: 0.32, ease: "power2.in" }, ${r2(TITLE_END - 0.45)});
  tl.to("#tName", { yPercent: -12, autoAlpha: 0, duration: 0.34, ease: "power2.in" }, ${r2(TITLE_END - 0.42)});
  tl.to("#tSub", { autoAlpha: 0, duration: 0.3, ease: "power2.in" }, ${r2(TITLE_END - 0.4)});
  tl.to("#tRule", { scaleX: 0, duration: 0.28, ease: "power2.in" }, ${r2(TITLE_END - 0.38)});

${kbTweens}

${bubbleTweens}

  tl.fromTo("#endImg", { scale: 1.0 }, { scale: 1.1, duration: ${r2(TOTAL - END_START)}, ease: "none" }, ${END_START});
  tl.fromTo("#eBadge", { scale: 0.6, autoAlpha: 0 }, { scale: 1, autoAlpha: 1, duration: 0.5, ease: "back.out(2)" }, ${r2(END_START + 0.15)});
  tl.fromTo("#eTitle", { yPercent: 40, autoAlpha: 0 }, { yPercent: 0, autoAlpha: 1, duration: 0.6, ease: "expo.out" }, ${r2(END_START + 0.3)});
  tl.fromTo("#eName", { yPercent: 34, autoAlpha: 0 }, { yPercent: 0, autoAlpha: 1, duration: 0.55, ease: "expo.out" }, ${r2(END_START + 0.5)});
  tl.fromTo("#eCamp", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "power2.out" }, ${r2(END_START + 0.75)});

  window.__timelines["${id}"] = tl;
})();
</script>
</body>
</html>
`;
}

const args = process.argv.slice(2);
const targets = args.length
  ? args
  : readdirSync(join(ROOT, 'students')).filter((f) => f.endsWith('.json')).map((f) => basename(f, '.json'));

let lastHtml = null;
for (const t of targets) {
  const data = JSON.parse(readFileSync(join(ROOT, 'students', `${t}.json`), 'utf8'));
  const html = buildHtml(data);
  writeFileSync(join(ROOT, 'compositions', `${data.slug}.html`), html, 'utf8');
  lastHtml = html;
  console.log(`built ${data.slug} <- ${data.shots.length} shots, ${data.messages.length} bubbles, ${timings(data.duration).total}s`);
}
// the most recently built student becomes the project's active composition,
// so `hyperframes check|snapshot|render` (which open index.html) act on it.
if (lastHtml) writeFileSync(join(ROOT, 'index.html'), lastHtml, 'utf8');
