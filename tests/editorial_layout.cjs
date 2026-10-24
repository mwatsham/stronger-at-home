// Local-only visual regression: NODE_PATH=<modules> node tests/editorial_layout.cjs <URL> [case]
// No form submissions or third-party widget requests are permitted by this check.
const assert = require('node:assert/strict');
const { chromium } = require('playwright');

const base = process.argv[2] || 'http://127.0.0.1:58632';
const only = process.argv[3];
const paths = ['/', '/about/', '/how-i-can-help/', '/appointments-and-fees/', '/contact/', '/privacy/', '/accessibility/', '/404.html'];

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const failures = [];
  let posts = 0;
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  await context.route('**/*', async route => {
    const request = route.request();
    if (request.method() !== 'GET') { posts++; return route.abort(); }
    if (!request.url().startsWith(base)) return route.abort();
    return route.continue();
  });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const visit = async path => {
    await page.goto(base + path);
    await page.evaluate(() => document.fonts.ready);
  };
  const check = async (name, run) => {
    if (only && name !== only) return;
    try { await run(); console.log(`PASS: ${name}`); }
    catch (error) { failures.push(`${name}: ${error.message}`); console.error(`FAIL: ${name}: ${error.message}`); }
  };
  try {
    await check('hero-first-viewport', async () => {
      await page.setViewportSize({ width: 1280, height: 720 });
      await visit('/');
      for (const selector of ['.hero .button', '.hero .trust-point']) {
        const box = await page.locator(selector).boundingBox();
        assert.ok(box.y >= 0 && box.y + box.height <= 720, `${selector} must fit in the first 720px viewport (bottom ${box.y + box.height})`);
      }
    });
    await check('appointment-context', async () => {
      await visit('/contact/#appointment-request');
      const target = page.locator('#appointment-request');
      assert.equal(await target.evaluate(element => element.tagName), 'SECTION');
      assert.equal(await target.locator('h2').innerText(), 'Request an appointment');
      assert.equal(await target.locator('form[action="/api/enquiry.php"]').count(), 1);
      const heading = await target.locator('h2').boundingBox();
      assert.ok(heading.y >= 0 && heading.y + heading.height < 720, 'Anchor arrival must show the enquiry heading');
      const form = await target.locator('form').boundingBox();
      assert.ok(Math.abs(form.x + form.width / 2 - 640) <= 1, 'Form must be centred in the viewport');
    });
    await check('editorial-rhythm', async () => {
      await page.setViewportSize({ width: 1280, height: 720 });
      await visit('/');
      const action = await page.locator('.hero .action-group').boundingBox();
      const reassurance = await page.locator('.hero .trust-point').boundingBox();
      assert.ok(reassurance.y - action.y - action.height >= 16, 'Reassurance has readable separation from appointment actions');
      await visit('/contact/');
      const form = await page.locator('form.appointment-form').boundingBox();
      for (const selector of ['.contact-intro h1', '.contact-methods', '.contact-form-section .section-heading']) {
        const box = await page.locator(selector).boundingBox();
        assert.ok(Math.abs(box.x - form.x) <= 1, `${selector} shares the form editorial axis`);
      }
      const methods = await page.locator('.contact-methods').boundingBox();
      const section = await page.locator('.contact-form-section').boundingBox();
      assert.ok(section.y - methods.y - methods.height >= 32, 'Contact methods retain breathing room before enquiry section');
      await visit('/about/');
      const sizes = await page.evaluate(() => ['h1', 'h2'].map(selector => parseFloat(getComputedStyle(document.querySelector(selector)).fontSize)));
      assert.ok(sizes[0] > sizes[1], 'Inner-page title remains larger than section headings');
    });
    await check('form-enhancement', async () => {
      await visit('/contact/');
      errors.length = 0;
      const submitted = await page.locator('form.appointment-form').evaluate(form => form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })));
      assert.equal(submitted, false, 'Blank enquiry must be stopped by existing client validation');
      assert.match(await page.locator('[data-form-status]').innerText(), /Please check the highlighted fields/);
      assert.deepEqual(errors, [], 'Form enhancement must still target the actual form');
    });
    await check('responsive-reflow', async () => {
      for (const width of [320, 375, 768, 1024, 1280]) {
        await page.setViewportSize({ width, height: 900 });
        for (const path of paths) {
          await visit(path);
          assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, `${width}px ${path}: no horizontal overflow`);
        }
      }
      // A 640 CSS-pixel viewport models 1280px at 200% browser zoom without shrinking text.
      await page.setViewportSize({ width: 640, height: 360 });
      for (const path of ['/', '/contact/']) {
        await visit(path);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, `200% effective reflow ${path}`);
        assert.ok(await page.locator('body').evaluate(element => parseFloat(getComputedStyle(element).fontSize) >= 16), 'Readable body text preserved');
      }
    });
    await check('keyboard-and-mobile', async () => {
      await page.setViewportSize({ width: 375, height: 900 });
      await visit('/');
      assert.ok((await page.locator('.skip-link').boundingBox()).y < 0, 'Skip link stays offscreen until focused');
      await page.keyboard.press('Tab');
      assert.equal(await page.locator('.skip-link').evaluate(element => element === document.activeElement), true);
      assert.notEqual(await page.locator('.skip-link').evaluate(element => getComputedStyle(element).outlineStyle), 'none');
      const menu = page.locator('.menu-button');
      await menu.focus();
      await page.keyboard.press('Enter');
      assert.equal(await menu.getAttribute('aria-expanded'), 'true');
      assert.equal(await page.locator('#primary-navigation .button').isVisible(), true);
      for (const selector of ['.menu-button', '.hero .button']) {
        assert.ok((await page.locator(selector).boundingBox()).height >= 44, `${selector}: 44px touch target`);
      }
      await page.keyboard.press('Enter');
      assert.equal(await menu.getAttribute('aria-expanded'), 'false');
      const action = await page.locator('.hero .button').boundingBox();
      const copy = await page.locator('.hero-copy').boundingBox();
      assert.ok(Math.abs(action.width - copy.width) < 1, 'Narrow-screen primary hero action uses available width');
      await page.locator('.hero .button').hover();
      assert.equal(await page.locator('.hero .button').evaluate(element => getComputedStyle(element).textDecorationLine), 'none', 'Appointment button hover stays un-underlined');
      await page.locator('.hero .button').focus();
      assert.notEqual(await page.locator('.hero .button').evaluate(element => getComputedStyle(element).outlineStyle), 'none', 'Appointment action retains visible keyboard focus');
    });
    await check('no-js-navigation', async () => {
      const noJs = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 375, height: 900 } });
      await noJs.route('**/*', route => route.request().url().startsWith(base) ? route.continue() : route.abort());
      const fallback = await noJs.newPage();
      for (const path of ['/', '/contact/']) {
        await fallback.goto(base + path);
        assert.equal(await fallback.locator('#primary-navigation a').count(), 6);
        for (const link of await fallback.locator('#primary-navigation a').all()) assert.equal(await link.isVisible(), true);
        assert.equal(await fallback.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      }
      await noJs.close();
    });
    await check('privacy-text-flow', async () => {
      await page.setViewportSize({ width: 375, height: 900 });
      await visit('/contact/');
      const label = page.locator('.form-field-checkbox label');
      const sentence = label.locator(':scope > span');
      assert.equal(await sentence.locator('a[href="/privacy/"]').count(), 1, 'Privacy sentence and link wrap as one text flow beside the checkbox');
      assert.match(await sentence.innerText(), /^I have read the privacy notice\. \(required\)$/);
      assert.equal(await label.locator('input[required]').count(), 1);
    });
    if (!only) {
      for (const [name, width, height, path] of [
        ['home-desktop', 1280, 720, '/'], ['home-mobile', 375, 900, '/'],
        ['contact-desktop', 1280, 900, '/contact/#appointment-request'], ['contact-mobile', 375, 900, '/contact/#appointment-request'],
        ['about-desktop', 1280, 900, '/about/'],
      ]) {
        await page.setViewportSize({ width, height });
        await visit(path);
        await page.evaluate(() => { if (document.activeElement instanceof HTMLElement) document.activeElement.blur(); });
        if (path.includes('#')) await page.screenshot({ path: `/private/tmp/warm-editorial-${name}-anchor.png` });
        // Full-page capture after a fragment scroll misplaces translated fixed elements in Chrome.
        await page.evaluate(() => scrollTo(0, 0));
        await page.screenshot({ path: `/private/tmp/warm-editorial-${name}.png`, fullPage: true });
      }
    }
    assert.equal(posts, 0, 'No form submission was attempted');
    if (failures.length) throw new Error(`${failures.length} editorial regression check(s) failed`);
  } finally { await browser.close(); }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
