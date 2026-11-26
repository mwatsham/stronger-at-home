'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const crypto = require('node:crypto');
const file = path.join(__dirname, '../../site/assets/js/analytics.js');
const exists = fs.existsSync(file);
const api = exists ? require(file) : {};
const provider = fs.readFileSync(path.join(__dirname, 'fixtures/goatcounter-count.js'), 'utf8');
function browser(url = 'https://stronger-at-home.co.uk/contact/', kind = '') {
  const scripts = [], requests = [];
  const location = new URL(url);
  const document = {
    referrer: 'https://www.google.com/search?q=private', title: 'Private patient name',
    visibilityState: 'visible', body: {},
    querySelector(selector) {
      if (selector === '[data-form-status]') return {dataset: {flashKind: kind}};
      return null;
    },
    createElement(tag) { assert.equal(tag, 'script'); return {}; },
    head: {appendChild(script) { scripts.push(script); }}
  };
  const storage = new Map();
  const window = {location, document, screen: {width: 1200}, navigator: {}, localStorage: {
    getItem(key) {return storage.get(key) || null;}, setItem(key,value) {storage.set(key,value);}
  }};
  window.self = window.top = window;
  const context = vm.createContext({window, document, location, parent: {location},
    navigator: {sendBeacon(url) {requests.push(url); return true;}},
    localStorage: {getItem() {return null;}}, console, URL, URLSearchParams});
  Object.defineProperty(context, 'goatcounter', {get() {return window.goatcounter;}});
  return {window, document, scripts, requests, context,
    load() {vm.runInContext(provider, context); scripts[0].onload();}};
}
test('analytics adapter is implemented', () => assert.equal(exists, true));
test('approved browser entry loads provider only on production', () => {
  const b = browser(); vm.runInContext(fs.readFileSync(file, 'utf8'), b.context);
  assert.equal(b.scripts.length, 1); b.load(); assert.equal(b.requests.length, 1);
});
test('saved opt-out, browser privacy signals and unavailable storage prevent collection', () => {
  for (const mode of ['saved','dnt','gpc','blocked']) {
    const b = browser();
    if (mode === 'saved') b.window.localStorage.setItem('sah-analytics-opt-out','1');
    if (mode === 'dnt') b.window.navigator.doNotTrack = '1';
    if (mode === 'gpc') b.window.navigator.globalPrivacyControl = true;
    if (mode === 'blocked') b.window.localStorage.getItem = () => {throw Error('blocked');};
    api.startAnalytics(b.window,b.document,true);
    assert.equal(b.scripts.length,0,mode);
  }
});
test('opting out while provider loads prevents pending counts', () => {
  const b = browser(); api.startAnalytics(b.window,b.document,true);
  b.window.localStorage.setItem('sah-analytics-opt-out','1'); b.load();
  assert.equal(b.requests.length,0);
});
test('privacy controls save a choice and report storage failures without enabling tracking', () => {
  const b = browser(), handlers = {};
  const off = {addEventListener(type, fn) {handlers.off = fn;}}, on = {addEventListener(type, fn) {handlers.on = fn;}};
  const status = {textContent:''};
  b.document.querySelector = s => ({'[data-analytics-off]':off,'[data-analytics-on]':on,'[data-analytics-status]':status}[s] || null);
  api.setupPrivacyControls(b.window,b.document);
  handlers.off();
  assert.equal(b.window.localStorage.getItem('sah-analytics-opt-out'),'1');
  assert.match(status.textContent,/off/i);
  handlers.on();
  assert.equal(b.window.localStorage.getItem('sah-analytics-opt-out'),'0');
  assert.match(status.textContent,/next page/i);
  b.window.localStorage.setItem = () => {throw Error('blocked');};
  handlers.off(); assert.match(status.textContent,/could not save/i);
  api.startAnalytics(b.window,b.document,true); assert.equal(b.scripts.length,0);
});
test('disabled, local, staging, lookalike, HTTP, private and framed pages never load provider', () => {
  for (const url of ['http://stronger-at-home.co.uk/', 'http://localhost:58642/',
    'https://staging.stronger-at-home.co.uk/', 'https://stronger-at-home.co.uk.evil.test/',
    'https://stronger-at-home.co.uk/feedback/admin/', 'https://stronger-at-home.co.uk/api/enquiry.php',
    'https://stronger-at-home.co.uk/design-preview/', 'https://stronger-at-home.co.uk/unknown']) {
    const b = browser(url); api.startAnalytics(b.window,b.document,true); assert.equal(b.scripts.length,0,url);
  }
  const off = browser(); api.startAnalytics(off.window,off.document,false); assert.equal(off.scripts.length,0);
  const frame = browser(); frame.window.top = {}; api.startAnalytics(frame.window,frame.document,true); assert.equal(frame.scripts.length,0);
});
test('all seven public routes have safe static pageview data', () => {
  for (const route of ['/', '/about/', '/how-i-can-help/', '/appointments-and-fees/', '/contact/', '/privacy/', '/accessibility/']) {
    const data = api.buildPageview(new URL('https://stronger-at-home.co.uk'+route+'?name=PRIVATE#PRIVATE'),'');
    assert.equal(data.path,route); assert.equal(data.event,false); assert.equal(data.referrer,'');
    assert.ok(data.title); assert.ok(!JSON.stringify(data).includes('PRIVATE'));
  }
});
test('special provider opt-out fragment cannot load code that changes browser storage or opens alerts', () => {
  const b = browser('https://stronger-at-home.co.uk/contact/#toggle-goatcounter');
  api.startAnalytics(b.window,b.document,true);
  assert.equal(b.scripts.length,0); assert.equal(b.requests.length,0);
});
test('modern hidden prerenders cannot load or count before a real navigation', () => {
  const b = browser(); b.document.prerendering = true; b.document.visibilityState = 'hidden';
  api.startAnalytics(b.window,b.document,true);
  assert.equal(b.scripts.length,0); assert.equal(b.requests.length,0);
});
test('referrers are hostname only and reject same-site or non-HTTP sources', () => {
  const loc = new URL('https://stronger-at-home.co.uk/');
  for (const ref of ['', 'javascript:PRIVATE', 'not a url', 'https://stronger-at-home.co.uk/about/', 'https://www.stronger-at-home.co.uk/'])
    assert.equal(api.buildPageview(loc,ref).referrer,'');
  assert.equal(api.buildPageview(loc,'https://www.google.com/search?q=PRIVATE').referrer,'https://www.google.com');
});
test('only approved campaign tags map to fixed source labels, including leaflet QR', () => {
  for (const [query,label] of [
    ['utm_source=leaflet&utm_medium=qr&utm_campaign=local-leaflet','Leaflet QR'],
    ['utm_source=google&utm_campaign=business-profile','Google Business Profile'],
    ['utm_source=facebook&utm_campaign=business-page','Facebook business page'],
    ['utm_source=email&utm_campaign=newsletter','Email newsletter'],
    ['utm_source=leaflet&utm_campaign=local-leaflet',''],
    ['utm_source=PRIVATE&utm_campaign=PRIVATE',''],
    ['utm_source=leaflet&utm_source=PRIVATE&utm_medium=qr&utm_campaign=local-leaflet','']]) {
    assert.equal(api.buildPageview(new URL('https://stronger-at-home.co.uk/?'+query),'').referrer,label);
  }
});
test('actual provider emits only safe payload with no query, screen or private content', () => {
  const b = browser('https://stronger-at-home.co.uk/contact/?utm_source=leaflet&utm_medium=qr&utm_campaign=local-leaflet&email=PRIVATE#appointment-request');
  api.startAnalytics(b.window,b.document,true); b.load();
  assert.equal(b.requests.length,1);
  const url = new URL(b.requests[0]);
  assert.equal(url.origin,'https://stronger-at-home.goatcounter.com');
  assert.deepEqual([...url.searchParams.keys()].sort(),['p','r','rnd','t']);
  assert.equal(url.searchParams.get('r'),'Leaflet QR'); assert.equal(url.searchParams.get('p'),'/contact/');
  assert.ok(!b.requests[0].includes('PRIVATE'));
});
test('provider script is integrity pinned to the audited fixture and sends no referrer', () => {
  const b = browser(); api.startAnalytics(b.window,b.document,true);
  assert.equal(b.scripts[0].integrity, 'sha384-'+crypto.createHash('sha384').update(provider).digest('base64'));
  assert.equal(b.scripts[0].crossOrigin,'anonymous');
  assert.equal(b.scripts[0].referrerPolicy,'no-referrer');
});
test('rejected beacon fallback sends the same sanitised payload in a hidden image', () => {
  const b = browser('https://stronger-at-home.co.uk/contact/?email=PRIVATE#PRIVATE');
  api.startAnalytics(b.window,b.document,true);
  const images = [];
  b.context.navigator.sendBeacon = () => false;
  b.document.createElement = tag => {
    assert.equal(tag,'img');
    return {style:{},setAttribute(){},addEventListener(){}};
  };
  b.document.body.appendChild = img => images.push(img);
  b.load();
  assert.equal(images.length,1);
  const url = new URL(images[0].src);
  assert.equal(url.origin,'https://stronger-at-home.goatcounter.com');
  assert.deepEqual([...url.searchParams.keys()].sort(),['p','r','rnd','t']);
  assert.equal(url.searchParams.get('p'),'/contact/');
  assert.equal(url.searchParams.get('r'),'https://www.google.com');
  assert.ok(!images[0].src.includes('PRIVATE'));
});
test('only server success counts once even with repeated init and load callbacks', () => {
  const b = browser(undefined,'success');
  api.startAnalytics(b.window,b.document,true); api.startAnalytics(b.window,b.document,true);
  assert.equal(b.scripts.length,1); b.load(); b.scripts[0].onload();
  assert.equal(b.requests.length,2);
  const event = new URL(b.requests[1]);
  assert.equal(event.searchParams.get('p'),'enquiry-submitted');
  assert.equal(event.searchParams.get('t'),'Enquiry submitted'); assert.equal(event.searchParams.get('e'),'true');
  assert.equal(event.searchParams.get('r'),null);
});
test('sent query, errors, missing flash, other pages and reload do not produce conversion', () => {
  for (const kind of ['', 'validation', 'delivery', 'rate']) {
    const b = browser('https://stronger-at-home.co.uk/contact/?sent=1',kind);
    api.startAnalytics(b.window,b.document,true); b.load(); assert.equal(b.requests.length,1);
  }
  const b = browser('https://stronger-at-home.co.uk/about/','success');
  api.startAnalytics(b.window,b.document,true); b.load(); assert.equal(b.requests.length,1);
});
test('provider and script failures are contained and not retried', () => {
  const b = browser(); api.startAnalytics(b.window,b.document,true);
  assert.doesNotThrow(()=>b.scripts[0].onerror());
  assert.doesNotThrow(()=>b.scripts[0].onload());
  api.startAnalytics(b.window,b.document,true); assert.equal(b.scripts.length,1); assert.equal(b.requests.length,0);
  const c = browser(); api.startAnalytics(c.window,c.document,true);
  c.window.goatcounter.count = ()=>{throw Error('blocked');};
  assert.doesNotThrow(()=>c.scripts[0].onload());
});
