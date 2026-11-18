/* Optional maintainer-only cross-engine smoke; install Playwright locally to run.
   No Playwright or browser code is included in consumer distributions. */
const assert = require('node:assert/strict');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium, firefox, webkit } = require('playwright');

const pageUrl = pathToFileURL(path.join(__dirname, '..', 'examples', 'chat-interface.html')).href;

(async () => {
  const engines = { chromium, firefox, webkit };
  const selected = (process.env.SYNTYR_BROWSERS || 'chromium,firefox,webkit').split(',');
  for (const name of selected) {
    const engine = engines[name];
    if (!engine) throw new Error('Unknown browser: ' + name);
    const executablePath = process.env['SYNTYR_' + name.toUpperCase() + '_EXECUTABLE'];
    const browser = await engine.launch({ headless: true, ...(executablePath ? { executablePath } : {}) });
    try {
      const page = await browser.newPage({ viewport: { width: 390, height: 800 } });
      const errors = [];
      page.on('pageerror', error => errors.push(String(error)));
      await page.goto(pageUrl);
      const message = page.locator('.syn-message--outgoing');
      const computed = async () => page.evaluate(() => {
        const panel = document.querySelector('.syn-panel[data-syn-contrast="more"]');
        const nested = document.querySelector('[data-syn-contrast="normal"].syn-surface--recessed');
        const composer = document.querySelector('.syn-composer');
        const message = document.querySelector('.syn-message--outgoing');
        return {
          panelBorder: getComputedStyle(panel).borderTopColor,
          nestedBorder: getComputedStyle(nested).borderTopColor,
          panelRadius: getComputedStyle(panel).borderTopLeftRadius,
          composerDisplay: getComputedStyle(composer).display,
          messageBackground: getComputedStyle(message).backgroundColor,
        };
      });
      const normal = await computed();
      assert.equal(normal.composerDisplay, 'grid');
      assert.notEqual(normal.panelBorder, normal.nestedBorder, name + ' contrast reset');
      assert.notEqual(normal.messageBackground, 'rgba(0, 0, 0, 0)');
      assert.equal(normal.panelRadius, '6px', name + ' Minimal radius');
      await page.emulateMedia({ contrast: 'more' });
      await page.reload();
      const high = await computed();
      assert.equal(high.panelBorder, high.nestedBorder, name + ' OS contrast must win');
      await page.emulateMedia({ contrast: 'no-preference' });
      for (const width of [320, 390, 1280]) {
        await page.setViewportSize({ width, height: 800 });
        const overflow = await page.evaluate(
          () => document.documentElement.scrollWidth - document.documentElement.clientWidth);
        assert.ok(overflow <= 1, name + ' horizontal overflow at ' + width + ': ' + overflow);
      }
      await page.evaluate(() => { document.documentElement.style.fontSize = '32px'; });
      await page.setViewportSize({ width: 390, height: 800 });
      const enlargedOverflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      assert.ok(enlargedOverflow <= 1, name + ' horizontal overflow with 200% root text');
      await page.evaluate(() => { document.documentElement.style.fontSize = ''; });
      await page.evaluate(() => { document.body.dataset.synTheme = 'grid'; });
      const grid = await computed();
      assert.equal(grid.panelRadius, '0px', name + ' Grid palette isolation');
      await page.locator('#message-prompt').focus();
      assert.equal(await page.locator('#message-prompt').evaluate(
        e => getComputedStyle(e).outlineStyle !== 'none'), true, name + ' textarea focus');
      assert.equal(await page.locator('button[type=submit]').isDisabled(), true);
      assert.deepEqual(errors, []);
      console.log('PASS ' + name + ' | contrast override / OS preference / nested themes / 320–1280 reflow / composer');
      await page.close();
    } finally {
      await browser.close();
    }
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
