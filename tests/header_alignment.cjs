// Run against a local PHP preview: NODE_PATH=<modules> node tests/header_alignment.cjs <URL>
// Requires Playwright and Chrome. Catches an oversized logo link leaving its image left-aligned.
const assert = require('node:assert/strict');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    const page = await browser.newPage();
    await page.route('https://widget.trustpilot.com/**', route => route.abort());
    const base = process.argv[2] || 'http://127.0.0.1:58632';
    for (const width of [320, 390, 499, 768, 769, 1440]) {
      await page.setViewportSize({ width, height: 1000 });
      for (const path of ['/', '/about/', '/how-i-can-help/', '/appointments-and-fees/', '/contact/', '/privacy/', '/accessibility/', '/404.html']) {
        await page.goto(base + path);
        await page.evaluate(() => document.fonts.ready);
        const logo = await page.locator('.brand-home img').boundingBox();
        const strap = await page.locator('.brand-strap').boundingBox();
        const identity = await page.locator('.site-identity').boundingBox();
        const label = `${width}px ${path}`;
        if (width <= 768) {
          assert.ok(Math.abs(logo.x + logo.width / 2 - width / 2) < 1, `${label}: logo must be horizontally centred`);
          assert.ok(Math.abs(logo.x + logo.width / 2 - strap.x - strap.width / 2) < 1, `${label}: logo and strapline centres must match`);
          assert.ok(logo.y + logo.height <= strap.y, `${label}: logo must be above strapline`);
          assert.ok(Math.abs(logo.width - Math.min(315, width - 40)) < 1, `${label}: preserve logo size`);
        } else {
          assert.ok(Math.abs(logo.x - identity.x) < 1, `${label}: desktop logo stays left-aligned`);
          assert.ok(logo.x + logo.width <= strap.x, `${label}: desktop identity remains side-by-side`);
        }
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, `${label}: no horizontal overflow`);
      }
    }
    await page.setViewportSize({ width: 499, height: 1000 });
    await page.goto(base + '/');
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: '/private/tmp/stronger-home-centred-mobile.png' });
    console.log('PASS: header alignment on eight pages at six widths; desktop preserved.');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
