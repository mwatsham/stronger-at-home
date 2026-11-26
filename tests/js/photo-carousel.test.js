'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const file = path.resolve(__dirname, '../../site/assets/js/photo-carousel.js');
test('photo rotation implementation is available', () => assert.ok(fs.existsSync(file)));
const { PhotoCarousel } = fs.existsSync(file) ? require(file) : {};
const flush = () => new Promise(resolve => setImmediate(resolve));
function setup(count = 3, extra = {}) {
  const timers = new Map(); let id = 0; let state;
  const carousel = new PhotoCarousel(count, {
    schedule: (fn, ms) => { assert.equal(ms, 8000); timers.set(++id, fn); return id; },
    cancel: key => timers.delete(key), render: value => { state = value; }, ...extra
  });
  return { carousel, timers, state: () => state, tick: async () => {
    assert.equal(timers.size, 1); const [key, fn] = timers.entries().next().value;
    timers.delete(key); fn(); await flush();
  }};
}
test('advances every eight seconds and wraps', async () => {
  const h = setup();
  for (const index of [1, 2, 0]) { await h.tick(); assert.equal(h.state().index, index); }
});
test('manual navigation stops until explicitly played', async () => {
  const h = setup(); await h.carousel.move(-1);
  assert.equal(h.state().index, 2); assert.equal(h.timers.size, 0);
  h.carousel.block('hover', true); h.carousel.block('hover', false);
  assert.equal(h.timers.size, 0); h.carousel.play(); await h.tick();
  assert.equal(h.state().index, 0);
});
test('overlapping temporary blockers must all clear', () => {
  const h = setup();
  for (const reason of ['hover', 'focus', 'hidden', 'offscreen']) h.carousel.block(reason, true);
  for (const reason of ['hover', 'focus', 'hidden']) h.carousel.block(reason, false);
  assert.equal(h.timers.size, 0); h.carousel.block('offscreen', false);
  assert.equal(h.timers.size, 1);
});
test('reduced motion prevents playback and handles preference changes', () => {
  const h = setup(3, { reduced: true }); h.carousel.play();
  assert.equal(h.timers.size, 0); h.carousel.block('reduced', false);
  assert.equal(h.timers.size, 1); h.carousel.block('reduced', true);
  assert.equal(h.timers.size, 0);
});
test('zero and one image never rotate', async () => {
  for (const count of [0, 1]) { const h = setup(count); await h.carousel.move(1); h.carousel.play(); assert.equal(h.timers.size, 0); assert.equal(h.state().index, 0); }
});
test('slow image cannot undo a newer navigation', async () => {
  let resolveOld; let calls = 0;
  const h = setup(3, { prepare: () => ++calls === 1 ? new Promise(r => { resolveOld = r; }) : Promise.resolve() });
  const old = h.carousel.move(1); await h.carousel.move(-1);
  assert.equal(h.state().index, 2); resolveOld(); await old;
  assert.equal(h.state().index, 2); assert.equal(h.timers.size, 0);
});
test('pausing or hiding cancels an in-flight automatic transition', async () => {
  for (const block of [false, true]) {
    let resolve;
    const h = setup(3, { prepare: () => new Promise(r => { resolve = r; }) });
    await h.tick();
    if (block) h.carousel.block('hidden', true); else h.carousel.pause();
    resolve(); await flush(); assert.equal(h.state().index, 0); assert.equal(h.timers.size, 0);
  }
});
test('failed image keeps current photo and later navigation skips it', async () => {
  const h = setup(3, { prepare: i => i === 1 ? Promise.reject(new Error('broken')) : Promise.resolve() });
  await h.carousel.move(1); assert.equal(h.state().index, 0);
  await h.carousel.move(1); assert.equal(h.state().index, 2);
});

