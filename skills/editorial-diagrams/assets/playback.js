(() => {
  "use strict";
  const root = document.getElementById(__DIAGRAM_ID__);
  const board = root.querySelector(".ed-board");
  const button = root.querySelector("[data-play-label]");
  const viewport = root.querySelector(".ed-viewport");
  const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
  const query = new URLSearchParams(window.location.search);
  const requestedTime = query.has("time") ? Number(query.get("time")) : NaN;
  const frozen = Number.isFinite(requestedTime) && requestedTime >= 0;
  const animated = root.dataset.animated !== "false" && !!button;
  const duration = Number(root.dataset.duration) || 8;
  let time = frozen ? requestedTime : Number(root.dataset.initialTime) || 0;
  let playing = animated && !frozen && !preference.matches;
  let visible = true;
  let initialized = false;
  let active = false;
  let lastTimestamp = null;
  let frame = null;

  function emitFrame() {
    const progress = (time % duration) / duration;
    root.dataset.time = String(time);
    root.dispatchEvent(new CustomEvent("ed:frame", {
      detail: {time, progress, cycle: Math.floor(time / duration), duration, playing, active}
    }));
  }

  function synchronizeMedia() {
    board.querySelectorAll("svg").forEach(svg => {
      if (typeof svg.pauseAnimations !== "function") return;
      svg.setCurrentTime(time);
      if (active) svg.unpauseAnimations();
      else svg.pauseAnimations();
    });
    if (typeof board.getAnimations === "function") {
      board.getAnimations({subtree: true}).forEach(animation => {
        animation.currentTime = time * 1000;
        if (active) animation.play();
        else animation.pause();
      });
    }
  }

  function tick(timestamp) {
    frame = null;
    if (!active) return;
    if (lastTimestamp !== null) time += Math.max(0, timestamp - lastTimestamp) / 1000;
    lastTimestamp = timestamp;
    emitFrame();
    frame = requestAnimationFrame(tick);
  }

  function update(resetClock = false) {
    const now = performance.now();
    if (resetClock === true) lastTimestamp = active ? now : null;
    if (active && lastTimestamp !== null) time += Math.max(0, now - lastTimestamp) / 1000;
    if (active) lastTimestamp = now;
    const wasActive = active;
    active = initialized && playing && visible && !document.hidden;
    if (active && !wasActive) lastTimestamp = now;
    root.dataset.playing = String(playing);
    root.dataset.active = String(active);
    if (button) {
      const label = playing ? button.dataset.pauseDescription : button.dataset.playDescription;
      button.setAttribute("aria-label", label);
      button.setAttribute("aria-pressed", String(playing));
      button.title = label;
      button.querySelector("[data-play]").toggleAttribute("hidden", playing);
      button.querySelector("[data-pause]").toggleAttribute("hidden", !playing);
      button.querySelector("[data-caption]").textContent = playing ? button.dataset.pauseLabel : button.dataset.playLabel;
    }
    if (!active) {
      if (frame !== null) cancelAnimationFrame(frame);
      frame = null;
      lastTimestamp = null;
    }
    if (initialized) emitFrame();
    synchronizeMedia();
    if (active && frame === null) frame = requestAnimationFrame(tick);
  }

  function checkLabels() {
    if (query.get("check") !== "1") return;
    const labels = [...root.querySelectorAll(".ed-node-title, .ed-node-subtitle, .ed-feature-title, .ed-feature-description, [data-ed-label]")];
    const overflowing = labels.filter(label => {
      const limit = Number(label.getAttribute("data-ed-max-width"));
      if (limit > 0) {
        const measured = typeof label.getBBox === "function" ? label.getBBox().width : label.getBoundingClientRect().width;
        return measured > limit + 0.5;
      }
      return label.scrollWidth > label.clientWidth + 0.5;
    });
    labels.forEach(label => { label.style.outline = overflowing.includes(label) ? "2px solid #e5484d" : ""; });
    root.dataset.overflow = String(overflowing.length);
    if (overflowing.length) console.warn("Overflowing labels:", overflowing.map(label => label.textContent));
  }

  root.addEventListener("ed:seek", event => {
    const value = event.detail && event.detail.time;
    if (typeof value !== "number" || !Number.isFinite(value) || value < 0) return;
    time = value;
    if (typeof event.detail.playing === "boolean") playing = animated && event.detail.playing;
    update(true);
  });
  root.querySelectorAll("[data-ed-replay]").forEach(control => {
    control.addEventListener("click", () => { time = 0; playing = animated; update(true); });
  });
  if (button) button.addEventListener("click", () => { playing = !playing; update(); });
  preference.addEventListener("change", event => { playing = animated && !event.matches; update(); });
  document.addEventListener("visibilitychange", update);
  if (typeof IntersectionObserver !== "undefined") {
    new IntersectionObserver(entries => {
      visible = entries[0].isIntersecting;
      update();
    }).observe(viewport);
  }
  if (typeof ResizeObserver !== "undefined") new ResizeObserver(checkLabels).observe(viewport);
  update();
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(() => {
    if (query.has("scroll")) {
      const offset = Number(query.get("scroll"));
      if (Number.isFinite(offset)) viewport.scrollLeft = Math.max(0, offset);
    }
    initialized = true;
    update();
    checkLabels();
    root.dataset.ready = "true";
  });
})();
