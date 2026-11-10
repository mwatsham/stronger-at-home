'use strict';

class FeedbackCarousel {
  constructor(count, { reduced = false, render = () => {}, schedule = (fn, ms) => setTimeout(fn, ms), cancel = id => clearTimeout(id) } = {}) {
    this.count = count;
    this.index = 0;
    this.stopped = false;
    this.blocks = new Set(reduced ? ['reduced'] : []);
    this.render = render;
    this.schedule = schedule;
    this.cancel = cancel;
    this.timer = null;
    this.update(false);
  }
  update(manual) {
    if (this.timer !== null) this.cancel(this.timer);
    this.timer = null;
    const running = this.count > 1 && !this.stopped && this.blocks.size === 0;
    this.render({ index: this.index, running, stopped: this.stopped, manual });
    if (running) this.timer = this.schedule(() => {
      this.index = (this.index + 1) % this.count;
      this.update(false);
    }, 8000);
  }
  move(direction) {
    this.stopped = true;
    if (this.count > 1) this.index = (this.index + direction + this.count) % this.count;
    this.update(true);
  }
  play() { this.stopped = false; this.update(false); }
  pause() { this.stopped = true; this.update(false); }
  block(reason, active) {
    if (active) this.blocks.add(reason); else this.blocks.delete(reason);
    this.update(false);
  }
}

if (typeof module !== 'undefined') module.exports = { FeedbackCarousel };

if (typeof document !== 'undefined') {
  const section = document.querySelector('[data-feedback-carousel]');
  if (section) {
    fetch('/feedback/feed.php', { credentials: 'same-origin', cache: 'no-store' })
      .then(response => { if (!response.ok) throw new Error('Unavailable'); return response.json(); })
      .then(data => {
        const quotes = data.quotes;
        if (!Array.isArray(quotes) || quotes.length === 0 || quotes.length > 100 ||
          quotes.some(q => !q || typeof q.text !== 'string' || !q.text.trim() || q.text.length > 2400 ||
            typeof q.attribution !== 'string' || !q.attribution.trim() || q.attribution.length > 400)) return;
        const text = section.querySelector('[data-quote]');
        const attribution = section.querySelector('[data-attribution]');
        const count = section.querySelector('[data-count]');
        const live = section.querySelector('[data-announcement]');
        const toggle = section.querySelector('[data-toggle]');
        const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
        const carousel = new FeedbackCarousel(quotes.length, {
          reduced: motion.matches,
          render: state => {
            text.textContent = quotes[state.index].text;
            attribution.textContent = quotes[state.index].attribution;
            count.textContent = (state.index + 1) + ' of ' + quotes.length;
            toggle.textContent = state.stopped ? 'Play' : 'Pause';
            toggle.setAttribute('aria-label', state.stopped ? 'Play automatic quote rotation' : 'Pause automatic quote rotation');
            if (state.manual) live.textContent = 'Quote ' + (state.index + 1) + ' of ' + quotes.length + ': ' + quotes[state.index].text + ' — ' + quotes[state.index].attribution;
          }
        });
        section.querySelector('[data-controls]').hidden = quotes.length < 2;
        section.querySelector('[data-previous]').addEventListener('click', () => carousel.move(-1));
        section.querySelector('[data-next]').addEventListener('click', () => carousel.move(1));
        toggle.addEventListener('click', () => carousel.stopped ? carousel.play() : carousel.pause());
        section.addEventListener('mouseenter', () => carousel.block('hover', true));
        section.addEventListener('mouseleave', () => carousel.block('hover', false));
        section.addEventListener('focusin', () => carousel.block('focus', true));
        section.addEventListener('focusout', e => { if (!section.contains(e.relatedTarget)) carousel.block('focus', false); });
        document.addEventListener('visibilitychange', () => carousel.block('hidden', document.hidden));
        carousel.block('hidden', document.hidden);
        const applyMotion = () => {
          carousel.block('reduced', motion.matches);
          toggle.hidden = motion.matches;
        };
        motion.addEventListener('change', applyMotion);
        applyMotion();
        section.hidden = false;
      }).catch(() => { /* Existing review links remain available if feedback is unavailable. */ });
  }
}
