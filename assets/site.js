(() => {
  const nav = document.querySelector('.site-nav');
  const toggle = nav?.querySelector('.menu-toggle');
  if (!toggle) return;
  nav.classList.add('enhanced');
  function closeMenu(restoreFocus = false) {
    nav.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.textContent = 'Menu +';
    if (restoreFocus) toggle.focus();
  }
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
    toggle.textContent = open ? 'Close −' : 'Menu +';
  });
  nav.querySelectorAll('.site-links a').forEach(a => a.addEventListener('click', () => {
    closeMenu();
    const target = new URL(a.href);
    if (target.pathname === location.pathname && target.hash) {
      const section = document.getElementById(target.hash.slice(1));
      if (section) {
        section.setAttribute('tabindex', '-1');
        section.focus({preventScroll: true});
      }
    }
  }));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && nav.classList.contains('open')) closeMenu(true); });
  document.addEventListener('click', e => { if (!nav.contains(e.target)) closeMenu(); });
  nav.addEventListener('focusout', e => { if (!nav.contains(e.relatedTarget)) closeMenu(); });
  window.matchMedia('(max-width: 959px)').addEventListener('change', () => closeMenu());
})();


// Manual testimonial navigation preserves reading position and works with a keyboard.
(() => {
  const carousel = document.querySelector('.testimonial-carousel');
  const controls = document.querySelector('.testimonial-dots');
  if (!carousel || !controls) return;
  const cards = [...carousel.querySelectorAll('.testimonial-card')];
  const anchors = [...controls.querySelectorAll('a')];
  const status = document.createElement('p');
  status.className = 'visually-hidden';
  status.setAttribute('role', 'status');
  controls.after(status);
  let current = Math.max(0, cards.findIndex(card => '#' + card.id === location.hash));
  const buttons = anchors.map((anchor, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = anchor.className;
    button.setAttribute('aria-label', `Show testimonial ${index + 1} of ${cards.length}`);
    button.setAttribute('aria-controls', cards[index].id);
    button.addEventListener('click', () => show(index, true));
    anchor.replaceWith(button);
    return button;
  });
  function show(index, announce = false) {
    current = (index + cards.length) % cards.length;
    cards.forEach((card, i) => { card.hidden = i !== current; });
    buttons.forEach((button, i) => button.setAttribute('aria-pressed', String(i === current)));
    if (announce) status.textContent = `Testimonial ${current + 1} of ${cards.length}: ${cards[current].querySelector('.testimonial-meta').textContent.trim()}`;
  }
  carousel.classList.add('enhanced');
  show(current);
  window.addEventListener('hashchange', () => {
    const index = cards.findIndex(card => '#' + card.id === location.hash);
    if (index >= 0) show(index);
  });
})();


// Entrance-only motion: content is visible by default, even without JavaScript.
(() => {
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (motion.matches || !window.IntersectionObserver || !Element.prototype.animate) return;
  const animations = new Set();
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      observer.unobserve(entry.target);
      const animation = entry.target.animate(
        [{opacity: 0.2, transform: 'translateY(16px)'}, {opacity: 1, transform: 'translateY(0)'}],
        {duration: 550, easing: 'cubic-bezier(0.22, 1, 0.36, 1)'}
      );
      animations.add(animation);
      animation.onfinish = () => animations.delete(animation);
    }
  }, {threshold: 0, rootMargin: '0px 0px -32px 0px'});
  document.querySelectorAll('.home-page .fade-section:not(.hero) > .section-inner').forEach(section => observer.observe(section));
  document.addEventListener('focusin', event => {
    animations.forEach(animation => {
      if (animation.effect.target.contains(event.target)) {
        animation.cancel();
        animations.delete(animation);
      }
    });
  });
  motion.addEventListener('change', event => {
    if (!event.matches) return;
    observer.disconnect();
    animations.forEach(animation => animation.cancel());
    animations.clear();
  });
})();
