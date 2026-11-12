(() => {
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  const german = document.documentElement.lang === 'de';
  let paused = preference.matches;
  const animations = new Map(), visible = new Set();
  const button = document.createElement('button');
  button.className = 'motion-toggle';
  button.type = 'button';
  document.querySelector('.topbar').after(button);
  const sync = () => {
    button.textContent = paused ? (german ? 'Animationen abspielen' : 'Play animations') : (german ? 'Animationen pausieren' : 'Pause animations');
    button.setAttribute('aria-pressed', String(!paused));
    animations.forEach((animation, target) => {
      if (paused || document.hidden || !visible.has(target)) animation.pause();
      else animation.play();
    });
  };
  const observer = new IntersectionObserver(entries => {
    entries.forEach(({target,isIntersecting}) => {
      isIntersecting ? visible.add(target) : visible.delete(target);
    });
    sync();
  }, {threshold:.15});
  const add = (selector,frames,duration,delay=0) => {
    document.querySelectorAll(selector).forEach(target => {
      const animation = target.animate(frames,{duration,delay,iterations:Infinity,easing:'ease-in-out'});
      animation.pause();animations.set(target,animation);observer.observe(target);
    });
  };
  add('.hero-mascot',[
    {transform:'translateY(0) rotate(-10deg)'},
    {transform:'translateY(-23px) rotate(-2deg)',offset:.25},
    {transform:'translateY(-7px) rotate(-15deg)',offset:.5},
    {transform:'translateY(-18px) rotate(-5deg)',offset:.75},
    {transform:'translateY(0) rotate(-10deg)'}
  ],4200);
  add('.hero-star',[
    {transform:'rotate(-12deg) scale(.85)',opacity:.65},
    {transform:'rotate(28deg) scale(1.2)',opacity:1},
    {transform:'rotate(-12deg) scale(.85)',opacity:.65}
  ],3000);
  const art = document.querySelector('.hero-art');
  if (art) for (let i=0;i<3;i++) {
    const star=document.createElement('span');star.className='motion-sparkle sparkle-'+i;
    star.textContent='✦';star.setAttribute('aria-hidden','true');art.append(star);
    add('.sparkle-'+i,[{transform:'translateY(5px) scale(.5)',opacity:.2},{transform:'translateY(-12px) scale(1)',opacity:1},{transform:'translateY(5px) scale(.5)',opacity:.2}],2600+i*450,i*400);
  }
  add('.feature-symbol', [{transform:'translateY(0) rotate(0)'},{transform:'translateY(-5px) rotate(7deg)'},{transform:'translateY(0) rotate(0)'}],4300);
  button.addEventListener('click',()=>{paused=!paused;sync()});
  preference.addEventListener('change',()=>{paused=preference.matches;sync()});
  document.addEventListener('visibilitychange',sync);
  sync();
})();
