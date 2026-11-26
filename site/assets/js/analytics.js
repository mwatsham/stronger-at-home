/* Owner-approved aggregate analytics: production public pages only. */
(function () {
  'use strict';
  const HOST = 'stronger-at-home.co.uk';
  const PAGES = Object.freeze({
    '/': 'Home', '/about/': 'About Melanie', '/how-i-can-help/': 'How I can help',
    '/appointments-and-fees/': 'Appointments and fees', '/contact/': 'Contact',
    '/privacy/': 'Privacy', '/accessibility/': 'Accessibility'
  });

  function buildPageview(location, referrer) {
    if (location.protocol !== 'https:' || location.hostname !== HOST ||
        !Object.prototype.hasOwnProperty.call(PAGES, location.pathname)) return null;
    let source = '';
    try {
      const ref = new URL(referrer);
      if (['https:', 'http:'].includes(ref.protocol) &&
          ![HOST, 'www.' + HOST].includes(ref.hostname)) source = ref.protocol + '//' + ref.hostname;
    } catch (_) { /* Missing or invalid referrer is not an identifiable source. */ }
    const tags = new URLSearchParams(location.search);
    const keys = ['utm_source', 'utm_medium', 'utm_campaign'];
    if (keys.every(key => tags.getAll(key).length <= 1)) {
      const pair = tags.get('utm_source') + '/' + tags.get('utm_campaign');
      const labels = {
        'google/business-profile': 'Google Business Profile',
        'facebook/business-page': 'Facebook business page',
        'email/newsletter': 'Email newsletter'
      };
      if (Object.prototype.hasOwnProperty.call(labels, pair)) source = labels[pair];
      if (pair === 'leaflet/local-leaflet' && tags.get('utm_medium') === 'qr') source = 'Leaflet QR';
    }
    return {path: location.pathname, title: PAGES[location.pathname], referrer: source, event: false};
  }

  function optedOut(window) {
    try {
      return window.__sahAnalyticsOptOut === true || window.navigator.doNotTrack === '1' ||
        window.navigator.globalPrivacyControl === true ||
        window.localStorage.getItem('sah-analytics-opt-out') === '1';
    } catch (_) { return true; }
  }

  function setupPrivacyControls(window, document) {
    const off = document.querySelector('[data-analytics-off]');
    const on = document.querySelector('[data-analytics-on]');
    const status = document.querySelector('[data-analytics-status]');
    if (!off || !on || !status) return;
    status.textContent = optedOut(window) ? 'Optional analytics are off in this browser.' : 'Optional analytics are on for production visits.';
    function save(disabled) {
      window.__sahAnalyticsOptOut = true;
      try {
        window.localStorage.setItem('sah-analytics-opt-out', disabled ? '1' : '0');
        status.textContent = disabled ? 'Optional analytics are off in this browser.' : 'Your choice is saved for your next page visit. Browser privacy signals still take priority.';
      } catch (_) {
        status.textContent = 'We could not save your choice. Analytics are off for this page; enable browser Do Not Track or Global Privacy Control to opt out on future visits.';
      }
    }
    off.addEventListener('click', () => save(true));
    on.addEventListener('click', () => save(false));
  }

  function startAnalytics(window, document, enabled) {
    if (enabled !== true) return;
    try {
      if (window.self !== window.top || document.visibilityState === 'prerender' || document.prerendering === true ||
          window.location.hash === '#toggle-goatcounter' ||
          window.__sahAnalyticsStarted) return;
      const page = buildPageview(window.location, document.referrer);
      if (!page) return;
      if (optedOut(window)) return;
      window.__sahAnalyticsStarted = true;
      const status = page.path === '/contact/' ? document.querySelector('[data-form-status]') : null;
      const success = status && status.dataset.flashKind === 'success';
      window.goatcounter = {
        no_onload: true, no_events: true,
        endpoint: 'https://stronger-at-home.goatcounter.com/count'
      };
      const script = document.createElement('script');
      script.src = 'https://gc.zgo.at/count.js';
      script.async = true;
      script.integrity = 'sha384-2UjvVpptg4JlEVgJI2PdscrjOjPcil/4F1ZvIMJ81CShQnEDSlPI+l4PfogvTLYi';
      script.crossOrigin = 'anonymous';
      script.referrerPolicy = 'no-referrer';
      let finished = false;
      script.onerror = function () { finished = true; };
      script.onload = function () {
        if (finished) return;
        finished = true;
        try {
          const counter = window.goatcounter;
          if (!counter || typeof counter.count !== 'function' || optedOut(window)) return;
          // The upstream default includes location.search and screen size even
          // with an explicit path. Project payloads deliberately omit both.
          // Reviewed against tests/js/fixtures/goatcounter-count.js (2026-11-26).
          counter.get_data = function (data) {
            return {p: data.path, t: data.title, r: data.referrer, e: data.event};
          };
          counter.count(page);
          if (success) counter.count({path: 'enquiry-submitted', title: 'Enquiry submitted', referrer: '', event: true});
        } catch (_) { /* Analytics must never interrupt the enquiry experience. */ }
      };
      document.head.appendChild(script);
    } catch (_) { /* Browser restrictions must not break the site. */ }
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {buildPageview, startAnalytics, setupPrivacyControls};
  } else {
    setupPrivacyControls(window, document);
    startAnalytics(window, document, true);
  }
}());
