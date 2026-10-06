const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/google-chrome',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,820']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  console.log('Navigating to app...');
  await page.goto('https://globetrotter-budget-frontend-797881982742.us-central1.run.app', { waitUntil: 'networkidle2' });

  console.log('Sending Interaction 1...');
  await page.type('#input', 'Budget trips under $50/day in Thailand');
  await page.click('button.send-btn');

  await new Promise(r => setTimeout(r, 12000));
  await page.screenshot({ path: path.join(__dirname, 'step1_inter1.png') });
  console.log('Saved step1_inter1.png');

  console.log('Sending Interaction 2...');
  await page.type('#input', 'Convert 200 USD to THB and generate a travel postcard for Chiang Mai night markets');
  await page.click('button.send-btn');

  for (let s = 5; s <= 30; s += 5) {
    await new Promise(r => setTimeout(r, 5000));
    await page.evaluate(() => {
      const log = document.getElementById('log');
      if (log) log.scrollTop = log.scrollHeight;
    });
    await page.screenshot({ path: path.join(__dirname, `step2_sec${s}.png`) });
    console.log(`Saved step2_sec${s}.png`);
  }

  await browser.close();
  console.log('Done test_pup.js');
})();
