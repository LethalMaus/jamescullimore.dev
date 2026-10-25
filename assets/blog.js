(() => {
  const form = document.querySelector('.blog-tools');
  const grid = document.getElementById('blog-grid');
  if (!form || !grid) return;
  const search = document.getElementById('blog-search');
  const topic = document.getElementById('blog-topic');
  const featured = document.getElementById('blog-featured');
  const featuredPage = grid.dataset.featured === 'true';
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
  let publications = {};
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
    if (article.featured_in?.length) {
      const features = element('div', 'article-features feature-compact');
      features.setAttribute('aria-label', 'Featured in newsletters and websites');
      features.append(element('p', 'feature-label', 'Featured in'));
      function badges(items) {
        const group = element('div', 'feature-badges');
        items.forEach(feature => {
          const pill = element('a', 'feature-pill');
          pill.href = feature.url;
          const icon = publications[feature.name]?.icon;
          const mark = icon ? element('img', 'publication-mark') : element('span', 'publication-mark publication-monogram', feature.name.split(' ').slice(0,2).map(w=>w[0]).join('').toUpperCase());
          if (icon) Object.assign(mark, {src:icon, alt:'', width:24, height:24, loading:'lazy'});
          else mark.setAttribute('aria-hidden', 'true');
          const copy = element('span', 'feature-copy');
          copy.append(element('strong', '', feature.name));
          if (feature.edition) copy.append(element('small', 'feature-edition', feature.edition));
          const arrow = element('span', 'feature-arrow', '↗');
          arrow.setAttribute('aria-hidden', 'true');
          pill.append(mark, copy, arrow);
          group.append(pill);
        });
        return group;
      }
      features.append(badges(article.featured_in.slice(0,2)));
      if (article.featured_in.length > 2) {
        const details = element('details', 'feature-more');
        const summary = element('summary');
        summary.append(element('span', 'feature-more-closed', `+${article.featured_in.length-2} more`), element('span', 'feature-more-open', 'Show fewer'), element('span', 'visually-hidden', ` features for ${article.title}`));
        details.append(summary, badges(article.featured_in.slice(2)));
        features.append(details);
      }
      node.append(features);
    }
    return node;
  }
  function update() {
    const query = search.value.trim().toLocaleLowerCase();
    const selectedTopic = topic.value;
    if (!query && !selectedTopic && !featured.value && !featuredPage) {
      grid.replaceChildren(...originalCards);
      status.textContent = originalStatus;
      pagination.hidden = false;
      more.hidden = true;
      return;
    }
    matches = all.filter(a => {
      const text = `${a.title} ${a.excerpt} ${a.tags.join(' ')}`;
      return (!featured.value || a.featured_in?.length) && query.split(/\s+/).every(word => text.toLocaleLowerCase().includes(word)) && (!selectedTopic || matchers[selectedTopic].test(text));
    });
    grid.replaceChildren(...matches.slice(0,visible).map(card));
    status.textContent = matches.length ? `${matches.length} matching article${matches.length === 1 ? '' : 's'} · Showing ${Math.min(visible,matches.length)}` : 'No articles found. Try another search or choose All topics.';
    pagination.hidden = true;
    more.hidden = matches.length <= visible;
  }
  form.addEventListener('submit', e => e.preventDefault());
  search.addEventListener('input', () => { visible=12; update(); });
  topic.addEventListener('change', () => { visible=12; update(); });
  featured.addEventListener('change', () => { visible=12; update(); });
  more.addEventListener('click', () => {
    const firstNew = visible;
    visible += 12;
    update();
    grid.children[firstNew]?.querySelector('.blog-title a')?.focus({preventScroll:true});
  });
  Promise.all(['/data/articles.json', '/data/publications.json'].map(url => fetch(url).then(r => { if (!r.ok) throw new Error('Article index unavailable'); return r.json(); }))).then(([data, brands]) => {
    all=data;
    publications=brands;
    form.hidden=false;
    if (featuredPage || featured.value || topic.value || search.value) update();
  }).catch(() => { /* Static archive links remain available if search cannot load. */ });
})();
