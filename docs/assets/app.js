/* research-gym - renders the dashboard, the track and the reading list.
   Plain DOM on purpose: this file should stay readable by everyone in the gym. */

const PIPS = {
  "complete+stretch": { cls: "stretch", glyph: "★", label: "core and stretch" },
  complete: { cls: "complete", glyph: "✓", label: "core checks pass" },
  partial: { cls: "partial", glyph: "●", label: "in progress" },
  submitted: { cls: "partial", glyph: "○", label: "submitted" },
  broken: { cls: "broken", glyph: "!", label: "not loading" },
};

const el = (tag, props = {}, children = []) => {
  const node = Object.assign(document.createElement(tag), props);
  for (const child of [].concat(children)) {
    if (child != null) node.append(child);
  }
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

/* --- dashboard ----------------------------------------------------------- */

function renderBoard(table, curriculum, progress) {
  const people = progress.people ?? [];
  const rows = progress.progress ?? {};

  // Only show modules someone could plausibly have reached: everything ready,
  // plus anything anyone has actually submitted.
  const submitted = new Set(Object.values(rows).flatMap(Object.keys));
  const modules = curriculum.modules.filter(
    (m) => m.status === "ready" || submitted.has(m.id)
  );

  table.replaceChildren();

  if (!people.length) {
    table.append(
      el("tbody", {}, el("tr", {}, el("td", {
        className: "empty",
        textContent: "Nobody has merged an onboarding pull request yet. Be the first.",
      })))
    );
    return;
  }

  const head = el("tr", {}, el("th", { className: "person", textContent: "Who" }));
  for (const module of modules) {
    head.append(el("th", { title: module.summary ?? "", textContent: module.id.slice(0, 2) }));
  }
  table.append(el("thead", {}, head));

  const body = el("tbody");
  for (const person of people) {
    const name = el("td", { className: "person" }, [
      person.links?.github
        ? el("a", { href: person.links.github, textContent: person.name, rel: "noopener" })
        : person.name,
      el("span", { className: "role", textContent: person.role || person.track || "" }),
    ]);

    const row = el("tr", {}, name);
    for (const module of modules) {
      const entry = rows[person.handle]?.[module.id];
      const pip = PIPS[entry?.status] ?? { cls: "", glyph: "·", label: "not started" };
      const detail = entry
        ? `${module.title}: ${entry.core_passed}/${entry.core_total} core` +
          (entry.stretch_total ? `, ${entry.stretch_passed}/${entry.stretch_total} stretch` : "")
        : `${module.title}: not started`;
      row.append(
        el("td", {}, el("i", { className: `pip ${pip.cls}`, title: detail, textContent: pip.glyph }))
      );
    }
    body.append(row);
  }
  table.append(body);
}

/* --- the track ----------------------------------------------------------- */

function renderPhases(container, curriculum) {
  container.replaceChildren();

  for (const phase of curriculum.phases) {
    const modules = curriculum.modules.filter((m) => m.phase === phase.id);
    if (!modules.length) continue;

    const list = el("ul", { className: "modules" });
    for (const module of modules) {
      const ready = module.status === "ready";
      const chapter = module.book_chapter
        ? el("span", { className: "tag", textContent: `book ch.${module.book_chapter}` })
        : null;
      list.append(
        el("li", { className: ready ? "ready" : "" }, [
          el("span", { className: "num", textContent: module.id.slice(0, 2) }),
          el("span", { className: "name", textContent: module.title }),
          el("span", { className: "summary", textContent: module.summary ?? "" }),
          chapter,
          el("span", {
            className: `tag ${ready ? "ready" : ""}`,
            textContent: ready ? "open" : "soon",
          }),
        ])
      );
    }

    container.append(
      el("div", { className: "phase" }, [
        el("h3", { textContent: phase.name }),
        el("p", { className: "blurb", textContent: phase.blurb }),
        list,
      ])
    );
  }
}

/* --- reading ------------------------------------------------------------- */

function renderReading(container, curriculum, reading) {
  container.replaceChildren();
  const items = reading.items ?? [];

  if (!items.length) {
    container.append(el("p", { className: "empty", textContent: "No readings yet." }));
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
    container.append(
      el("h3", { className: "group", textContent: titleOf[key] ?? "Anytime" })
    );
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

/* --- wire it up ---------------------------------------------------------- */

(async function main() {
  const curriculum = await loadJSON("data/curriculum.json", { modules: [], phases: [] });

  document.title = curriculum.title ?? document.title;
  const tagline = document.getElementById("tagline");
  if (tagline && curriculum.tagline) tagline.textContent = curriculum.tagline;

  const repoLink = document.getElementById("repo-link");
  if (repoLink) {
    if (curriculum.repo) repoLink.href = curriculum.repo;
    else repoLink.remove();
  }

  const bookLink = document.getElementById("book-link");
  if (bookLink && curriculum.book?.url) bookLink.href = curriculum.book.url;

  const board = document.getElementById("board");
  if (board) {
    const progress = await loadJSON("data/progress.json", { people: [], progress: {} });
    renderBoard(board, curriculum, progress);
    const stamp = document.getElementById("generated");
    if (stamp && progress.generated_at) {
      stamp.textContent = `Updated ${new Date(progress.generated_at).toLocaleString()}`;
    }
  }

  const phases = document.getElementById("phases");
  if (phases) renderPhases(phases, curriculum);

  const reading = document.getElementById("reading");
  if (reading) renderReading(reading, curriculum, await loadJSON("data/reading.json", { items: [] }));
})();
