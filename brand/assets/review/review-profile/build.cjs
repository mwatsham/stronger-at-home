// Format approved pixels for profile uploads; adjust spacing without redrawing.
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const sharp = require('sharp');

async function main() {
  const source = path.resolve(__dirname, '../../source/logo-primary-transparent-v2-2048.png');
  const bytes = await fs.readFile(source);
  const expected = '0328080f1f7ecc01a93108cc686fad88490f404c0d989671271bd7b16a96717c';
  if (crypto.createHash('sha256').update(bytes).digest('hex') !== expected) {
    throw new Error('The approved source has changed. Refusing to use it.');
  }
  // Keep the requested 39-pixel gap (half the original gap, halved again).
  const raw = await sharp(bytes).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  for (let y = 0; y < raw.info.height; y++) {
    for (let x = 500; x < 620; x++) {
      if (raw.data[(y * raw.info.width + x) * 4 + 3] !== 0) {
        throw new Error('Spacing strip contains visible artwork; refusing to crop it.');
      }
    }
  }
  const left = await sharp(bytes).extract({ left: 0, top: 0, width: 500, height: 640 }).toBuffer();
  const right = await sharp(bytes).extract({ left: 620, top: 0, width: 1428, height: 640 }).toBuffer();
  const symbol = await sharp(left).trim({ threshold: 0 }).toBuffer({ resolveWithObject: true });
  const wordmark = await sharp(right).trim({ threshold: 0 }).toBuffer({ resolveWithObject: true });
  // Scale all three text lines together, including their internal spacing.
  // The complete wordmark is 75% of the symbol height and vertically centred.
  const textHeightRatio = 0.75;
  const symbolRatio = symbol.info.width / symbol.info.height;
  const wordmarkRatio = wordmark.info.width / wordmark.info.height;
  const gapRatio = 39 / symbol.info.height;
  for (const [name, width, height, artworkWidth] of [
    ['../../source/logo-primary-transparent-v3-2048', 2048, 640, 1740],
    ['stronger-at-home-review-profile-1024', 1024, 1024, 870],
    ['stronger-at-home-review-logo-wide-1200', 1200, 500, 1100],
  ]) {
    const blockHeight = Math.round(artworkWidth / (symbolRatio + wordmarkRatio * textHeightRatio + gapRatio));
    const scaledSymbol = await sharp(symbol.data).resize({ height: blockHeight })
      .toBuffer({ resolveWithObject: true });
    const scaledWordmark = await sharp(wordmark.data).resize({ height: Math.round(blockHeight * textHeightRatio) })
      .toBuffer({ resolveWithObject: true });
    const gap = Math.round(blockHeight * gapRatio);
    const groupWidth = scaledSymbol.info.width + gap + scaledWordmark.info.width;
    const leftEdge = Math.round((width - groupWidth) / 2);
    const top = Math.round((height - blockHeight) / 2);
    const master = name.includes('v3-2048');
    const canvas = sharp({ create: { width, height, channels: master ? 4 : 3,
      background: master ? { r: 0, g: 0, b: 0, alpha: 0 } : '#F9F4F2' } })
      .composite([
        { input: scaledSymbol.data, left: leftEdge, top },
        { input: scaledWordmark.data, left: leftEdge + scaledSymbol.info.width + gap,
          top: top + Math.round((blockHeight - scaledWordmark.info.height) / 2) },
      ]);
    await canvas.clone().png().toFile(path.join(__dirname, `${name}.png`));
    if (master) {
      const transparent = await canvas.clone().png().toBuffer();
      await sharp(transparent).flatten({ background: '#F9F4F2' }).png()
        .toFile(path.resolve(__dirname, '../../source/logo-primary-raster-v3-2048.png'));
      await sharp(transparent).resize({ width: 512 }).flatten({ background: '#F9F4F2' }).png()
        .toFile(path.resolve(__dirname, '../../source/logo-primary-raster-v3-512.png'));
    }
    if (width === 1024) await canvas.clone().jpeg({ quality: 95, chromaSubsampling: '4:4:4' })
      .toFile(path.join(__dirname, `${name}.jpg`));
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
