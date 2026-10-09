(() => {
  "use strict";
  const root = document.getElementById(__DIAGRAM_ID__);
  const button = root.querySelector(".ed-control");
  const viewport = root.querySelector(".ed-viewport");
  const motion = root.querySelector(".ed-motion");
  const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
  const query = new URLSearchParams(window.location.search);
  const requestedTime = query.has("time") ? Number(query.get("time")) : NaN;
  const frozen = Number.isFinite(requestedTime) && requestedTime >= 0;
  let playing = frozen ? false : !preference.matches;
  let visible = true;
  let initialized = false;

  function update() {
    const active = initialized && playing && visible && !document.hidden;
    if (active) motion.unpauseAnimations();
    else motion.pauseAnimations();
    root.dataset.playing = String(playing);
    root.dataset.active = String(active);
    const label = playing ? button.dataset.pauseDescription : button.dataset.playDescription;
    button.setAttribute("aria-label", label);
    button.setAttribute("aria-pressed", String(playing));
    button.title = label;
    button.querySelector("[data-play]").toggleAttribute("hidden", playing);
    button.querySelector("[data-pause]").toggleAttribute("hidden", !playing);
    button.querySelector("[data-caption]").textContent = playing ? button.dataset.pauseLabel : button.dataset.playLabel;
  }

  button.addEventListener("click", () => { playing = !playing; update(); });
  preference.addEventListener("change", event => { playing = !event.matches; update(); });
  document.addEventListener("visibilitychange", update);
  if (typeof IntersectionObserver !== "undefined") {
    new IntersectionObserver(entries => {
      visible = entries[0].isIntersecting;
      update();
    }).observe(viewport);
  }
  // Pause immediately; initialize after fonts are ready for repeatable captures.
  motion.pauseAnimations();
  update();
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(() => {
    if (frozen) motion.setCurrentTime(requestedTime);
    if (query.has("scroll")) {
      const offset = Number(query.get("scroll"));
      if (Number.isFinite(offset)) viewport.scrollLeft = Math.max(0, offset);
    }
    if (query.get("check") === "1") {
      const overflowing = [...root.querySelectorAll(".ed-node-title, .ed-node-subtitle, .ed-feature-title, .ed-feature-description")]
        .filter(label => label.scrollWidth > label.clientWidth + 0.5);
      overflowing.forEach(label => { label.style.outline = "2px solid #e5484d"; });
      root.dataset.overflow = String(overflowing.length);
      if (overflowing.length) console.warn("Overflowing labels:", overflowing.map(label => label.textContent));
    }
    initialized = true;
    root.dataset.ready = "true";
    update();
  });
})();
