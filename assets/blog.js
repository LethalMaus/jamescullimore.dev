(() => {
  const form = document.querySelector('.blog-tools');
  const grid = document.getElementById('blog-grid');
  if (!form || !grid) return;
  const search = document.getElementById('blog-search');
  const topic = document.getElementById('blog-topic');
  const status = document.getElementById('blog-status');
  const pagination = document.querySelector('.pagination');
  const more = document.getElementById('more-results');
  const originalCards = [...grid.children];
  const originalStatus = status.textContent;
  const matchers = {
    Security: /secur|encrypt|https|permission|keystore|pinning|mitm|ipc|proguard/i,
    Testing: /test|maestro|espresso|qa |screenshot|ci time/i,
    Performance: /performance|startup|perfetto|build time|memory|leakcanary|ci time/i,
    Architecture: /architect|modul|decoupl|navigation|data layer|network layer|dependency|gradle/i,
    Compose: /compose|coil/i,
    'IoT & Wear OS': /wear os|bluetooth|\bble\b|wifi|wi-fi|zeromq|handover|iot/i,
    'Developer life': /interview|work.life|developer life|open.source|doubt|mask|contribut/i
  };
  let all = [];
  let matches = [];
  let visible = 12;
  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }
  function card(article) {
    const node = element('article', 'blog-card');
    const media = element('a', 'blog-card-media');
    media.href = article.url;
    media.tabIndex = -1;
    media.setAttribute('aria-hidden', 'true');
    const img = element('img');
    Object.assign(img, {src: article.image, alt: '', loading: 'lazy', width: 640, height: 360});
    media.append(img);
    const heading = element('h2', 'blog-title');
    const link = element('a', '', article.title);
    link.href = article.url;
    heading.append(link);
    let excerpt = article.excerpt;
    if (excerpt.length > 155) excerpt = excerpt.slice(0,155).replace(/\s+\S*$/, '') + '…';
    const tags = element('div', 'blog-tags');
    article.tags.slice(0,3).forEach(t => tags.append(element('span','blog-tag',t)));
    node.append(media, element('div','blog-date',article.date), heading, element('p','blog-excerpt',excerpt), tags);
    return node;
  }
  function update() {
    const query = search.value.trim().toLocaleLowerCase();
    const selectedTopic = topic.value;
    if (!query && !selectedTopic) {
      grid.replaceChildren(...originalCards);
      status.textContent = originalStatus;
      pagination.hidden = false;
      more.hidden = true;
      return;
    }
    matches = all.filter(a => {
      const text = `${a.title} ${a.excerpt} ${a.tags.join(' ')}`;
      return query.split(/\s+/).every(word => text.toLocaleLowerCase().includes(word)) && (!selectedTopic || matchers[selectedTopic].test(text));
    });
    grid.replaceChildren(...matches.slice(0,visible).map(card));
    status.textContent = matches.length ? `${matches.length} matching article${matches.length === 1 ? '' : 's'} · Showing ${Math.min(visible,matches.length)}` : 'No articles found. Try another search or choose All topics.';
    pagination.hidden = true;
    more.hidden = matches.length <= visible;
  }
  form.addEventListener('submit', e => e.preventDefault());
  search.addEventListener('input', () => { visible=12; update(); });
  topic.addEventListener('change', () => { visible=12; update(); });
  more.addEventListener('click', () => {
    const firstNew = visible;
    visible += 12;
    update();
    grid.children[firstNew]?.querySelector('.blog-title a')?.focus({preventScroll:true});
  });
  fetch('/data/articles.json').then(r => { if (!r.ok) throw new Error('Article index unavailable'); return r.json(); }).then(data => {
    all=data;
    form.hidden=false;
  }).catch(() => { /* Static archive links remain available if search cannot load. */ });
})();
