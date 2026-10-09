# Graph configuration

Prefer a matching case from [pattern-catalog.md](pattern-catalog.md). This convenience interface handles explicitly positioned component-and-connection adaptations. Other case adaptations can use [scene-format.md](scene-format.md). The visual identity in [visual-language.md](visual-language.md) applies throughout.

The renderer uses explicit coordinates in CSS pixels. The agent plans the layout; the renderer validates geometry and produces HTML, CSS and SVG. It does not run an automatic graph-layout engine or translate text.

## Top-level fields

| Field | Meaning |
|---|---|
| `id` | Diagram identifier |
| `locale` | Language tag for generated content; defaults to `en` |
| `direction` | `ltr` or `rtl`; defaults to `ltr` |
| `ui` | Complete localized UI object described below |
| `kicker`, `title`, `intro` | Figure label, heading and explanation |
| `width`, `height` | Fixed board dimensions; the header is outside the board |
| `animated` | Optional boolean; use `false` for static output without playback controls |
| `duration` | Optional positive shared-clock cycle duration; defaults to 8 seconds |
| `legend` | Array of `{kind, label}`; kind is `request`, `response` or `change` |
| `groups` | Optional array of `{id, title, x, y, w, h}` |
| `nodes` | Nodes with explicit rectangles |
| `edges` | Directed edges with orthogonal path points |
| `notes` | Optional array of explanatory strings beneath the figure |
| `sources` | Optional `{title, url}` array; URLs must use HTTP or HTTPS |

All visible text belongs in the user's selected language. The renderer never requests source URLs during generation.

## Localization

```json
{
  "locale": "en-US",
  "direction": "ltr",
  "ui": {
    "play": "Play",
    "pause": "Pause",
    "playAnimation": "Play animation",
    "pauseAnimation": "Pause animation",
    "legend": "Legend",
    "scrollHint": "Scroll horizontally to explore the diagram"
  }
}
```

Translate every value in `ui` when selecting another language. The object must contain all six non-empty strings if supplied. A missing object defaults to English only for an English locale; other locales are rejected rather than silently receiving English controls.

`play` and `pause` are visible captions. `playAnimation` and `pauseAnimation` become the button's accessible name and tooltip. `legend` names the legend for assistive technology. `scrollHint` accompanies the diagram title in the scroll region's accessible name. Localized strings are HTML-escaped and read by the playback controller from data attributes.

The agent selects the language before rendering using the user's explicit preference, conversation language or known application locale. The generated page keeps that selected locale when shared; it does not silently translate itself according to a recipient's browser. Icons remain language-neutral geometric shapes.

## Nodes and groups

A normal node has `{id, title, subtitle?, icon?, x, y, w, h, group?}`. Coordinates always refer to the board. Valid icon names are `client`, `api`, `database`, `cache`, `blob`, `stream`, `service` and `more`.

Add `features: [{title, description}, ...]` for parallel capabilities. `featureColumns` is `2` or `3`. Allow room for a title, its 16px bottom gap, 62px feature rows, 12px row gaps and 16px outer padding. For `r` feature rows, a height of `57 + 74r` px fits exactly (two rows: 205, three rows: 279); add more only when you want extra breathing room. Normal nodes reserve approximately 62px for the icon, padding and gap. Actual text widths must be checked in the browser.

Groups are explanatory containers, not executable stages. Their headings also require clearance. Nodes may refer to an existing group using `group`.

## Edges

An edge has `{id, from, to, kind, points, label?, labelX?, labelY?, duration?, begin?}`.

- `points` is `[[x, y], ...]` ordered in the real direction of the edge.
- Adjacent points share an x or y coordinate and cannot be identical.
- The first and last points touch the borders of `from` and `to`.
- Route around unrelated nodes. Corners are rounded by up to 8px.
- If `label` is supplied, provide numeric `labelX` and `labelY` at its center.
- A response uses its own source, destination and ordered path; do not reverse its visual motion while keeping incorrect endpoint semantics.
- Durations are positive seconds. Defaults are 8 for request, 9 for response and 7 for change. `begin` is a numeric phase offset. These timings are illustrative.

## Rendering and review

When a script generates request and response pairs, give each edge its own copy of the point list. Reversing a shared list and then shifting coordinates moves the shared points twice.


```sh
python3 scripts/render.py --data examples/05-http3.json --output /path/to/task/http3.html
```

`--instance graph-one` sets an explicit root ID, which must start with a lowercase letter and use lowercase letters, digits or hyphens. Give each fragment a different instance ID when embedding several diagrams on one page. A host page must allow inline CSS and JavaScript. The graph's per-edge SVG timing is preserved; authored scenes can instead derive coherent state from the shared `ed:frame` clock.

Check labels after localization. Do not clip long translations or force them into small cards by reducing all text sizes. Adjust the layout and path endpoints together when resizing nodes.

The board scrolls horizontally at narrow widths. Use `?time=2.4&scroll=500` for deterministic browser checks. Add `check=1` to outline labels that overflow their cards; the diagram root then carries `data-overflow` with the number of overflowing labels. Default playback respects reduced motion, document visibility and whether the board is in view.
