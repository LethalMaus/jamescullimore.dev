(function () {
  var measurementId = 'G-TYPWQYLWYH';
  var consentKey = 'analytics_consent';
  var loadedFlag = '__gaLoaded';
  var styleId = 'analytics-consent-style';

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function gtag() {
    dataLayer.push(arguments);
  };

  gtag('consent', 'default', {
    analytics_storage: 'denied',
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied'
  });

  function loadAnalytics() {
    if (window[loadedFlag]) return;
    window[loadedFlag] = true;

    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + measurementId;
    document.head.appendChild(script);

    gtag('js', new Date());
    gtag('config', measurementId);
  }

  function getConsent() {
    return localStorage.getItem(consentKey);
  }

  function syncUi() {
    var consent = getConsent();
    var banner = document.getElementById('analytics-consent-banner');
    var manage = document.getElementById('analytics-consent-manage');

    if (!banner || !manage) return;

    var hasDecision = consent === 'granted' || consent === 'denied';
    banner.hidden = hasDecision;
    manage.hidden = !hasDecision;
  }

  function setConsent(granted) {
    var consentValue = granted ? 'granted' : 'denied';

    gtag('consent', 'update', {
      analytics_storage: consentValue
    });

    localStorage.setItem(consentKey, granted ? 'granted' : 'denied');

    if (granted) {
      loadAnalytics();
    }

    syncUi();
  }

  function ensureStyles() {
    if (document.getElementById(styleId)) return;

    var style = document.createElement('style');
    style.id = styleId;
    style.textContent = [
      '.analytics-consent-banner{position:fixed;left:20px;right:20px;bottom:20px;z-index:9999;max-width:960px;margin:0 auto;padding:18px 20px;border:1px solid rgba(17,24,39,.14);border-radius:18px;background:rgba(252,252,249,.98);color:#111827;box-shadow:0 20px 50px rgba(15,23,42,.18);backdrop-filter:blur(14px);font:400 14px/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;}',
      '.analytics-consent-banner[hidden]{display:none !important;}',
      '.analytics-consent-copy{margin:0 0 12px;}',
      '.analytics-consent-copy strong{display:block;margin-bottom:4px;font-size:15px;}',
      '.analytics-consent-copy a{color:inherit;text-decoration:underline;}',
      '.analytics-consent-actions{display:flex;gap:10px;flex-wrap:wrap;align-items:center;}',
      '.analytics-consent-button{appearance:none;border:0;border-radius:999px;padding:10px 16px;font:600 13px/1 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;cursor:pointer;transition:transform .15s ease,opacity .15s ease;}',
      '.analytics-consent-button:hover{transform:translateY(-1px);}',
      '.analytics-consent-button-primary{background:#0f172a;color:#fff;}',
      '.analytics-consent-button-secondary{background:#e5e7eb;color:#111827;}',
      '.analytics-consent-manage{position:fixed;right:18px;bottom:18px;z-index:9998;appearance:none;border:1px solid rgba(17,24,39,.14);border-radius:999px;padding:10px 14px;background:rgba(252,252,249,.95);color:#111827;box-shadow:0 14px 34px rgba(15,23,42,.14);font:600 12px/1 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;cursor:pointer;backdrop-filter:blur(12px);}',
      '.analytics-consent-manage[hidden]{display:none !important;}',
      '@media (max-width:640px){.analytics-consent-banner{left:12px;right:12px;bottom:12px;padding:16px;}.analytics-consent-actions{flex-direction:column;align-items:stretch;}.analytics-consent-button{width:100%;}.analytics-consent-manage{right:12px;bottom:12px;}}'
    ].join('');
    document.head.appendChild(style);
  }

  function ensureUi() {
    ensureStyles();

    if (!document.getElementById('analytics-consent-banner')) {
      var banner = document.createElement('section');
      banner.className = 'analytics-consent-banner';
      banner.id = 'analytics-consent-banner';
      banner.setAttribute('aria-label', 'Analytics consent');
      banner.hidden = true;
      banner.innerHTML =
        '<p class="analytics-consent-copy"><strong>Analytics preferences</strong>This site uses Google Analytics only if you opt in. You can change your choice at any time. <a href="/datenschutz.html">Privacy policy</a></p>' +
        '<div class="analytics-consent-actions">' +
        '<button type="button" class="analytics-consent-button analytics-consent-button-primary" data-analytics-consent="accept">Allow analytics</button>' +
        '<button type="button" class="analytics-consent-button analytics-consent-button-secondary" data-analytics-consent="decline">Decline</button>' +
        '</div>';
      document.body.appendChild(banner);
    }

    if (!document.getElementById('analytics-consent-manage')) {
      var manage = document.createElement('button');
      manage.type = 'button';
      manage.id = 'analytics-consent-manage';
      manage.className = 'analytics-consent-manage';
      manage.textContent = 'Analytics settings';
      manage.hidden = true;
      document.body.appendChild(manage);
    }

    document.addEventListener('click', function (event) {
      var action = event.target.getAttribute('data-analytics-consent');

      if (action === 'accept') {
        setConsent(true);
      }

      if (action === 'decline') {
        setConsent(false);
      }

      if (event.target.id === 'analytics-consent-manage') {
        localStorage.removeItem(consentKey);
        syncUi();
      }
    });
  }

  window.setAnalyticsConsent = setConsent;

  if (getConsent() === 'granted') {
    loadAnalytics();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      ensureUi();
      syncUi();
    });
  } else {
    ensureUi();
    syncUi();
  }
})();
