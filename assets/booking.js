(function () {
  // Click intent only. The shared analytics helper enforces opt-in consent.
  // Never send URLs, email addresses, subjects, message bodies or booking data.
  var actions = {
    project_email: 'email',
    discovery_call: 'topmate',
    topmate_catalogue: 'topmate',
    fiverr_services: 'fiverr'
  };
  document.addEventListener('click', function (event) {
    var link = event.target.closest && event.target.closest('a[data-booking-action]');
    if (!link || typeof window.trackAnalyticsEvent !== 'function') return;
    var action = link.dataset.bookingAction;
    if (!Object.prototype.hasOwnProperty.call(actions, action)) return;
    window.trackAnalyticsEvent('booking_click', {
      booking_action: action,
      booking_provider: actions[action],
      link_location: link.closest('#contact') ? 'contact' : 'service_enquiry',
      page_path: location.pathname,
      page_language: document.documentElement.lang
    });
  });
})();
