(function () {
  // Click intent only: never infer installs, enquiries sent, or unique clients.
  var appIds = {
    '6758762270': 'starjar', '6812278045': 'dontgotobed', '6812295504': 'watchful',
    'dev.jamescullimore.starjar': 'starjar',
    'dev.jamescullimore.dontgotobed': 'dontgotobed',
    'dev.jamescullimore.watchful': 'watchful'
  };
  document.addEventListener('click', function (event) {
    var link = event.target.closest && event.target.closest('a[href]');
    if (!link || typeof window.trackAnalyticsEvent !== 'function') return;
    var url = new URL(link.href, location.href);
    var parameters = { page_path: location.pathname };
    var appId;
    if (url.hostname === 'play.google.com' && url.pathname === '/store/apps/details') {
      appId = appIds[url.searchParams.get('id')];
      parameters.store = 'google_play';
    } else if (url.hostname === 'apps.apple.com') {
      var match = url.pathname.match(/\/id(\d+)(?:\/|$)/);
      appId = match && appIds[match[1]];
      parameters.store = 'app_store';
    }
    if (appId) {
      parameters.app_id = appId;
      parameters.link_location = link.closest('footer') ? 'footer' :
        link.closest('.hero, .hero-grid') ? 'hero' : 'content';
      window.trackAnalyticsEvent('app_store_click', parameters);
    } else if (url.protocol === 'mailto:' || url.protocol === 'tel:') {
      // Omit email addresses, phone numbers, subjects and message bodies.
      parameters.contact_method = url.protocol === 'mailto:' ? 'email' : 'phone';
      parameters.contact_context = location.pathname === '/' ? 'project' : 'page';
      window.trackAnalyticsEvent('contact_click', parameters);
    }
  });
})();