// The DOM boundary is represented only by events, image decoding and attributes;
// the real initializer/controller perform all state changes under test.
function browser(withControls = true) {
  function element() {
    const listeners = {}; const attributes = {}; const classes = new Set();
    return { hidden: true, attributes, classes,
      addEventListener: (type, fn) => { listeners[type] = fn; },
      emit: (type, event = {}) => listeners[type]?.(event),
      setAttribute: (key, value) => { attributes[key] = value; },
      classList: { add: name => classes.add(name), toggle: (name, yes) => yes ? classes.add(name) : classes.delete(name) }
    };
  }
  const images = Array.from({ length: 3 }, () => ({ ...element(), naturalWidth: 960, decode: async () => {} }));
  const controls = Object.fromEntries(['controls', 'toggle', 'count', 'previous', 'next'].map(name => [`[data-photo-${name}]`, element()]));
  const section = { ...element(), querySelectorAll: () => images, querySelector: name => withControls ? controls[name] : null, matches: () => false, contains: item => Object.values(controls).includes(item) };
  const doc = { ...element(), hidden: false, activeElement: null };
  const motion = { ...element(), matches: false }; let observer;
  const win = { matchMedia: () => motion, IntersectionObserver: class {
    constructor(callback) { observer = callback; } observe(target) { assert.equal(target, section); }
  }};
  const { initialisePhotoCarousel } = require(file);
  const carousel = initialisePhotoCarousel(section, doc, win);
  return { section, doc, motion, carousel, images, controls,
    visible: yes => observer([{ target: section, isIntersecting: yes }]) };
}
test('browser controls expose only the active alt text and stop on manual navigation', async () => {
  const h = browser();
  try {
    assert.equal(h.controls['[data-photo-controls]'].hidden, false);
    assert.deepEqual(h.images.map(i => i.attributes['aria-hidden']), ['false', 'true', 'true']);
    h.controls['[data-photo-next]'].emit('click'); await flush();
    assert.deepEqual(h.images.map(i => i.attributes['aria-hidden']), ['true', 'false', 'true']);
    assert.equal(h.controls['[data-photo-count]'].textContent, '2 of 3');
    assert.equal(h.controls['[data-photo-toggle]'].textContent, 'Play');
    assert.equal(h.section.attributes['aria-live'], undefined);
  } finally { h.carousel.pause(); }
});
test('browser maps visibility, focus, hover, viewport and motion preferences to pause', () => {
  const h = browser();
  try {
    assert.equal(h.carousel.timer, null); h.visible(true); assert.notEqual(h.carousel.timer, null);
    h.section.emit('mouseenter'); h.section.emit('focusin'); h.section.emit('mouseleave');
    assert.equal(h.carousel.timer, null);
    h.section.emit('focusout', { relatedTarget: h.controls['[data-photo-next]'] });
    assert.equal(h.carousel.timer, null);
    h.section.emit('focusout', { relatedTarget: null }); assert.notEqual(h.carousel.timer, null);
    h.doc.hidden = true; h.doc.emit('visibilitychange'); assert.equal(h.carousel.timer, null);
    h.doc.hidden = false; h.doc.emit('visibilitychange'); assert.notEqual(h.carousel.timer, null);
    h.motion.matches = true; h.motion.emit('change'); assert.equal(h.carousel.timer, null);
    assert.equal(h.controls['[data-photo-toggle]'].hidden, true);
    h.motion.matches = false; h.motion.emit('change'); assert.notEqual(h.carousel.timer, null);
    h.visible(false); assert.equal(h.carousel.timer, null);
  } finally { h.carousel.pause(); }
});
test('browser image decode failure leaves the working photo visible', async () => {
  const h = browser();
  try {
    h.images[1].decode = async () => { throw new Error('network'); };
    h.controls['[data-photo-next]'].emit('click'); await flush();
    assert.equal(h.images[0].attributes['aria-hidden'], 'false');
    assert.equal(h.controls['[data-photo-count]'].textContent, '1 of 3');
    h.controls['[data-photo-next]'].emit('click'); await flush();
    assert.equal(h.images[2].attributes['aria-hidden'], 'false');
  } finally { h.carousel.pause(); }
});
test('manual navigation immediately labels the control Play while decode is pending', async () => {
  const h = browser(); let resolve;
  try {
    h.images[1].decode = () => new Promise(r => { resolve = r; });
    h.controls['[data-photo-next]'].emit('click');
    assert.equal(h.controls['[data-photo-toggle]'].textContent, 'Play');
    assert.equal(h.controls['[data-photo-toggle]'].attributes['aria-label'], 'Play automatic photo rotation');
    resolve(); await flush();
    assert.equal(h.controls['[data-photo-count]'].textContent, '2 of 3');
  } finally { resolve?.(); h.carousel.pause(); }
});
test('temporary pause conditions do not discard a requested manual photo', async () => {
  let resolve; const h = setup(3, { prepare: () => new Promise(r => { resolve = r; }) });
  const pending = h.carousel.move(1); h.carousel.block('hover', true);
  resolve(); await pending;
  assert.equal(h.state().index, 1); assert.equal(h.timers.size, 0);
});
test('automatic-only photo frame works without controls and respects motion preferences', async () => {
  const h = browser(false);
  try {
    h.visible(true);
    assert.notEqual(h.carousel.timer, null);
    await h.carousel.advance(1);
    assert.equal(h.images[1].attributes['aria-hidden'], 'false');
    h.motion.matches = true; h.motion.emit('change');
    assert.equal(h.carousel.timer, null);
    h.motion.matches = false; h.motion.emit('change');
    assert.notEqual(h.carousel.timer, null);
    h.section.emit('mouseenter'); assert.equal(h.carousel.timer, null);
    h.section.emit('mouseleave'); assert.notEqual(h.carousel.timer, null);
  } finally { h.carousel.pause(); }
});
