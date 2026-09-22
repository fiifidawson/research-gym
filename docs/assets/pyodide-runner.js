/* Runs a module's checks.py in the browser, under Pyodide.

   docs/_browser/ holds copies of gym/ and checks.py, made at deploy time by
   .github/scripts/build_browser_bundle.py. Don't reimplement a check here -
   there should only ever be one copy of each assertion. */

const GYM_FILES = ["__init__.py", "checks.py", "data.py", "seed.py"];
const SITE_DIR = "/home/pyodide/site";

const GLUE = `
import importlib.util, json, sys, traceback

def _import(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def _gym_run(checks_path, submission_path):
    suite = _import(checks_path, "_gym_checks").SUITE
    try:
        submission = _import(submission_path, "_gym_submission")
    except Exception:
        return json.dumps({
            "loaded": False,
            "error": traceback.format_exc(limit=2),
        })
    return json.dumps({
        "loaded": True,
        "results": [check.run(submission) for check in suite.checks],
    })
`;

const $ = (id) => document.getElementById(id);
const status = (text) => ($("status").textContent = text);

const state = { pyodide: null, manifest: [], module: null, starters: new Map() };

async function text(path) {
  const response = await fetch(path, { cache: "no-cache" });
  if (!response.ok) throw new Error(`${path}: ${response.status}`);
  return await response.text();
}

async function boot() {
  try {
    state.manifest = await (await fetch("_browser/manifest.json", { cache: "no-cache" })).json();
  } catch {
    status("The browser bundle is missing - run build_browser_bundle.py.");
    return;
  }

  const select = $("module");
  select.replaceChildren(
    ...state.manifest.map((m) => new Option(`${m.id.slice(0, 2)} - ${m.title}`, m.id))
  );

  const wanted = new URLSearchParams(location.search).get("module");
  if (wanted && state.manifest.some((m) => m.id === wanted)) select.value = wanted;

  state.pyodide = await loadPyodide({ indexURL: "https://cdn.jsdelivr.net/npm/pyodide@0.26.4/" });
  status("Loading NumPy…");
  await state.pyodide.loadPackage("numpy");

  const fs = state.pyodide.FS;
  fs.mkdirTree(`${SITE_DIR}/gym`);
  fs.mkdirTree("/home/pyodide/submission");
  for (const name of GYM_FILES) {
    fs.writeFile(`${SITE_DIR}/gym/${name}`, await text(`_browser/gym/${name}`));
  }
  state.pyodide.runPython(`import sys; sys.path.insert(0, ${JSON.stringify(SITE_DIR)})`);
  state.pyodide.runPython(GLUE);

  await selectModule(select.value);
  $("run").disabled = false;
  status("Ready.");
}

async function selectModule(id) {
  const entry = state.manifest.find((m) => m.id === id);
  if (!entry) return;
  state.module = entry;

  const fs = state.pyodide.FS;
  fs.mkdirTree(`${SITE_DIR}/${id}`);
  fs.writeFile(`${SITE_DIR}/${id}/checks.py`, await text(`_browser/${id}/checks.py`));

  if (!state.starters.has(id)) {
    state.starters.set(
      id,
      entry.has_starter ? await text(`_browser/${id}/${entry.entrypoint}`) : ""
    );
  }

  const saved = localStorage.getItem(`research-gym:${id}`);
  setCode(saved ?? state.starters.get(id));
  $("results-pane").replaceChildren(
    Object.assign(document.createElement("p"), {
      className: "muted small",
      textContent: `Editing ${entry.entrypoint}.`,
    })
  );
}

function run() {
  const button = $("run");
  button.disabled = true;
  status("Running…");

  // Let the browser paint the disabled button before Pyodide blocks the thread.
  setTimeout(() => {
    try {
      const { id, entrypoint } = state.module;
      const path = `/home/pyodide/submission/${entrypoint}`;
      state.pyodide.FS.writeFile(path, $("code").value);
      const raw = state.pyodide.runPython(
        `_gym_run(${JSON.stringify(`${SITE_DIR}/${id}/checks.py`)}, ${JSON.stringify(path)})`
      );
      render(JSON.parse(raw));
    } catch (error) {
      renderBlocker(String(error));
    } finally {
      button.disabled = false;
    }
  }, 16);
}

function renderBlocker(message) {
  const pane = $("results-pane");
  pane.replaceChildren();
  pane.append(
    Object.assign(document.createElement("p"), { className: "group", textContent: "Could not run" }),
    Object.assign(document.createElement("pre"), { textContent: message })
  );
  status("Your file did not load.");
}

function render(payload) {
  if (!payload.loaded) return renderBlocker(payload.error);

  const pane = $("results-pane");
  pane.replaceChildren();

  for (const [label, tier] of [["Core", "core"], ["Stretch (optional)", "stretch"]]) {
    const results = payload.results.filter((r) => r.tier === tier);
    if (!results.length) continue;

    const passed = results.filter((r) => r.passed).length;
    pane.append(
      Object.assign(document.createElement("p"), {
        className: "group",
        textContent: `${label}: ${passed} of ${results.length}`,
      })
    );

    const list = document.createElement("ul");
    list.className = "results";
    for (const result of results) {
      const item = document.createElement("li");
      item.className = result.passed ? "pass" : "fail";
      item.append(
        Object.assign(document.createElement("span"), {
          className: "mark",
          textContent: result.passed ? "✓" : "✗",
        }),
        Object.assign(document.createElement("span"), { textContent: result.name })
      );
      if (!result.passed) {
        item.append(Object.assign(document.createElement("pre"), { textContent: result.error }));
        if (result.hint) {
          item.append(
            Object.assign(document.createElement("span"), {
              className: "hint",
              textContent: `Nudge: ${result.hint}`,
            })
          );
        }
      }
      list.append(item);
    }
    pane.append(list);
  }

  const core = payload.results.filter((r) => r.tier === "core");
  const remaining = core.filter((r) => !r.passed).length;
  status(
    remaining === 0
      ? "Core checks pass. Commit it and open the pull request."
      : `${remaining} core check${remaining === 1 ? "" : "s"} left.`
  );
}

// Assigning .value fires no input event, so the highlighter would keep showing
// the previous file. Everything that replaces the editor contents goes through
// here and says so.
function setCode(text) {
  $("code").value = text;
  $("code").dispatchEvent(new Event("codechange"));
}

function save() {
  if (!state.module) return;
  try {
    localStorage.setItem(`research-gym:${state.module.id}`, $("code").value);
  } catch {
    /* private window or full storage; the draft just isn't kept */
  }
}

$("run").addEventListener("click", run);
$("module").addEventListener("change", (event) => selectModule(event.target.value));
$("code").addEventListener("input", save);

$("reset").addEventListener("click", () => {
  if (!state.module) return;
  setCode(state.starters.get(state.module.id) ?? "");
  save();
});

$("file").addEventListener("change", async (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  setCode(await file.text());
  save();
  event.target.value = "";
});

document.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
    event.preventDefault();
    if (!$("run").disabled) run();
  }
});

boot().catch((error) => status(`Could not start: ${error}`));
