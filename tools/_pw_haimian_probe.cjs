
const { createRequire } = require('module');
const PW_CORE = 'C:/Users/LIN/.dsh/profiles/web/node_modules/playwright-core';
const { chromium } = require(PW_CORE);
const fs = require('fs');

(async () => {
  const outDir = 'H:/ai_music_crew/shots';
  fs.mkdirSync(outDir, { recursive: true });
  const ctx = await chromium.launchPersistentContext('H:/pw-haimian', {
    channel: 'msedge',
    headless: true,
    viewport: { width: 1440, height: 900 },
    locale: 'zh-CN',
    args: ['--disable-blink-features=AutomationControlled'],
  });
  const page = ctx.pages()[0] || await ctx.newPage();
  await page.goto('https://www.haimian.com/', { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForTimeout(3500);
  console.log('URL:', page.url());
  console.log('TITLE:', await page.title());
  const txt = await page.evaluate(() => document.body ? document.body.innerText.slice(0, 1200) : '');
  console.log('TEXT:\n' + txt);
  await page.screenshot({ path: outDir + '/haimian-01-home.png', fullPage: false });
  // 列出可点击元素
  const els = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('a,button,[role=button]').forEach((e, i) => {
      const t = (e.innerText || e.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ');
      if (t && t.length < 30) out.push({ i, tag: e.tagName, text: t, href: e.getAttribute('href') || '' });
    });
    return out.slice(0, 80);
  });
  console.log('CLICKABLE:', JSON.stringify(els, null, 1).slice(0, 3000));
  await ctx.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
