---
name: editorial-diagrams
description: Draw technical illustrations by selecting and adapting the five composition families demonstrated in OpenAI's storage engineering article: architecture, request flow, paired timelines, connection-pool reuse and connection aggregation. Match the article's visual grammar and behavior, choose the case for the user's scenario, and localize all generated text and controls.
---

# Editorial Diagrams

Select a proven engineering-article composition, then adapt its labels, participants and model to explain the user's idea. The default is the article case library, not unrestricted visual invention. The user describes the subject; the agent selects the suitable case.

The reference is [Scaling storage to one billion users](https://openai.com/zh-Hans-CN/index/scaling-storage-one-billion-users-part-one/). Its six figures provide five composition families, with LIFO and FIFO variants of the same connection-pool composition. The bundled implementations are original code using system fonts, not extracted website components or proprietary fonts. They preserve the case structure and illustrative behavior without claiming pixel identity.

## Select a case before drawing

Read [references/pattern-catalog.md](references/pattern-catalog.md). Choose the case by the relationship the reader needs to understand, not by isolated keywords or by always preferring a flowchart.

| Reader's question | Pattern | Article reference |
|---|---|---|
| What are the components, responsibilities and dependencies? | `architecture` | Figure 01 |
| Which components does an operation pass through? | `request-flow` | Figure 02 |
| Where is time spent, and what becomes ready while a resource is busy? | `timeline-comparison` | Figure 03 |
| Which returned resource is selected next, and how does that affect load? | `pool-reuse` with `policy: lifo` or `fifo` | Figures 04A / 04B |
| How can the same workload use fewer downstream connections? | `connection-aggregation` | Figure 05 |

For example, a request's route through proxies calls for Figure 02; stream multiplexing that reduces connections calls for Figure 05; latency caused by scheduling calls for Figure 03. The word “connection” alone does not decide between a pool-allocation model and an aggregation comparison.

When several questions matter, make a small sequence of suitable cases or compare variants. State the selected case and its purpose briefly, then create the figure. Do not ask the user to choose a diagram type when their intent is sufficient. If none fits exactly, adapt the closest case while retaining its visual grammar; describe substantive model changes. Use custom scene authoring only when the bundled parameters cannot represent the required content, or when the user explicitly requests another composition.

## Adapt the selected case

1. Open its JSON under `examples/blog/`. Copy it into the task workspace; never overwrite installed examples while drawing.
2. Replace the title, explanation, labels and participants with the user's subject. Retain the distinguishing composition: component columns, branched request paths, paired time tracks, ordered returned-resource chips, or repeated connection scenarios.
3. Set `pattern`, `content`, and applicable `model` parameters. The renderer computes board dimensions and placement. Keep model assumptions consistent between compared scenarios.
4. Render with the bundled Python 3.8+ script:

```sh
python3 /path/to/editorial-diagrams/scripts/render.py --data /path/to/task/figure.json --output /path/to/task/figure.html
```

Resolve the actual skill path. The renderer has no third-party dependencies and emits self-contained HTML. `--instance` sets a stable root ID; `--fragment` emits an embeddable fragment. Figures with replay controls require `ui.replay` in non-English output.

5. Inspect the rendered result, correct demonstrated problems, and deliver the HTML plus editable JSON and an optional preview.

The two scheduling scenarios use one shared time scale. The two pool policies use identical arrivals, server work and connection counts. The aggregation scenarios use the same upstream workload. Keep these comparisons intact when changing their parameters. Do not turn a pool diagram into a generic queue picture or replace a connection-count comparison with proportional bars.

## Preserve the blog's visual grammar

Read [references/visual-language.md](references/visual-language.md). Use white surfaces, thin dark structure, small corner radii, restrained accents, compact mono annotations and a clear figure/title/explanation hierarchy. Architecture and request paths use the subtle dot grid. Timelines, pool demonstrations and connection scenarios use plain white backgrounds.

Preserve each case's own geometry and density. Timeline segments share a scale; pool resources are pills and workload entries are rectangles; aggregation uses retained connection rails, dashed idle lines and request/response markers. The blue/green/purple flow palette is not mandatory for every case: CPU timelines use their blue phase palette. Replay, phase selection and seeking appear where the case needs them.

Do not add dashboard metrics, decorative curves, oversized numbers, arbitrary chart types or unrelated icons to make the figure look more elaborate. Customize the article's case rather than replacing its structure with a new visual metaphor.

## Language

These instructions and authoring references stay in English. Generated figures follow the user's explicitly requested language, then conversation language, then a known application locale; otherwise use English. Never infer language from paths or usernames.

Set `locale` and `direction`. Translate headings, descriptions, legends, notes, `content.labels`, participant captions, controls, tooltips and accessible names. Preserve appropriate protocol and code identifiers. Provide the six `ui` strings `play`, `pause`, `playAnimation`, `pauseAnimation`, `legend`, `scrollHint`; add `replay` for patterns that use it. Non-English patterns reject missing internal labels rather than silently mixing languages. Recheck text fit after translation.

## Behavior and verification

- Motion must follow the selected model. Preserve resource identity, return order, capacity, one-thread scheduling, counts and shared comparison conditions.
- Use `?time=...&check=1` for repeatable captures and label-overflow diagnostics. Pattern details in the catalog explain the mapping from playback seconds to model time.
- Inspect desktop and narrow layouts. Request flow has a vertical phone composition; pool reuse compacts its columns; architecture, paired timelines and aggregation preserve scale with horizontal scrolling.
- Inspect initial, intermediate and outcome states. Exercise localized play/pause/replay, phase buttons or time seeking as applicable. Verify reduced-motion and visibility handling when the host can test them.
- Correct layout and text before shrinking typography. The renderer cannot validate arbitrary technical explanations or prove fidelity in every browser.
- Label timings and counts as illustrative unless they are actual measurements. The supplied cases do not establish general performance guarantees for FIFO, LIFO, Python or HTTP/2.

## Additional authoring interfaces

The [graph interface](references/graph-format.md) remains available for architecture topologies that need explicitly positioned nodes. The [scene interface](references/scene-format.md) is an escape hatch for adaptations beyond the bundled case parameters; retain the chosen case's structure and style. Neither is the default substitute for selecting a blog case.

Keep output scoped and self-contained. Review executable scene code locally; do not pass through untrusted remote HTML. Do not distribute extracted website code, proprietary fonts or brand assets. Bundled original files use the MIT license. Generation does not publish a result.
