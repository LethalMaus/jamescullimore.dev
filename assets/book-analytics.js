(function () {
  // Count PDF link clicks, not completed downloads or unique readers.
  // Separate names avoid duplicating GA4's automatic file_download event.
  document.addEventListener('click', function (event) {
    var link = event.target.closest('a[data-book-pdf]');
    if (!link || typeof window.trackAnalyticsEvent !== 'function') return;
    var action = link.getAttribute('data-book-pdf');
    if (action !== 'download' && action !== 'open') return;
    window.trackAnalyticsEvent('book_pdf_' + action, {
      book_id: '5-minute-bedtime-stories-for-android-devs',
      link_location: link.getAttribute('data-book-location'),
      file_name: 'book.pdf',
      file_extension: 'pdf',
      link_url: link.href
    });
  });
})();
