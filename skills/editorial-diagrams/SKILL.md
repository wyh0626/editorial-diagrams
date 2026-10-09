---
name: editorial-diagrams
description: Create polished interactive architecture and protocol diagrams with aligned cards, orthogonal connectors and animated flow markers. Use for system architecture, request flows, protocol transport, event pipelines and engineering illustrations. Adapt diagram text and UI labels to the user's language.
---

# Editorial Diagrams

Turn a natural-language request into a precise, editable technical diagram. Own the content model, layout, JSON configuration, rendering and visual review. Do not ask the user to write JSON or calculate coordinates.

This is an independent community skill inspired by the editorial appearance of public engineering articles. Its bundled implementation uses original code, simple geometric icons and system fonts. It includes no extracted website templates, proprietary font files or brand assets, and makes no pixel-identity claim.

## Language and locale

The skill instructions and bundled examples are in English. Generated diagrams must follow the user's language rather than inheriting the example's language.

1. Use an explicitly requested output language first.
2. Otherwise use the user's current conversation language and any stated locale preference. Use a known application or browser locale only when the conversation gives no clear language signal. Do not infer language from usernames, directory names or geographic location.
3. Fall back to English when no language context is available. Resolve ordinary language choices without asking for confirmation.
4. Set `locale` to a suitable language tag and `direction` to `ltr` or `rtl`. Translate the title, description, node and group labels, legend, edge labels, notes and source captions consistently. Preserve standard technical identifiers, protocol names and code tokens when appropriate.
5. Supply all six `ui` strings in the chosen language: `play`, `pause`, `playAnimation`, `pauseAnimation`, `legend` and `scrollHint`. These control visible button captions, tooltips, accessible names, the legend name and the viewport hint. The renderer requires a complete UI object for non-English locales to prevent accidental English fallback.
6. Keep play, pause, arrows and component icons as language-neutral geometry. Localize their associated captions and accessibility labels rather than replacing them with language-specific text inside SVGs. For RTL content, check text direction and legibility while keeping graph ports and arrows consistent with the configured relationships.

The renderer does not translate text or detect the user's conversation language. Resolve the language as the agent before generating the configuration. See [references/graph-format.md](references/graph-format.md) for the localization contract.

## Drawing workflow

1. Identify the entities, grouping boundaries and actual directed relationships. State the scenario and distinguish parallel capabilities from sequential processing. Verify unfamiliar technical claims with authoritative references when research tools are available.
2. Read [references/graph-format.md](references/graph-format.md). Select an example with a suitable topology, or build a new graph. The examples are starting points, not a fixed menu.
3. Plan a balanced composition. Prefer aligned rows or columns, consistent card dimensions, mirrored endpoints for symmetric systems and ample whitespace. Reserve space for group headings, node descriptions, connector labels and arrowheads. Do not force unrelated subjects into an existing layout.
4. Write the task's JSON with the selected locale and complete localized UI labels. Position each node explicitly, then route horizontal and vertical segments from the actual source border to the destination border. Give requests and responses separate directed edges.
5. Invoke the bundled renderer with Python 3.8 or newer. Resolve it relative to this skill directory, and save task files in the task workspace:

```sh
python3 /path/to/editorial-diagrams/scripts/render.py --data /path/to/task/diagram.json --output /path/to/task/diagram.html
```

Use the actual resolved paths. Do not overwrite installed examples or skill files while drawing. The renderer uses only Python's standard library and creates a self-contained HTML file. `--instance` sets a stable unique root ID; `--fragment` produces an embeddable fragment with inline styles and script.

6. Inspect the generated HTML in a browser when preview tools are available. Open it with `?check=1` first: the page outlines every card label that overflows its box and reports the count in `data-overflow` on the diagram root and in the console. Then check desktop and narrow views, horizontal scrolling, fonts, text overflow, group-heading clearance, edge-label placement, arrowheads and alignment. Exercise play, pause and resume, including the localized captions, tooltips and accessible names.
7. Fix demonstrated issues in the configuration, rerender and inspect the affected view. Shorten labels, enlarge cards or revise geometry before reducing typography. Translate and recheck example labels after every locale change because text lengths differ.
8. Deliver the interactive HTML and editable JSON. Include a preview image when browser capture is available. Report any checks that could not be completed. The renderer itself does not take screenshots; use the host's available browser tools.

## Visual rules

- Use a white surface, a subtle 5px dot grid, 1px dark borders and 4px card corners.
- Keep a clear figure label, heading, short explanation, labeled playback control and legend.
- Use restrained request squares, response circles and change diamonds. Name the legend for the actual semantics of the diagram.
- Keep the board at its designed scale on narrow screens and allow horizontal scrolling. Do not shrink all text to fit a phone.
- Use system fonts. Text dimensions can vary by platform, so inspect actual rendering rather than relying only on character counts.
- Treat motion as a direction cue. Loop timing is not measured latency, packet count, throughput or a complete causal simulation.
- Keep related functionality grouped without implying an unsupported execution order.

## Quality and reuse

Structural validation checks finite geometry, board bounds, duplicate IDs, node overlap, orthogonal segments, endpoint attachment and connectors through unrelated nodes. It does not prove semantic correctness or that labels fit.

For deterministic screenshots, use `?time=2.4` to freeze animation and append `&scroll=500` to inspect a scrolled state. Respect reduced-motion preferences. Explain a technical diagram's assumptions in localized notes and attach relevant source links when useful.

Keep this skill self-contained. Do not introduce extracted website code, unlicensed fonts, brand icons or copied article templates. Bundled original files use the accompanying MIT license; materials imported by a user retain their own terms. Creating local output does not itself publish it.
