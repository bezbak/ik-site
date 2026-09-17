(function () {
  var ENDPOINT = '/api/leads/';

  var MODAL_HTML = '' +
    '<div id="avat-lead-modal" class="avat-lead-modal" hidden>' +
      '<div class="avat-lead-modal-backdrop" data-avat-lead-close></div>' +
      '<div class="avat-lead-modal-card" role="dialog" aria-modal="true" aria-labelledby="avat-lead-modal-title">' +
        '<button type="button" class="avat-lead-modal-close" data-avat-lead-close aria-label="Закрыть">&times;</button>' +
        '<h3 id="avat-lead-modal-title">Оставьте заявку</h3>' +
        '<p>Оставьте контакты — команда отдела продаж свяжется с вами в WhatsApp и поможет подобрать планировку.</p>' +
        '<form data-avat-lead-form>' +
          '<label>Ваше имя<input type="text" name="full_name" required autocomplete="name"></label>' +
          '<label>Телефон (WhatsApp)<input type="tel" name="phone" required autocomplete="tel" placeholder="+996 700 000 000"></label>' +
          '<fieldset><legend>Что интересует?</legend>' +
            '<label class="avat-lead-radio"><input type="radio" name="property_type" value="apartment" checked>Апартаменты</label>' +
            '<label class="avat-lead-radio"><input type="radio" name="property_type" value="cottage">Коттедж</label>' +
          '</fieldset>' +
          '<input type="text" name="website" class="avat-lead-hp" tabindex="-1" autocomplete="off" aria-hidden="true">' +
          '<button type="submit" class="avat-lead-submit">Отправить заявку</button>' +
          '<p class="avat-lead-status" data-avat-lead-status aria-live="polite"></p>' +
        '</form>' +
      '</div>' +
    '</div>';

  var CSS = '' +
    '.avat-lead-modal{position:fixed;inset:0;z-index:9999;display:flex;align-items:center;justify-content:center;padding:20px}' +
    '.avat-lead-modal[hidden]{display:none}' +
    '.avat-lead-modal-backdrop{position:absolute;inset:0;background:rgba(23,33,46,.55)}' +
    '.avat-lead-modal-card{position:relative;background:#fff;border-radius:20px;padding:32px;max-width:420px;width:100%;box-shadow:0 24px 60px rgba(0,0,0,.25);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;max-height:90vh;overflow:auto;box-sizing:border-box}' +
    '.avat-lead-modal-close{position:absolute;top:14px;right:14px;width:32px;height:32px;border-radius:50%;border:0;background:#F6F6F6;color:#17212E;font-size:20px;line-height:1;cursor:pointer}' +
    '.avat-lead-modal-card h3{margin:0 0 8px;font-size:22px;color:#17212E;font-weight:600}' +
    '.avat-lead-modal-card>p{margin:0 0 20px;font-size:14px;color:#637185;line-height:1.5}' +
    '.avat-lead-form-fields label{display:block;font-size:13px;color:#637185;margin-bottom:14px}' +
    '.avat-lead-form-fields input[type=text],.avat-lead-form-fields input[type=tel]{display:block;width:100%;margin-top:6px;padding:12px 14px;border:1px solid #DCE5F0;border-radius:10px;font-size:15px;color:#17212E;box-sizing:border-box;font-family:inherit}' +
    '.avat-lead-form-fields fieldset{border:0;padding:0;margin:0 0 18px;display:flex;gap:16px;flex-wrap:wrap}' +
    '.avat-lead-form-fields legend{font-size:13px;color:#637185;margin-bottom:8px;padding:0}' +
    '.avat-lead-radio{display:flex!important;align-items:center;gap:6px;font-size:14px!important;color:#17212E!important;margin:0!important}' +
    '.avat-lead-radio input{width:auto!important}' +
    '.avat-lead-hp{position:absolute!important;left:-9999px;width:1px;height:1px;opacity:0}' +
    '.avat-lead-submit{width:100%;background:#10284E;color:#fff;border:0;padding:14px;border-radius:12px;font-size:15px;font-weight:500;cursor:pointer;font-family:inherit}' +
    '.avat-lead-submit:hover{background:#19458B}' +
    '.avat-lead-submit:disabled{opacity:.6;cursor:default}' +
    '.avat-lead-status{margin:12px 0 0;font-size:13px;color:#637185;min-height:18px}' +
    '.avat-lead-status.is-error{color:#c0392b}' +
    '.avat-lead-status.is-ok{color:#1a7f4b}';

  function injectStyle() {
    if (document.getElementById('avat-lead-style')) return;
    var style = document.createElement('style');
    style.id = 'avat-lead-style';
    style.textContent = CSS;
    document.head.appendChild(style);
  }

  function ensureModal() {
    var existing = document.getElementById('avat-lead-modal');
    if (existing) return existing;
    document.body.insertAdjacentHTML('beforeend', MODAL_HTML);
    var modal = document.getElementById('avat-lead-modal');
    modal.querySelectorAll('[data-avat-lead-close]').forEach(function (el) {
      el.addEventListener('click', closeModal);
    });
    modal.querySelector('.avat-lead-modal-card form').className = 'avat-lead-form-fields';
    wireForm(modal.querySelector('[data-avat-lead-form]'));
    return modal;
  }

  function openModal(presetType) {
    injectStyle();
    var modal = ensureModal();
    if (presetType) {
      var radio = modal.querySelector('input[name="property_type"][value="' + presetType + '"]');
      if (radio) radio.checked = true;
    }
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    var modal = document.getElementById('avat-lead-modal');
    if (!modal) return;
    modal.hidden = true;
    document.body.style.overflow = '';
  }

  function submitForm(form, e) {
    if (e) e.preventDefault();
    if (form.dataset.avatSubmitting === '1') return;
    var status = form.querySelector('[data-avat-lead-status]');
    var fullName = form.elements.full_name ? form.elements.full_name.value.trim() : '';
    var phone = form.elements.phone ? form.elements.phone.value.trim() : '';
    var typeInput = form.querySelector('input[name="property_type"]:checked');

    function setStatus(text, cls) {
      if (!status) return;
      status.textContent = text;
      status.className = 'avat-lead-status' + (cls ? ' ' + cls : '');
    }

    if (!fullName || !phone || !typeInput) {
      setStatus('Заполните имя, телефон и тип недвижимости.', 'is-error');
      return;
    }

    var data = new FormData(form);
    data.set('source_page', window.location.pathname);
    form.dataset.avatSubmitting = '1';
    var submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;
    setStatus('Отправляем...', '');

    fetch(ENDPOINT, { method: 'POST', body: data, headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, body: j }; }); })
      .then(function (res) {
        form.dataset.avatSubmitting = '0';
        if (submitBtn) submitBtn.disabled = false;
        if (res.ok && res.body && res.body.ok) {
          setStatus('Спасибо! Мы свяжемся с вами в WhatsApp в ближайшее время.', 'is-ok');
          form.reset();
          setTimeout(closeModal, 2200);
        } else {
          setStatus('Проверьте, что заполнены имя и телефон.', 'is-error');
        }
      })
      .catch(function () {
        form.dataset.avatSubmitting = '0';
        if (submitBtn) submitBtn.disabled = false;
        setStatus('Не удалось отправить. Напишите нам в WhatsApp.', 'is-error');
      });
  }

  function wireForm(form) {
    if (!form || form.dataset.avatWired) return;
    form.dataset.avatWired = '1';
    form.addEventListener('submit', function (e) { submitForm(form, e); });
  }

  function wireTriggers() {
    document.querySelectorAll('a,button').forEach(function (el) {
      if (el.dataset.avatLeadWired) return;
      var text = (el.textContent || '').trim();
      if (text.indexOf('Получить подборку') === -1) return;
      el.dataset.avatLeadWired = '1';
      el.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        if (e.stopImmediatePropagation) e.stopImmediatePropagation();
        openModal();
      }, true);
    });
    document.querySelectorAll('[data-avat-lead-form]').forEach(wireForm);
  }

  window.AvatLeads = { open: openModal, wireTriggers: wireTriggers, wireForm: wireForm };

  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    wireTriggers();
  } else {
    document.addEventListener('DOMContentLoaded', wireTriggers);
  }
})();
