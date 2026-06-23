document.addEventListener("DOMContentLoaded", () => {
  const roots = document.querySelectorAll("[data-link-preview]");

  for (const root of roots) {
    try {
      const fallback = root.querySelector(".link-preview-fallback");
      if (!(fallback instanceof HTMLAnchorElement)) {
        continue;
      }

      const url = fallback.dataset.previewUrl || fallback.href;
      const title = fallback.dataset.previewTitle || "";
      const description = fallback.dataset.previewDescription || "";
      const image = fallback.dataset.previewImage || "";
      const siteName = fallback.dataset.previewSite || "";

      if (!url || !title) {
        continue;
      }

      const card = document.createElement("a");
      card.className = "link-preview-card";
      card.href = url;
      card.target = "_blank";
      card.rel = "noopener noreferrer";

      const content = document.createElement("div");
      content.className = "link-preview-content";

      if (siteName) {
        const site = document.createElement("p");
        site.className = "link-preview-site";
        site.textContent = siteName;
        content.appendChild(site);
      }

      const heading = document.createElement("h3");
      heading.className = "link-preview-title";
      heading.textContent = title;
      content.appendChild(heading);

      if (description) {
        const body = document.createElement("p");
        body.className = "link-preview-description";
        body.textContent = description;
        content.appendChild(body);
      }

      card.appendChild(content);

      if (image) {
        card.classList.add("has-image");
        const media = document.createElement("div");
        media.className = "link-preview-media";

        const img = document.createElement("img");
        img.className = "link-preview-image";
        img.src = image;
        img.alt = "";
        img.loading = "lazy";

        media.appendChild(img);
        card.appendChild(media);
      }

      root.insertBefore(card, fallback);
      root.classList.add("is-enhanced");
    } catch (_error) {
      // Leave the plain link visible if enhancement fails for any reason.
    }
  }
});
