// Stacked composition approved under D-43. Reuse pixels; never regenerate lettering.
const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const sharp = require('sharp');

async function main() {
  const source = path.resolve(__dirname, '../../source/logo-primary-transparent-v2-2048.png');
  const bytes = await fs.readFile(source);
  const sourceHash = crypto.createHash('sha256').update(bytes).digest('hex');
  assert.equal(sourceHash, '0328080f1f7ecc01a93108cc686fad88490f404c0d989671271bd7b16a96717c');
  const symbolCrop = await sharp(bytes).extract({left:0, top:0, width:500, height:640}).toBuffer();
  const symbol = await sharp(symbolCrop)
    .trim({threshold:0}).toBuffer({resolveWithObject:true});
  const textCrop = await sharp(bytes).extract({left:620, top:0, width:1428, height:640}).toBuffer();
  const text = await sharp(textCrop)
    .trim({threshold:0}).toBuffer({resolveWithObject:true});
  const raw = await sharp(bytes).ensureAlpha().raw().toBuffer({resolveWithObject:true});
  const bands = [[130,233], [270,350], [390,427]];
  // Confirm that these three bands contain all lettering before extracting.
  for (let y=0; y<raw.info.height; y++) {
    for (let x=500; x<raw.info.width; x++) {
      if (raw.data[(y*raw.info.width+x)*4+3] !== 0) {
        assert.ok(x >= 620 && bands.some(([a,b]) => y >= a && y <= b), 'Unexpected ink outside lettering bands');
      }
    }
  }
  const lines = [];
  for (const [top,bottom] of bands) {
    const lineCrop = await sharp(bytes).extract({left:620, top, width:1428, height:bottom-top+1}).toBuffer();
    const line = await sharp(lineCrop)
      .trim({threshold:0}).toBuffer({resolveWithObject:true});
    lines.push({input:line.data, left:Math.round((text.info.width-line.info.width)/2), top:top-bands[0][0]});
  }
  // Preserve the original vertical spacing and the relative sizes of all lines.
  const centredText = await sharp({create:{width:text.info.width,height:text.info.height,channels:4,
    background:{r:0,g:0,b:0,alpha:0}}}).composite(lines).png().toBuffer();
  const canvasSize = 1600;
  const wordmark = await sharp(centredText).resize({width:1360}).png().toBuffer({resolveWithObject:true});
  const mark = await sharp(symbol.data).resize({height:Math.round(wordmark.info.height/0.75)})
    .png().toBuffer({resolveWithObject:true});
  const gap = Math.round(mark.info.height*39/469);
  const groupHeight = mark.info.height+gap+wordmark.info.height;
  const top = Math.round((canvasSize-groupHeight)/2);
  assert.ok(top > 0);
  const layers = [
    {input:mark.data,left:Math.round((canvasSize-mark.info.width)/2),top},
    {input:wordmark.data,left:Math.round((canvasSize-wordmark.info.width)/2),top:top+mark.info.height+gap},
  ];
  const transparent = await sharp({create:{width:canvasSize,height:canvasSize,channels:4,
    background:{r:0,g:0,b:0,alpha:0}}}).composite(layers).png().toBuffer();
  const pale = await sharp(transparent).flatten({background:'#F9F4F2'}).png().toBuffer();
  for (const [name,data] of [['stacked-transparent-1600.png',transparent],['stacked-pale-1600.png',pale]]) {
    await fs.writeFile(path.join(__dirname,name),data);
  }
  const metadata = {
    status:'approved', reviewed_by:'Project sponsor', reviewed_on:'2026-09-07', decision:'D-43',
    source:path.relative(__dirname,source), source_sha256:sourceHash,
    canvas:[canvasSize,canvasSize], symbol:[mark.info.width,mark.info.height],
    wordmark:[wordmark.info.width,wordmark.info.height], gap,
    wordmark_height_ratio:0.75, alignment:'symbol and each existing text line centred',
    restrictions:'PNG only. No redraw, retyping or recolouring. Supplementary variant; horizontal logo and website unchanged.',
  };
  await fs.writeFile(path.join(__dirname,'proposal.json'),JSON.stringify(metadata,null,2)+'\n');
  console.log(JSON.stringify(metadata));
}
main().catch(error => {console.error(error);process.exitCode=1;});
