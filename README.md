# Editorial Diagrams

English | [简体中文](README.zh-CN.md)

An agent skill that selects and adapts engineering-blog diagram cases from a plain-language request. Six figures from [OpenAI's storage engineering article](https://openai.com/zh-Hans-CN/index/scaling-storage-one-billion-users-part-one/) form five reusable composition families. The agent chooses the case for the explanation, then adapts its participants, labels and model.

## Case library

| What the reader needs to understand | Selected composition | Article figure |
| --- | --- | --- |
| Components, responsibilities and dependencies | Platform architecture | 01 |
| The route of one operation through components | Branched request flow | 02 |
| Time spent working, waiting and blocked | Paired timelines on one scale | 03 |
| Return order, resource selection and resulting load | Connection-pool reuse, LIFO / FIFO | 04A / 04B |
| Fewer connections for the same upstream workload | Three stacked aggregation scenarios | 05 |

The user describes the idea; the agent chooses the case. For example, explaining where a request travels selects Figure 02, explaining why a ready response waits selects Figure 03, and explaining multiplexing's connection savings selects Figure 05. A request that mentions “connections” does not automatically become a flowchart.

| | |
| --- | --- |
| [![Platform architecture](docs/images/blog-01-architecture.jpg)](skills/editorial-diagrams/examples/blog/01-architecture.json) | [![Request flow](docs/images/blog-02-request-flow.jpg)](skills/editorial-diagrams/examples/blog/02-request-flow.json) |
| Figure 01 · Platform architecture | Figure 02 · Request flow |
| [![Paired timelines](docs/images/blog-03-timeline.jpg)](skills/editorial-diagrams/examples/blog/03-timeline.json) | [![Connection aggregation](docs/images/blog-05-aggregation.jpg)](skills/editorial-diagrams/examples/blog/05-aggregation.json) |
| Figure 03 · Thread scheduling and readiness | Figure 05 · Local pools, shared pool, multiplexing |
| [![LIFO pool reuse](docs/images/blog-04a-pool-lifo.jpg)](skills/editorial-diagrams/examples/blog/04a-pool-lifo.json) | [![FIFO pool reuse](docs/images/blog-04b-pool-fifo.jpg)](skills/editorial-diagrams/examples/blog/04b-pool-fifo.json) |
| Figure 04A · Most recently returned first | Figure 04B · Earliest returned first |

These previews use original implementations and system fonts. They follow the article's compositions and illustrative behavior; they are not pixel-identical copies of the website.

## Install

With [skills.sh](https://skills.sh):

```bash
npx skills add wyh0626/editorial-diagrams
```

Or install globally for a specific agent:

```bash
npx skills add wyh0626/editorial-diagrams -g -a claude-code
npx skills add wyh0626/editorial-diagrams -g -a codex
```

Manual install: copy [`skills/editorial-diagrams`](skills/editorial-diagrams) into your agent's skills directory, such as `~/.claude/skills/editorial-diagrams` or `~/.codex/skills/editorial-diagrams`.

## Use

```text
Use editorial-diagrams to explain why ready responses wait when an event-loop thread spends too long processing CPU work.
```

```text
Use editorial-diagrams to compare independent connection pools, a shared proxy pool and multiplexing under the same workload.
```

The agent selects the closest case, copies its editable JSON, adjusts the content and parameters, renders it and inspects it in a browser. It should preserve the selected case's defining structure. Custom scene authoring remains available when the parameters cannot express a necessary adaptation.

Generated headings, legends, buttons, internal labels and accessible names follow the requested language or the conversation language. The skill and authoring references are in English.

Deliverables are an editable `diagram.json`, self-contained `diagram.html`, and an optional browser preview. The page requires no external fonts, libraries or network requests. Additional scene files are only needed for custom adaptations.

## Render a case

Python 3.8+ is the only requirement:

```bash
python3 skills/editorial-diagrams/scripts/render.py --data skills/editorial-diagrams/examples/blog/05-aggregation.json --output out/aggregation.html
```

Set `pattern`, `content` and applicable `model` parameters in the JSON. The renderer computes geometry. Pool policies share identical arrivals and server work; timelines share one scale; aggregation panels share the same upstream workload.

- `--instance <id>` sets a stable root ID; `--fragment` emits an embeddable fragment.
- `animated: false` renders a static figure. Dynamic cases support pause/resume, reduced motion and visibility handling. Timelines and pool reuse add seeking; aggregation opens at a steady state and can replay from zero.
- `?time=...&check=1` freezes a repeatable state and reports label overflow. Playback seconds and model time are documented per case.
- Request flow has a vertical phone layout. Pool reuse compacts its columns. Architecture, timelines and aggregation preserve geometry with horizontal scrolling.

Read the [case catalog and parameters](skills/editorial-diagrams/references/pattern-catalog.md), [visual language](skills/editorial-diagrams/references/visual-language.md), [custom scene interface](skills/editorial-diagrams/references/scene-format.md) and [graph interface](skills/editorial-diagrams/references/graph-format.md).

## Development

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/playback.test.cjs
```

Tests cover rendering and localization contracts, scheduling, pool conservation and allocation, responsive geometry, and the shared playback clock. Browser checks remain necessary for appearance, text fit and interaction. Timings and counts are illustrative, not measured performance guarantees.

The earlier graph examples remain under `examples/`. An additional community example is the [Codex CLI architecture](https://codex-architecture-site.vercel.app/) drawn from the public `openai/codex` source tree.

## License and provenance

[MIT](LICENSE). This is an independent community project, unaffiliated with and not endorsed by OpenAI. The case library is studied from the linked article and implemented in original SVG/HTML/CSS/JavaScript. It contains no extracted website code, proprietary fonts or brand assets.
