// Keep the public YouTube link usable without JavaScript. Load the player only
// after an explicit click, while dedicated /videos/ pages retain static embeds.
(() => {
  document.querySelectorAll('a.video-preview[data-video-id]').forEach(link => {
    const id = link.dataset.videoId;
    if (!/^[\w-]{11}$/.test(id)) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = link.className;
    button.setAttribute('aria-label', link.getAttribute('aria-label'));
    button.append(...link.childNodes);
    button.addEventListener('click', () => {
      const frame = document.createElement('iframe');
      frame.title = link.dataset.videoTitle;
      frame.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&cc_load_policy=1';
      frame.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      frame.allowFullscreen = true;
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      frame.tabIndex = 0;
      button.replaceWith(frame);
      frame.focus();
    }, {once: true});
    link.replaceWith(button);
  });
})();
