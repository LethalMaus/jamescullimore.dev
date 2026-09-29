// Progressive enhancement: the authored code remains readable without JavaScript.
(() => {
  if (!window.hljs) return;
  const candidates = ['kotlin', 'java', 'groovy', 'bash', 'xml', 'json', 'javascript', 'css', 'ini', 'python', 'sql', 'yaml'].filter(name => hljs.getLanguage(name));
  // Bash grammars primarily colour shell syntax; external tools and flags need
  // their own tokens. Enhance only plain text nodes, never strings or comments.
  function highlightShellCommands(block) {
    const walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) {
      if (walker.currentNode.parentElement === block) nodes.push(walker.currentNode);
    }
    const tokens = /(?<commandLead>^\s*(?:\$\s*)?|\|\s*|&&\s*)(?<command>adb|emulator|maestro|gradle|\.\/gradlew|curl|git|openssl|grep|sed|awk|cat|ls|cd|mkdir|rm|python3?|java|keytool|apktool|jadx)\b|(?<optionLead>\s)(?<option>--?[A-Za-z][\w-]*)(?=[\s=]|$)/gm;
    for (const node of nodes) {
      const text = node.textContent;
      const fragment = document.createDocumentFragment();
      let offset = 0;
      for (const match of text.matchAll(tokens)) {
        fragment.append(document.createTextNode(text.slice(offset, match.index)));
        fragment.append(document.createTextNode(match.groups.commandLead ?? match.groups.optionLead));
        const span = document.createElement('span');
        span.className = match.groups.command ? 'hljs-built_in' : 'hljs-attr';
        span.textContent = match.groups.command ?? match.groups.option;
        fragment.append(span);
        offset = match.index + match[0].length;
      }
      if (offset) {
        fragment.append(document.createTextNode(text.slice(offset)));
        node.replaceWith(fragment);
      }
    }
  }
  function highlightFunctionCalls(block) {
    for (const node of [...block.childNodes]) {
      if (node.nodeType !== Node.TEXT_NODE) continue;
      const source = node.textContent;
      const fragment = document.createDocumentFragment();
      let offset = 0;
      for (const match of source.matchAll(/\b[A-Za-z_$][\w$]*(?=\s*(?:<[\w.,? ]+>)?\s*\()/g)) {
        fragment.append(document.createTextNode(source.slice(offset, match.index)));
        const span = document.createElement('span');
        span.className = 'hljs-title function_';
        span.textContent = match[0];
        fragment.append(span);
        offset = match.index + match[0].length;
      }
      if (offset) {
        fragment.append(document.createTextNode(source.slice(offset)));
        node.replaceWith(fragment);
      }
    }
  }
  document.querySelectorAll('.article-content pre code').forEach(block => {
    const source = block.textContent;
    if (!source.trim() || source.length > 50000) return;
    const declared = [...block.classList].find(name => name.startsWith('language-'))?.slice(9);
    if (declared === 'plaintext' || block.classList.contains('nohighlight')) return;
    let language = declared;
    // Older imports label many Kotlin/XML snippets as text or shell.
    if (!language || ['text', 'sh', 'bash'].includes(language)) {
      if (/\b(?:fun\s+\w+\s*\(|(?:val|var)\s+\w+\s*[:=]|suspend\s+fun|@Composable)/.test(source)) language = 'kotlin';
      else if (/^\s*(?:<\?xml|<(?:manifest|application|resources|activity|uses-permission|network-security-config)\b)/m.test(source)) language = 'xml';
      else if (/\b(?:public|private)\s+(?:static\s+)?(?:class|void)\b/.test(source)) language = 'java';
      else if (/^\s*(?:\$\s*)?(?:adb|emulator|maestro|gradle|\.\/gradlew|curl|git|export|echo|openssl)\s/m.test(source)) language = 'bash';
      else language = null;
    }
    try {
      const result = language && hljs.getLanguage(language)
        ? hljs.highlight(source, {language, ignoreIllegals: true})
        : hljs.highlightAuto(source, candidates);
      if (!language && result.relevance < 2) return;
      block.innerHTML = result.value;
      if (['kotlin', 'groovy', 'java'].includes(language || result.language)) highlightFunctionCalls(block);
      if (['bash', 'sh', 'shell'].includes(language || result.language)) highlightShellCommands(block);
      block.classList.add('hljs');
      block.dataset.highlighted = 'yes';
    } catch (_) {
      // A failed enhancement must not remove or alter the original code.
      block.textContent = source;
    }
  });
})();
