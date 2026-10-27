(() => {
  const scene = document.querySelector('.character-scene');
  const jump = document.querySelector('#jump-heroes');
  const toggle = document.querySelector('#toggle-motion');
  const status = document.querySelector('#hero-action-status');
  if (!scene || !jump || !toggle) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let reset;
  jump.addEventListener('click', () => {
    clearTimeout(reset);
    scene.classList.remove('jumping');
    if (!reduced.matches && !document.body.classList.contains('motion-paused')) {
      requestAnimationFrame(() => {
        scene.classList.add('jumping');
        reset = setTimeout(() => scene.classList.remove('jumping'), 850);
      });
    }
    status.textContent = 'Ian and Leo are ready for the adventure.';
  });
  toggle.addEventListener('click', () => {
    const paused = document.body.classList.toggle('motion-paused');
    toggle.setAttribute('aria-pressed', String(paused));
    toggle.textContent = paused ? 'Resume animation' : 'Pause animation';
  });
})();
