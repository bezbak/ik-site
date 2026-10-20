/*
 * Header/footer fixes shared by every page (Django templates and the static
 * export pages in public/):
 *  - keeps the page <title> the server rendered (Framer's runtime rewrites it
 *    to the title baked into its bundle, e.g. "Homy - About Us | ...");
 *  - hides the duplicated link lists in the phone menu overlay;
 *  - gives the Apartments/Cottages items the pages add to the header nav the
 *    same hover underline as the original items;
 *  - points Framer's extensionless export-time links ("./contact-us") at this
 *    site's real pages;
 *  - removes the leftover "Crafted by <Framer designer>" link;
 *  - tightens the empty gap above the logo in the phone footer;
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
    var css = '[data-framer-name="Crafted By"]{display:none!important}' +
      '[data-avat-dup]{display:none!important}';
    // Header nav items the pages add by cloning "ПЛАНИРОВКИ" (Apartments,
    // Cottages): Framer drives the original's hover underline from React
    // state (a .hover class plus a motion-animated "Fill" bar), which a cloned
    // node never gets, so replay the same slide-in/fade/colour with CSS.
    css += '.framer-eumtsr-container [data-avat-nav-clone] a [data-framer-name="Fill"]{' +
      'opacity:0!important;background-color:#fff!important;' +
      'transition:left 1s cubic-bezier(.2,.9,.2,1),opacity 1s cubic-bezier(.2,.9,.2,1),background-color 1s cubic-bezier(.2,.9,.2,1)}' +
      '.framer-eumtsr-container [data-avat-nav-clone] a:hover [data-framer-name="Fill"]{' +
      'left:0;opacity:1!important;background-color:rgb(16,40,78)!important}';
    // Phone footer: the exported layout leaves a ~100px empty band between the
    // CTA button and the logo (64px bottom padding + a 80px-tall logo box).
    css += '@media (max-width:809.98px){' +
      '.framer-fbxftr-container [data-framer-name="Content Area"]{padding-bottom:16px!important}' +
      '.framer-fbxftr-container [data-framer-name="Logo Image"]>a{height:32px!important}' +
      '}';
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

  // The phone/tablet menu overlay is client-rendered and mounts one "Links"
  // list per responsive variant, but the CSS that hides all but the active
  // variant only exists for markup present in the static export, so every
  // copy shows up and the menu items repeat. Keep the fullest list under each
  // parent (the real menu, including the Apartments/Cottages links the pages
  // add) and hide the rest.
  function dedupeMenuLinks() {
    var groups = [];
    document.querySelectorAll('.framer-eumtsr-container [data-framer-name="Links"]').forEach(function (el) {
      var parent = el.parentElement;
      if (!parent) return;
      var group = null;
      for (var i = 0; i < groups.length; i++) {
        if (groups[i].parent === parent) { group = groups[i]; break; }
      }
      if (!group) { group = { parent: parent, items: [] }; groups.push(group); }
      group.items.push(el);
    });
    groups.forEach(function (group) {
      if (group.items.length < 2) return;
      var best = group.items[0];
      group.items.forEach(function (el) {
        if (el.children.length > best.children.length) best = el;
      });
      group.items.forEach(function (el) {
        if (el === best) el.removeAttribute('data-avat-dup');
        else el.setAttribute('data-avat-dup', '');
      });
    });
  }

  // The export links its buttons to extensionless paths ("./contact-us",
  // "./properties", "./privacy-policy"). Framer's runtime handles those clicks
  // itself and routes them inside its bundled SPA, which renders the original
  // English template page (and 404s on reload) instead of this site's pages.
  var ROUTES = {
    'contact-us': '/contact-us.html',
    'properties': '/properties/',
    'about-us': '/about-us.html',
    'privacy-policy': '/privacy-policy.html',
    'terms-of-service': '/terms-of-service.html'
  };
  var ROUTE_RE = /^(?:\.{0,2}\/)*([a-z-]+)\/?([?#].*)?$/;

  function fixRouteLinks() {
    document.querySelectorAll('a[href]').forEach(function (a) {
      var m = ROUTE_RE.exec(a.getAttribute('href'));
      if (!m || !ROUTES[m[1]]) return;
      // Opened by the lead-form script instead of navigating.
      if (/Получить подборку/.test(a.textContent)) return;
      var target = ROUTES[m[1]] + (m[2] || '');
      a.dataset.avatRoute = target;
      // Only write when different: the href mutation re-triggers apply().
      if (a.getAttribute('href') !== target) a.setAttribute('href', target);
      if (a.dataset.avatRouted) return;
      a.dataset.avatRouted = '1';
      a.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        if (e.stopImmediatePropagation) e.stopImmediatePropagation();
        window.location.href = a.dataset.avatRoute;
      }, true);
    });
  }

  function apply() {
    dedupeMenuLinks();
    fixRouteLinks();
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

  // This script runs before Framer's modules, so document.title is still the
  // server-rendered one here.
  var pageTitle = document.title;
  var titleEl = document.querySelector('title');
  if (titleEl) {
    new MutationObserver(function () {
      if (document.title !== pageTitle) document.title = pageTitle;
    }).observe(titleEl, { childList: true, characterData: true, subtree: true });
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
