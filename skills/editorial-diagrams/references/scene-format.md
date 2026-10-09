# Scene adaptations beyond case parameters

Prefer the cases in [pattern-catalog.md](pattern-catalog.md). Use this lower-level interface when an adaptation requires geometry or behavior beyond their parameters, or when the user explicitly requests another composition. Preserve the selected case's visual grammar; the renderer supplies the shared presentation.

## Metadata

```json
{
  "locale": "en",
  "direction": "ltr",
  "kicker": "Figure 01",
  "title": "What the figure explains",
  "intro": "A concise explanation and any important assumptions.",
  "width": 1100,
  "height": 520,
  "animated": true,
  "duration": 12,
  "legend": [
    {"label": "Available", "shape": "circle", "color": "#9ae8c5"},
    {"label": "Occupied", "shape": "square", "color": "#70a0ff"}
  ],
  "scene": {"markup": "scene.svg", "style": "scene.css", "script": "scene.js"},
  "notes": ["Illustrative states; not production measurements."]
}
```

Only `markup` is required inside `scene`. File paths resolve relative to the metadata file. The CLI reads and embeds the selected local source files; generated output has no external runtime dependencies. A scene does not need graph `nodes`, `edges` or `groups`.

The frame fields and localization contract are shared with [graph-format.md](graph-format.md). `legend` may be empty. A custom entry specifies `shape` (`square`, `circle`, `diamond` or `line`) and a hexadecimal `color`; these are mark primitives, not diagram categories. Existing graph entries using `kind` continue to work.

Set `animated: false` for a static figure. It has no playback button and no running clock. `duration` is a positive number of seconds for the custom scene's illustrative cycle. `initialTime` optionally sets its starting point. `replay: true` adds a reset control (provide `ui.replay` for non-English output). The graph interface still preserves each edge's independent timing.

## Markup

Supply a body fragment, commonly a root SVG with a matching `viewBox` and a descriptive accessible name. HTML and SVG can be composed freely. No orthogonal-path or non-overlap constraint is applied to scenes.

```html
<svg class="capacity-study" viewBox="0 0 1100 520" role="img" aria-labelledby="__ID__-title">
  <title id="__ID__-title">A descriptive title in the user's language</title>
  <path d="M80 350 C250 100 450 440 650 200" class="trend" />
  <text x="80" y="65" data-ed-label data-ed-max-width="300">A direct label</text>
</svg>
```

`__ID__` is replaced with the unique root ID for IDs, URL references and accessibility links. Keep element IDs scoped this way when several figures may share a page. Do not use whole-document tags or include external asset references. Author and review executable scene code locally; the scene interface is not an HTML sanitizer.

Mark custom text with `data-ed-label` for optional width diagnostics. Add a numeric `data-ed-max-width` in local SVG units for SVG text, or CSS pixels for HTML labels. Without a declared width, only HTML scroll overflow can be measured. Inspect clipping, collisions and meaning independently.

## Styles

Use theme variables from [visual-language.md](visual-language.md). Scope every custom selector with `__ROOT__`, which becomes the figure's `#id`:

```css
__ROOT__ .capacity-study { display: block; width: 100%; height: 100%; }
__ROOT__ .trend { fill: none; stroke: var(--ed-ink); stroke-width: 1; }
__ROOT__ .capacity-study text { fill: var(--ed-ink); font-family: var(--ed-sans); }
```

The shared board maintains its designed scale with horizontal scrolling by default. Custom responsive rules are permitted when they preserve the explanation. Scope keyframe names and IDs with `__ID__` too. Do not impose a global stylesheet on the host page.

## Behavior and shared clock

The renderer wraps `scene.js` in an isolated function that supplies `root`, the figure's DOM root. It runs before the playback controller initializes. Register a listener rather than starting another independent animation loop:

```js
const marker = root.querySelector('[data-marker]');
root.addEventListener('ed:frame', event => {
  const {time, progress, cycle, duration, playing, active} = event.detail;
  marker.setAttribute('cx', String(80 + 500 * progress));
});
```

The event provides absolute elapsed `time` in seconds, normalized `progress` in `[0, 1)`, the cycle index, cycle duration, desired playback and effective activity. It fires for initialization, playback changes and active frames. Derive the complete scene state from its time so `?time=...` reconstructs the same state directly. Avoid dependence on how many prior frames ran.

The controller coordinates the clock with SVG SMIL and standard CSS/Web Animations within the board. Pausing freezes the state; resuming continues. Reduced motion, document visibility and offscreen state suspend animation. Static figures receive one initial frame for setup but never run a loop.

Dispatch `new CustomEvent("ed:seek", {detail: {time: 2.4, playing: false}})` on `root` to seek the common clock from a localized phase control or range input. Replay resets to zero and resumes.

Use your own state model for object identity, capacity, counts and ordering. The controller does not enforce simulation invariants. It supplies timing, not a domain simulator.

## Output and validation

```sh
python3 scripts/render.py --data /path/to/task/figure.json --output /path/to/task/figure.html
```

Deliver the metadata and referenced sources alongside the HTML. Scene validation covers frame metadata, localization, file loading and basic legend values, not arbitrary geometry or code semantics. Review the sources and inspect browser states at meaningful times. Test localized playback and static output, text fit, responsive behavior and domain invariants.
