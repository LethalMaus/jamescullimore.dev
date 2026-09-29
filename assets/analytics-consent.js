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

  var memoryConsent = null;
  function getConsent() {
    try { return localStorage.getItem(consentKey) || memoryConsent; } catch (_) { return memoryConsent; }
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

    memoryConsent = consentValue;
    try { localStorage.setItem(consentKey, consentValue); } catch (_) {}

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
      '.analytics-consent-banner{position:fixed;left:auto;right:20px;bottom:max(16px,env(safe-area-inset-bottom));z-index:9999;width:min(420px,calc(100% - 32px));margin:0;padding:18px;background:#fff;border:1px solid #cbd7d1;border-radius:10px;box-shadow:0 8px 32px #183b4020;color:#183b40;font:14px/1.5 system-ui,sans-serif;}',
      '.analytics-consent-banner[hidden],.analytics-consent-manage[hidden]{display:none!important;}',
      '.analytics-consent-copy{margin:0 0 12px;font:inherit;}.analytics-consent-copy strong{display:block;margin-bottom:4px;}.analytics-consent-copy a{color:#176b70;text-decoration:underline;}',
      '.analytics-consent-actions{display:flex;gap:10px;}.analytics-consent-button{flex:1;min-height:44px;appearance:none;border:1px solid #849d92;border-radius:6px;padding:10px 12px;background:#f2f6f0;color:#183b40;font:600 14px/1.3 system-ui,sans-serif;cursor:pointer;}',
      '.analytics-consent-button:hover{background:#e2ece0;}.analytics-consent-button:focus-visible,.analytics-consent-manage:focus-visible{outline:3px solid #287f91;outline-offset:3px;}',
      '.analytics-consent-manage{display:block;position:static;margin:16px auto 20px;min-height:44px;appearance:none;border:1px solid #b0c1b7;border-radius:6px;padding:10px 14px;background:#fafaf6;color:#183b40;font:14px/1.4 system-ui,sans-serif;cursor:pointer;}',
      '@media(max-width:640px){.analytics-consent-banner{right:16px;bottom:max(12px,env(safe-area-inset-bottom));padding:14px;}}'
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
        '<p class="analytics-consent-copy"><strong>Analytics preferences</strong>Allow optional analytics to help improve this site? You can change your choice in the footer. <a href="/datenschutz.html">Privacy policy</a></p>' +
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
      var footers = document.querySelectorAll('footer');
      (footers[footers.length - 1] || document.body).appendChild(manage);
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
        memoryConsent = null;
        try { localStorage.removeItem(consentKey); } catch (_) {}
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
