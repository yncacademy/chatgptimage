/* 550 ChatGPT Image Prompts — app logic (vanilla JS, no dependencies)
   Data: data/prompts.json → window.PROMPTS_DATA (inlined at build time by tools/build_site.py)
*/
(function () {
  "use strict";

  var DATA = window.PROMPTS_DATA;
  var items = DATA.items;
  var sections = DATA.sections;
  var catName = {};
  sections.forEach(function (s) { catName[s.slug] = s.name; });

  var state = { cat: "all", q: "", shown: 0, list: [] };
  var PAGE = 36;

  var $grid = document.getElementById("grid");
  var $count = document.getElementById("count-line");
  var $empty = document.getElementById("empty-state");
  var $sentinel = document.getElementById("sentinel");
  var $search = document.getElementById("search");
  var $searchClear = document.getElementById("search-clear");
  var $chips = document.getElementById("chip-row");
  var $loadNote = document.getElementById("load-note");

  var COLORS = ["#c25a12", "#1f7a45", "#96690a", "#0b6f88", "#1a5fb4", "#1c7259", "#c0124f"];
  function catColor(slug) {
    var h = 0;
    for (var i = 0; i < slug.length; i++) h = (h * 31 + slug.charCodeAt(i)) >>> 0;
    return COLORS[h % COLORS.length];
  }

  /* ── chips ─────────────────────────────────────────────────────────────── */
  function buildChips() {
    var frag = document.createDocumentFragment();
    var all = chipEl("all", "All prompts", 550);
    frag.appendChild(all);
    sections.forEach(function (s) { frag.appendChild(chipEl(s.slug, s.name, s.count)); });
    $chips.appendChild(frag);
  }
  function chipEl(slug, name, count) {
    var b = document.createElement("button");
    b.className = "chip"; b.type = "button";
    b.setAttribute("aria-pressed", slug === state.cat ? "true" : "false");
    b.dataset.cat = slug;
    var label = document.createElement("span");
    label.textContent = name;
    var n = document.createElement("span");
    n.className = "n"; n.textContent = String(count); n.setAttribute("aria-hidden", "true");
    b.appendChild(label); b.appendChild(n);
    b.setAttribute("aria-label", name + ", " + count + " prompts");
    return b;
  }
  $chips.addEventListener("click", function (e) {
    var btn = e.target.closest(".chip");
    if (!btn) return;
    state.cat = btn.dataset.cat;
    $chips.querySelectorAll(".chip").forEach(function (c) {
      c.setAttribute("aria-pressed", c.dataset.cat === state.cat ? "true" : "false");
    });
    reset();
  });

  /* ── search ────────────────────────────────────────────────────────────── */
  var debounce;
  $search.addEventListener("input", function () {
    clearTimeout(debounce);
    debounce = setTimeout(function () {
      state.q = $search.value.trim().toLowerCase();
      $searchClear.hidden = state.q === "";
      reset();
    }, 160);
  });
  $searchClear.addEventListener("click", function () {
    $search.value = ""; state.q = ""; $searchClear.hidden = true; reset(); $search.focus();
  });

  /* ── filtering ─────────────────────────────────────────────────────────── */
  function matches(num) {
    var it = items[num];
    if (state.cat !== "all" && it.c !== state.cat) return false;
    if (!state.q) return true;
    return (it.t + " " + it.p + " " + catName[it.c]).toLowerCase().indexOf(state.q) !== -1;
  }
  function reset() {
    state.list = [];
    for (var n = 1; n <= 550; n++) if (matches(String(n))) state.list.push(n);
    state.shown = 0;
    $grid.innerHTML = "";
    $empty.hidden = state.list.length !== 0;
    $loadNote.hidden = state.list.length === 0;
    renderMore();
  }
  function renderMore() {
    var canLoad = state.shown < state.list.length;
    $loadNote.hidden = !canLoad;
    $sentinel.hidden = !canLoad;
    if (!canLoad) return;
    var end = Math.min(state.shown + PAGE, state.list.length);
    var frag = document.createDocumentFragment();
    for (var i = state.shown; i < end; i++) frag.appendChild(cardEl(state.list[i]));
    $grid.appendChild(frag);
    state.shown = end;
    updateCount();
  }
  function updateCount() {
    $count.innerHTML = "Showing <strong>" + state.shown + "</strong> of <strong>" + state.list.length + "</strong> prompts";
  }

  function esc(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  var COPY_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="12" height="12" rx="2.5"/><path d="M5 15H4.5A2.5 2.5 0 0 1 2 12.5v-8A2.5 2.5 0 0 1 4.5 2h8A2.5 2.5 0 0 1 15 4.5V5"/></svg>';
  var CHECK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12.5 9.5 18 20 6.5"/></svg>';

  function cardEl(num) {
    var it = items[num];
    var li = document.createElement("li");
    li.className = "card"; li.dataset.num = num;

    var media = document.createElement("div");
    media.className = "card-media";
    var img = document.createElement("img");
    img.loading = "lazy"; img.decoding = "async";
    img.width = 640; img.height = 800;
    img.src = it.img; img.alt = it.t + " — example image, prompt #" + num;
    media.appendChild(img);
    var numBadge = document.createElement("span");
    numBadge.className = "card-num"; numBadge.textContent = "#" + num;
    media.appendChild(numBadge);

    var open = document.createElement("a");
    open.className = "card-link"; open.href = "#prompt-" + num;
    open.setAttribute("aria-label", "Open prompt #" + num + ": " + it.t);
    media.appendChild(open);

    var copy = document.createElement("button");
    copy.className = "card-copy"; copy.type = "button";
    copy.innerHTML = COPY_SVG + "<span>Copy</span>";
    copy.setAttribute("aria-label", "Copy prompt #" + num);
    copy.addEventListener("click", function (ev) {
      ev.stopPropagation();
      copyPrompt(it.p, copy);
    });
    media.appendChild(copy);

    var body = document.createElement("div");
    body.className = "card-body";
    body.innerHTML =
      '<span class="card-cat">' + esc(catName[it.c]) + "</span>" +
      '<h3 class="card-title">' + esc(it.t) + "</h3>" +
      '<p class="card-prompt">' + esc(truncate(it.p, 170)) + "</p>" +
      '<p class="card-why"><strong>Why it works:</strong> ' + esc(truncate(it.w, 110)) + "</p>";

    li.appendChild(media); li.appendChild(body);
    open.addEventListener("click", function (ev) {
      ev.preventDefault();
      openModal(parseInt(num, 10));
    });
    return li;
  }
  function truncate(s, n) {
    if (s.length <= n) return s;
    return s.slice(0, s.lastIndexOf(" ", n)) + "…";
  }

  /* ── clipboard ─────────────────────────────────────────────────────────── */
  function copyPrompt(text, btn) {
    function flash(b) {
      if (!b) return;
      var label = b.querySelector("span");
      var old = label ? label.textContent : null;
      b.classList.add("copied");
      if (label) label.textContent = "Copied";
      setTimeout(function () {
        b.classList.remove("copied");
        if (label) label.textContent = old;
      }, 1600);
    }
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(function () { flash(btn); }, function () { fallbackCopy(text, btn); });
    } else {
      fallbackCopy(text, btn);
    }
  }
  function fallbackCopy(text, btn) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.cssText = "position:fixed;left:-9999px;top:0;opacity:0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); flash(btn); } catch (e) { /* no-op */ }
    document.body.removeChild(ta);
  }

  /* ── modal ─────────────────────────────────────────────────────────────── */
  var modal = document.getElementById("modal");
  var mImg = document.getElementById("modal-img");
  var mNum = document.getElementById("modal-num");
  var mCat = document.getElementById("modal-cat");
  var mTitle = document.getElementById("modal-title");
  var mWhy = document.getElementById("modal-why");
  var mPrompt = document.getElementById("modal-prompt");
  var mCopy = document.getElementById("modal-copy");
  var mPrev = document.getElementById("modal-prev");
  var mNext = document.getElementById("modal-next");
  var mPos = document.getElementById("modal-pos");
  var mClose = document.getElementById("modal-close");
  var mNote = document.getElementById("copy-note");
  var current = null;
  var lastFocus = null;

  function openModal(num) {
    current = parseInt(num, 10);
    fillModal();
    lastFocus = document.activeElement;
    modal.hidden = false;
    document.body.style.overflow = "hidden";
    mClose.focus();
  }
  function closeModal() {
    modal.hidden = true;
    document.body.style.overflow = "";
    if (lastFocus) lastFocus.focus();
  }
  function fillModal() {
    var it = items[String(current)];
    mImg.src = it.img;
    mImg.alt = it.t + " — example image, prompt #" + current;
    mNum.textContent = "#" + current;
    mCat.textContent = catName[it.c];
    mCat.style.color = "#9c1044";
    mTitle.textContent = it.t;
    mWhy.innerHTML = "<strong>Why it works:</strong> " + esc(it.w);
    mPrompt.textContent = it.p;
    var pos = state.list.indexOf(current);
    mPos.textContent = (pos >= 0 ? (pos + 1) + " / " + state.list.length : "Prompt " + current + " of 550");
    mPrev.disabled = current <= 1;
    mNext.disabled = current >= 550;
    mNote.textContent = "";
    modal.querySelector(".modal-body").scrollTop = 0;
  }
  function step(d) {
    var n = current + d;
    if (n < 1 || n > 550) return;
    current = n;
    fillModal();
  }
  document.getElementById("empty-reset").addEventListener("click", function () {
    $search.value = ""; state.q = ""; $searchClear.hidden = true;
    state.cat = "all";
    $chips.querySelectorAll(".chip").forEach(function (c) {
      c.setAttribute("aria-pressed", c.dataset.cat === "all" ? "true" : "false");
    });
    reset();
    document.getElementById("gallery").scrollIntoView({ behavior: "smooth" });
  });
  mClose.addEventListener("click", closeModal);
  modal.querySelector(".modal-backdrop").addEventListener("click", closeModal);
  mPrev.addEventListener("click", function () { step(-1); });
  mNext.addEventListener("click", function () { step(1); });
  mCopy.addEventListener("click", function () {
    copyPrompt(items[String(current)].p, null);
    mNote.textContent = "Prompt copied to clipboard.";
    setTimeout(function () { mNote.textContent = ""; }, 2400);
  });
  document.addEventListener("keydown", function (e) {
    if (modal.hidden) return;
    if (e.key === "Escape") closeModal();
    else if (e.key === "ArrowLeft") step(-1);
    else if (e.key === "ArrowRight") step(1);
    else if (e.key === "Tab") {
      var f = modal.querySelectorAll("button, [href]");
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  /* ── random ────────────────────────────────────────────────────────────── */
  document.getElementById("random-btn").addEventListener("click", function () {
    var n = 1 + Math.floor(Math.random() * 550);
    openModal(n);
  });
  document.getElementById("random-btn-2").addEventListener("click", function () {
    var pool = state.list.length ? state.list : null;
    var n = pool ? pool[Math.floor(Math.random() * pool.length)] : 1 + Math.floor(Math.random() * 550);
    openModal(parseInt(n, 10));
  });

  /* ── infinite scroll ───────────────────────────────────────────────────── */
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && state.shown < state.list.length) renderMore();
      });
    }, { rootMargin: "1400px 0px" });
    io.observe($sentinel);
  } else {
    window.addEventListener("scroll", function () {
      if ($sentinel.getBoundingClientRect().top < window.innerHeight + 1200) renderMore();
    }, { passive: true });
  }

  /* ── boot ──────────────────────────────────────────────────────────────── */
  buildChips();
  reset();

  // deep link: /#prompt-123 opens that prompt
  var hash = location.hash.match(/^#prompt-(\d+)$/);
  if (hash) openModal(parseInt(hash[1], 10));
})();
