const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const file = require('node:path').join(__dirname, '../../site/assets/js/feedback-carousel.js');
test('carousel controller exists', () => assert.ok(fs.existsSync(file)));
if (fs.existsSync(file)) {
  test('feed request retains same-origin authentication without caching quotes', () => {
    const vm = require('node:vm');
    let request;
    vm.runInNewContext(fs.readFileSync(file, 'utf8'), {
      document: { querySelector: () => ({}) },
      fetch: (url, options) => {
        request = { url, options };
        return Promise.resolve({ ok: true, json: () => ({ quotes: [] }) });
      }
    });
    assert.equal(request.url, '/feedback/feed.php');
    assert.equal(request.options.credentials, 'same-origin');
    assert.equal(request.options.cache, 'no-store');
  });
  const { FeedbackCarousel } = require(file);
  test('native browser timers are not invoked with the controller as receiver', () => {
    const vm = require('node:vm');
    const sandbox = { module: { exports: {} }, setTimeout: function () {
      assert.ok(!(this instanceof sandbox.module.exports.FeedbackCarousel)); return 1;
    }, clearTimeout: function () {
      assert.ok(!(this instanceof sandbox.module.exports.FeedbackCarousel));
    } };
    vm.runInNewContext(fs.readFileSync(file, 'utf8'), sandbox);
    const c = new sandbox.module.exports.FeedbackCarousel(3);
    c.pause();
  });
  function fixture(count = 3, reduced = false) {
    let next = null, delay = null;
    const states = [];
    const carousel = new FeedbackCarousel(count, {
      reduced, render: s => states.push(s),
      schedule: (f, ms) => { next = f; delay = ms; return 1; },
      cancel: () => { next = null; }
    });
    return { carousel, states, tick: () => { const f = next; next = null; if (f) f(); }, scheduled: () => next !== null, delay: () => delay };
  }
  test('advances after eight seconds and wraps', () => {
    const f = fixture(); assert.equal(f.delay(), 8000);
    f.tick(); assert.equal(f.carousel.index, 1);
    f.tick(); f.tick(); assert.equal(f.carousel.index, 0);
  });
  test('manual navigation stops until Play even after hover or focus leave', () => {
    const f = fixture();
    f.carousel.move(-1); assert.equal(f.carousel.index, 2); assert.equal(f.scheduled(), false);
    f.carousel.block('hover', true); f.carousel.block('hover', false);
    f.carousel.block('focus', true); f.carousel.block('focus', false);
    assert.equal(f.scheduled(), false);
    f.carousel.play(); assert.equal(f.scheduled(), true);
    f.carousel.pause(); assert.equal(f.scheduled(), false);
  });
  test('all temporary blockers must clear before autoplay resumes', () => {
    const f=fixture();
    f.carousel.block('hover',true); f.carousel.block('focus',true);
    f.carousel.block('hover',false); assert.equal(f.scheduled(),false);
    f.carousel.block('focus',false); assert.equal(f.scheduled(),true);
    f.carousel.block('hidden',true); assert.equal(f.scheduled(),false);
    f.carousel.block('hidden',false); assert.equal(f.scheduled(),true);
  });
  test('reduced motion disables autoplay even when Play requested', () => {
    const f=fixture(3,true); assert.equal(f.scheduled(),false);
    f.carousel.play(); assert.equal(f.scheduled(),false);
    f.carousel.block('reduced',false); assert.equal(f.scheduled(),true);
    f.carousel.move(1); f.carousel.block('reduced',true); f.carousel.block('reduced',false);
    assert.equal(f.scheduled(),false);
  });
  test('zero and one quote never rotate', () => {
    for(const count of [0,1]) { const f=fixture(count); f.carousel.play(); f.carousel.move(1); assert.equal(f.scheduled(),false); assert.equal(f.carousel.index,0); }
  });
}
