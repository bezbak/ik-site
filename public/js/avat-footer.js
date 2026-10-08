/*
 * Footer fixes shared by every page (Django templates and the static export
 * pages in public/):
 *  - removes the leftover "Crafted by <Framer designer>" link;
 *  - wires the footer social icons (Instagram, Facebook, X, YouTube) to the
 *    URLs set in the admin (Контакты сайта -> Соцсети в футере), and hides
 *    the icons whose URL is empty.
 *
 * Framer's hydration runtime keeps recreating its original footer markup, so
 * everything is done through an injected <style> (survives re-renders) plus a
 * re-apply on DOM changes.
 */
(function () {
  var SOCIAL_KEYS = ['instagram', 'facebook', 'x', 'youtube'];
  var links = null;

  var style = document.createElement('style');
  style.setAttribute('data-avat-footer', '');
  document.head.appendChild(style);

  function updateCss() {
    var css = '[data-framer-name="Crafted By"]{display:none!important}';
    if (links) {
      SOCIAL_KEYS.forEach(function (key, i) {
        if (!links[key]) {
          css += '[data-framer-name="Social Icons"]>a:nth-of-type(' + (i + 1) + '){display:none!important}';
        }
      });
    }
    style.textContent = css;
  }

  function forceSocialLink(a, url) {
    if (a.getAttribute('href') !== url) a.setAttribute('href', url);
    if (a.getAttribute('target') !== '_blank') a.setAttribute('target', '_blank');
    a.setAttribute('rel', 'noopener');
    if (a.dataset.avatForced) return;
    a.dataset.avatForced = '1';
    // Framer's runtime handles clicks on its own <a> components with the
    // destination baked in at export time, so open the real URL ourselves.
    a.addEventListener('click', function (e) {
      var href = a.getAttribute('href');
      if (!href) return;
      e.preventDefault();
      e.stopPropagation();
      if (e.stopImmediatePropagation) e.stopImmediatePropagation();
      window.open(href, '_blank', 'noopener');
    }, true);
  }

  function apply() {
    document.querySelectorAll('[data-framer-name="Crafted By"]').forEach(function (n) {
      if (n.parentNode) n.parentNode.removeChild(n);
    });
    if (!links) return;
    document.querySelectorAll('[data-framer-name="Social Icons"]').forEach(function (box) {
      var anchors = box.querySelectorAll(':scope > a');
      SOCIAL_KEYS.forEach(function (key, i) {
        if (anchors[i] && links[key]) forceSocialLink(anchors[i], links[key]);
      });
    });
  }

  var scheduled = false;
  function scheduleApply() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(function () {
      scheduled = false;
      apply();
    });
  }

  updateCss();
  apply();

  fetch('/api/site-links/', { cache: 'no-store' })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (data) {
      if (!data) return;
      links = data;
      updateCss();
      apply();
    })
    .catch(function () {});

  new MutationObserver(scheduleApply).observe(document.documentElement, {
    childList: true, subtree: true, attributes: true, attributeFilter: ['href', 'target'],
  });
})();
