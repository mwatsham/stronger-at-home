'use strict';

class PhotoCarousel {
  constructor(count, { reduced = false, render = () => {}, prepare = () => Promise.resolve(),
    schedule = (fn, ms) => setTimeout(fn, ms), cancel = id => clearTimeout(id) } = {}) {
    Object.assign(this, { count, render, prepare, schedule, cancel });
    this.index = 0;
    this.stopped = false;
    this.blocks = new Set(reduced ? ['reduced'] : []);
    this.failed = new Set();
    this.timer = null;
    this.request = 0;
    this.update();
  }
  update() {
    if (this.timer !== null) this.cancel(this.timer);
    this.timer = null;
    const running = this.count - this.failed.size > 1 && !this.stopped && !this.blocks.size;
    this.render({ index: this.index, stopped: this.stopped, running });
    if (running) this.timer = this.schedule(() => this.advance(1), 8000);
  }
  async advance(direction) {
    const request = ++this.request;
    if (this.timer !== null) this.cancel(this.timer);
    this.timer = null;
    let next = this.index;
    for (let n = 0; n < this.count; n++) {
      next = (next + direction + this.count) % this.count;
      if (!this.failed.has(next)) break;
    }
    if (next === this.index) { this.update(); return; }
    try {
      await this.prepare(next);
      if (request !== this.request) return;
      this.index = next;
    } catch (_) {
      if (request !== this.request) return;
      this.failed.add(next);
    }
    this.update();
  }
  move(direction) {
    this.stopped = true;
    this.update();
    return this.advance(direction);
  }
  play() { ++this.request; this.stopped = false; this.update(); }
  pause() { ++this.request; this.stopped = true; this.update(); }
  block(reason, active) {
    if (this.blocks.has(reason) === active) return;
    if (active) {
      this.blocks.add(reason);
      // Temporary autoplay blockers must not discard an explicit photo choice.
      if (!this.stopped) ++this.request;
    } else this.blocks.delete(reason);
    this.update();
  }
}

function initialisePhotoCarousel(section, doc = document, win = window) {
  const images = Array.from(section.querySelectorAll('[data-photo]'));
  if (images.length < 2) return;
  const controls = section.querySelector('[data-photo-controls]');
  const toggle = section.querySelector('[data-photo-toggle]');
  const counter = section.querySelector('[data-photo-count]');
  const motion = win.matchMedia('(prefers-reduced-motion: reduce)');
  const carousel = new PhotoCarousel(images.length, {
    reduced: motion.matches,
    prepare: async index => {
      const image = images[index];
      image.loading = 'eager';
      await image.decode();
      if (!image.naturalWidth) throw new Error('Photo unavailable');
    },
    render: state => {
      images.forEach((image, index) => {
        const active = index === state.index;
        image.classList.toggle('is-active', active);
        image.setAttribute('aria-hidden', String(!active));
      });
      if (counter) counter.textContent = `${state.index + 1} of ${images.length}`;
      if (toggle) {
        toggle.textContent = state.stopped ? 'Play' : 'Pause';
        toggle.setAttribute('aria-label', `${state.stopped ? 'Play' : 'Pause'} automatic photo rotation`);
      }
    }
  });
  // Only enhance once decoding and viewport observation are supported.
  carousel.block('offscreen', true);
  carousel.block('hidden', doc.hidden);
  if (section.matches(':hover')) carousel.block('hover', true);
  if (section.contains(doc.activeElement)) carousel.block('focus', true);
  section.classList.add('photo-carousel-ready');
  images.forEach(image => { image.hidden = false; });
  if (controls) controls.hidden = false;
  section.querySelector('[data-photo-previous]')?.addEventListener('click', () => carousel.move(-1));
  section.querySelector('[data-photo-next]')?.addEventListener('click', () => carousel.move(1));
  toggle?.addEventListener('click', () => carousel.stopped ? carousel.play() : carousel.pause());
  section.addEventListener('mouseenter', () => carousel.block('hover', true));
  section.addEventListener('mouseleave', () => carousel.block('hover', false));
  section.addEventListener('focusin', () => carousel.block('focus', true));
  section.addEventListener('focusout', event => {
    if (!section.contains(event.relatedTarget)) carousel.block('focus', false);
  });
  doc.addEventListener('visibilitychange', () => carousel.block('hidden', doc.hidden));
  const applyMotion = () => {
    carousel.block('reduced', motion.matches);
    if (toggle) toggle.hidden = motion.matches;
  };
  motion.addEventListener('change', applyMotion);
  applyMotion();
  const observer = new win.IntersectionObserver(entries => {
    for (const entry of entries) if (entry.target === section) carousel.block('offscreen', !entry.isIntersecting);
  });
  observer.observe(section);
  return carousel;
}

if (typeof module !== 'undefined') module.exports = { PhotoCarousel, initialisePhotoCarousel };
if (typeof document !== 'undefined' && typeof window.IntersectionObserver === 'function' &&
    typeof window.HTMLImageElement.prototype.decode === 'function') {
  document.querySelectorAll('[data-photo-carousel]').forEach(section => initialisePhotoCarousel(section));
}
