// Сквозной тест WebRTC оператора: headless Chromium открывает tests/wss/softphone.html,
// регистрируется по WSS, ждёт звонок из очереди (его запускает CALLER_CMD), отвечает
// и проверяет ICE/DTLS и RTP в обе стороны.
//
//   CALLER_CMD='sipp 192.168.56.10:5060 -sf tests/sipp/uac-call-audio.xml ...' \
//   OP_PASSWORD='...' node tests/wss/webrtc_e2e.js
//
// Нужны Node.js и Playwright с Chromium. Код возврата 0 — звук идёт в обе стороны.
const path = require('path');
const { exec } = require('child_process');
const { chromium } = require('playwright');

const env = (k, d) => process.env[k] || d;
const WSS = env('WSS_URL', 'wss://192.168.57.10:8443');
const URI = env('OP_URI', 'sip:1001@bii.pbx.test');
const PASSWORD = env('OP_PASSWORD', '');
const CALLER_CMD = env('CALLER_CMD', '');

(async () => {
  const browser = await chromium.launch({
    args: ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream',
           '--ignore-certificate-errors', '--no-proxy-server'],
  });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, permissions: ['microphone'] });
  await ctx.addInitScript(() => {
    window.__pcs = [];
    const Orig = window.RTCPeerConnection;
    window.RTCPeerConnection = function (...a) { const pc = new Orig(...a); window.__pcs.push(pc); return pc; };
    window.RTCPeerConnection.prototype = Orig.prototype;
  });
  const page = await ctx.newPage();
  const status = (p) => page.waitForFunction((pre) => document.getElementById('status').textContent.startsWith(pre), p.text, { timeout: p.timeout });

  await page.goto('file://' + path.resolve(__dirname, 'softphone.html'));
  await page.fill('#ws', WSS);
  await page.fill('#uri', URI);
  await page.fill('#pw', PASSWORD);
  await page.click('#reg');
  await status({ text: 'зарегистрирован', timeout: 15000 });
  console.log('регистрация по WSS: OK');

  const caller = CALLER_CMD ? new Promise((res) => exec(CALLER_CMD, (e) => res(e ? e.code : 0))) : Promise.resolve(0);
  await status({ text: 'входящий', timeout: 30000 });
  console.log('входящий звонок из очереди: OK');
  await page.click('#answer');
  await status({ text: 'разговор', timeout: 15000 });
  await page.waitForTimeout(6000);

  const rtc = await page.evaluate(async () => {
    const pc = window.__pcs[window.__pcs.length - 1];
    const r = { ice: pc.iceConnectionState, dtls: null, sent: 0, recv: 0, codec: null };
    (await pc.getStats()).forEach((s) => {
      if (s.type === 'outbound-rtp' && s.kind === 'audio') r.sent = s.packetsSent;
      if (s.type === 'inbound-rtp' && s.kind === 'audio') r.recv = s.packetsReceived;
      if (s.type === 'transport') r.dtls = s.dtlsState;
      if (s.type === 'codec') r.codec = s.mimeType;
    });
    return r;
  });
  console.log('WebRTC:', JSON.stringify(rtc));
  const callerRc = await caller;
  await browser.close();

  const ok = rtc.ice === 'connected' && rtc.dtls === 'connected' && rtc.sent > 0 && rtc.recv > 0 && callerRc === 0;
  console.log(ok ? 'ИТОГ: звук в обе стороны — OK' : `ИТОГ: ошибка (caller rc=${callerRc})`);
  process.exit(ok ? 0 : 1);
})().catch((e) => { console.error('ОШИБКА:', e.message); process.exit(1); });
