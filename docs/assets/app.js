/* Renders the module list and the reading list from docs/data/. */

const el = (tag, props = {}, children = []) => {
  const node = Object.assign(document.createElement(tag), props);
  for (const child of [].concat(children)) if (child != null) node.append(child);
  return node;
};

async function loadJSON(path, fallback) {
  try {
    const response = await fetch(path, { cache: "no-cache" });
    if (!response.ok) throw new Error(response.status);
    return await response.json();
  } catch {
    return fallback;
  }
}

function renderTrack(container, curriculum) {
  container.replaceChildren();

  for (const phase of curriculum.phases) {
    const modules = curriculum.modules.filter((m) => m.phase === phase.id);
    if (!modules.length) continue;

    const list = el("ul", { className: "modules" });
    for (const module of modules) {
      list.append(
        el("li", {}, [
          el("span", { className: "id", textContent: module.id.slice(0, 2) }),
          el("span", { className: "name", textContent: module.title }),
          el("span", { className: "desc", textContent: module.summary ?? "" }),
          module.status === "ready"
            ? null
            : el("span", { className: "soon", textContent: "not open yet" }),
        ])
      );
    }

    container.append(
      el("p", { className: "phase-name", textContent: phase.name }),
      el("p", { className: "phase-note", textContent: phase.blurb }),
      list
    );
  }
}

function renderReading(container, curriculum, reading) {
  container.replaceChildren();
  const items = reading.items ?? [];
  if (!items.length) {
    container.append(el("p", { className: "muted", textContent: "Nothing here yet." }));
    return;
  }

  const titleOf = Object.fromEntries(curriculum.modules.map((m) => [m.id, m.title]));
  const groups = new Map();
  for (const item of items) {
    const key = item.module ?? "general";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
  }

  for (const [key, entries] of [...groups].sort()) {
    container.append(el("p", { className: "group", textContent: titleOf[key] ?? "Anytime" }));
    const list = el("ul", { className: "reading" });
    for (const item of entries) {
      list.append(
        el("li", {}, [
          el("a", { href: item.url, textContent: item.title, rel: "noopener", target: "_blank" }),
          el("span", {
            className: "meta",
            textContent: [item.source, item.kind, item.minutes && `${item.minutes} min`]
              .filter(Boolean)
              .join(" · "),
          }),
          item.why ? el("span", { className: "meta", textContent: item.why }) : null,
        ])
      );
    }
    container.append(list);
  }
}

(async function main() {
  const curriculum = await loadJSON("data/curriculum.json", { modules: [], phases: [] });

  const repoLink = document.getElementById("repo-link");
  if (repoLink) {
    if (curriculum.repo) repoLink.href = curriculum.repo;
    else repoLink.remove();
  }

  const bookLink = document.getElementById("book-link");
  if (bookLink && curriculum.book?.url) bookLink.href = curriculum.book.url;

  const track = document.getElementById("track");
  if (track) renderTrack(track, curriculum);

  const reading = document.getElementById("reading");
  if (reading) {
    renderReading(reading, curriculum, await loadJSON("data/reading.json", { items: [] }));
  }
})();
