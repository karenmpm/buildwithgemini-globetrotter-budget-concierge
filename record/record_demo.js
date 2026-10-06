const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const FRAMES_DIR = path.join(__dirname, 'frames');
const VIDEO_URL = 'https://globetrotter-budget-frontend-797881982742.us-central1.run.app';

if (fs.existsSync(FRAMES_DIR)) {
  fs.rmSync(FRAMES_DIR, { recursive: true, force: true });
}
fs.mkdirSync(FRAMES_DIR, { recursive: true });

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

(async () => {
  console.log('🚀 Launching Chrome to record complete demo video...');
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/google-chrome',
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--window-size=1280,820',
    ]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  let frameCount = 0;
  const client = await page.target().createCDPSession();

  client.on('Page.screencastFrame', async (event) => {
    const frameNumber = String(frameCount++).padStart(5, '0');
    const filePath = path.join(FRAMES_DIR, `frame_${frameNumber}.jpg`);
    fs.writeFileSync(filePath, Buffer.from(event.data, 'base64'));
    await client.send('Page.screencastFrameAck', { sessionId: event.sessionId });
  });

  await client.send('Page.startScreencast', {
    format: 'jpeg',
    quality: 90,
    everyNthFrame: 1
  });

  console.log('🌐 Loading Pineapple Trips Planner app...');
  await page.goto(VIDEO_URL, { waitUntil: 'networkidle2' });
  await delay(2000);

  // --- Interaction 1: Core Travel Planning Feature ---
  console.log('💬 Interaction 1: Requesting budget trip suggestions in Thailand...');
  await page.type('#input', 'Budget trips under $50/day in Thailand', { delay: 40 });
  await delay(500);
  await page.click('button.send-btn');

  console.log('⏳ Waiting 12s for Interaction 1 response...');
  await delay(12000);

  // Smooth scroll log to show Interaction 1 cards
  await page.evaluate(() => {
    const log = document.getElementById('log');
    if (log) log.scrollTop = log.scrollHeight;
  });
  await delay(3000);

  // --- Interaction 2: Currency Conversion & Travel Postcard Generation ---
  console.log('💬 Interaction 2: Requesting currency conversion & Chiang Mai postcard...');
  
  // Clear input explicitly
  await page.evaluate(() => {
    const inp = document.getElementById('input');
    if (inp) inp.value = '';
  });
  await delay(500);

  const prompt2 = 'Convert 200 USD to THB and generate a travel postcard for Chiang Mai night markets';
  await page.type('#input', prompt2, { delay: 40 });
  await delay(800);
  await page.click('button.send-btn');

  console.log('⏳ Waiting 20s for Interaction 2 tool calls and postcard generation...');
  await delay(20000);

  // Scroll down smoothly to show currency conversion card + generated postcard
  await page.evaluate(() => {
    const log = document.getElementById('log');
    if (log) log.scrollTop = log.scrollHeight;
  });
  await delay(4000);

  // --- Lightbox Modal Interaction ---
  console.log('🖼️ Opening Lightbox preview for generated postcard image...');
  await page.evaluate(() => {
    const imgs = document.querySelectorAll('.a2img, img');
    if (imgs.length > 0) {
      const lastImg = imgs[imgs.length - 1];
      lastImg.click();
    }
  });
  await delay(7000); // Hold Lightbox modal open for 7 seconds

  // Close Lightbox modal
  console.log('✖️ Closing Lightbox preview modal...');
  await page.evaluate(() => {
    const modal = document.getElementById('lightbox-modal');
    if (modal) modal.style.display = 'none';
  });
  await delay(3000);

  console.log('🛑 Stopping screencast recording...');
  await client.send('Page.stopScreencast');
  await browser.close();

  console.log(`📸 Captured ${frameCount} frames.`);

  // --- Stitch frames + lo-fi music with FFmpeg ---
  console.log('🎬 Stitching frames and lo-fi audio into demo_video.mp4...');
  const outputVideo = path.join(__dirname, '..', 'demo_video.mp4');
  const audioFile = path.join(__dirname, 'lofi_track.wav');

  const ffmpegCmd = `ffmpeg -y -framerate 10 -i "${FRAMES_DIR}/frame_%05d.jpg" -i "${audioFile}" -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest "${outputVideo}"`;
  execSync(ffmpegCmd);

  console.log('✅ Demo video created successfully at:', outputVideo);
})();
