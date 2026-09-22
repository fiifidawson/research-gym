// Light unless the reader picks dark. The choice is remembered per browser.
(function () {
  const KEY = "research-gym-theme";
  const root = document.documentElement;

  function apply(theme) {
    root.dataset.theme = theme;
    const button = document.getElementById("theme");
    if (button) {
      button.textContent = theme === "dark" ? "Light" : "Dark";
      button.setAttribute("aria-label", `Switch to ${theme === "dark" ? "light" : "dark"} mode`);
    }
  }

  let saved = "light";
  try {
    saved = localStorage.getItem(KEY) === "dark" ? "dark" : "light";
  } catch {
    /* private window or blocked storage: stay light */
  }
  apply(saved);

  document.addEventListener("DOMContentLoaded", () => {
    apply(root.dataset.theme);
    document.getElementById("theme")?.addEventListener("click", () => {
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      apply(next);
      try {
        localStorage.setItem(KEY, next);
      } catch {
        /* nothing to do; the page still switched for this visit */
      }
    });
  });
})();
