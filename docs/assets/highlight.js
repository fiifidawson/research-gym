// Python colouring for the editor.
//
// The textarea stays exactly where it was: the runner reads its .value, and
// undo, selection and mobile keyboards keep working. We render the same text
// as coloured markup in a <pre> directly behind it and make the textarea's own
// glyphs transparent, leaving just its caret. The two only line up while their
// font, padding, border and wrapping match, so those live together in one CSS
// rule rather than being repeated here.
(function () {
  const area = document.getElementById("code");
  const out = document.querySelector("#code-highlight code");
  if (!area || !out) return;

  const KEYWORDS =
    "and|as|assert|async|await|break|class|continue|def|del|elif|else|except|" +
    "finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|" +
    "raise|return|try|while|with|yield";
  const CONSTANTS = "True|False|None";
  const BUILTINS =
    "abs|all|any|bool|dict|enumerate|filter|float|format|getattr|hasattr|int|" +
    "isinstance|issubclass|len|list|map|max|min|next|object|open|print|range|" +
    "repr|reversed|round|set|setattr|sorted|str|sum|super|tuple|type|zip|" +
    "Exception|IndexError|KeyError|NotImplementedError|TypeError|ValueError";

  // String.raw so the backslashes reach the regex engine as written.
  // Ordered so the greediest constructs win: a # inside a string is not a
  // comment, and a keyword inside a comment is not a keyword.
  const TOKEN = new RegExp(
    [
      String.raw`(#[^\n]*)`, // 1 comment
      String.raw`([rRbBuUfF]{0,2}(?:"""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'))`, // 2 string
      String.raw`(@[A-Za-z_][\w.]*)`, // 3 decorator
      // Bases first: \b\d would otherwise take the 0 of 0xFF and leave xFF.
      // The leading-dot branch carries no \b, so .5 colours whole.
      String.raw`((?:\b0[xX][0-9a-fA-F_]+|\b0[bB][01_]+|\b0[oO][0-7_]+|\b\d[\d_]*\.?[\d_]*|\.\d[\d_]*)(?:[eE][+-]?\d+)?[jJ]?)`, // 4 number
      String.raw`\b(def|class)(\s+)([A-Za-z_]\w*)`, // 5 kw, 6 gap, 7 name
      String.raw`\b(` + CONSTANTS + String.raw`)\b`, // 8 constant
      String.raw`\b(` + KEYWORDS + String.raw`)\b`, // 9 keyword
      String.raw`\b(self|cls)\b`, // 10 self
      String.raw`\b(` + BUILTINS + String.raw`)\b(?=\s*\()`, // 11 builtin, only when called
    ].join("|"),
    "g"
  );

  const ESCAPES = { "&": "&amp;", "<": "&lt;", ">": "&gt;" };
  const esc = (s) => s.replace(/[&<>]/g, (c) => ESCAPES[c]);
  const wrap = (cls, text) => `<span class="t-${cls}">${esc(text)}</span>`;

  function colour(src) {
    let html = "";
    let last = 0;
    let m;
    TOKEN.lastIndex = 0;
    while ((m = TOKEN.exec(src))) {
      html += esc(src.slice(last, m.index));
      if (m[1]) html += wrap("comment", m[1]);
      else if (m[2]) html += wrap("string", m[2]);
      else if (m[3]) html += wrap("decorator", m[3]);
      else if (m[4]) html += wrap("number", m[4]);
      else if (m[5]) html += wrap("keyword", m[5]) + esc(m[6]) + wrap("name", m[7]);
      else if (m[8]) html += wrap("constant", m[8]);
      else if (m[9]) html += wrap("keyword", m[9]);
      else if (m[10]) html += wrap("self", m[10]);
      else if (m[11]) html += wrap("builtin", m[11]);
      last = TOKEN.lastIndex;
    }
    return html + esc(src.slice(last));
  }

  function render() {
    // <pre> swallows one trailing newline; without this the last blank line
    // the reader types would have nothing behind the caret.
    out.innerHTML = colour(area.value) + "\n";
    sync();
  }

  function sync() {
    out.parentNode.scrollTop = area.scrollTop;
    out.parentNode.scrollLeft = area.scrollLeft;
  }

  area.addEventListener("input", render);
  area.addEventListener("scroll", sync);
  // The runner replaces .value outright when you switch module, reset, or open
  // a file; assigning .value fires no input event, so it says so itself.
  area.addEventListener("codechange", render);

  render();
})();
