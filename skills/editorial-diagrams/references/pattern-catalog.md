# Blog case library

The reference article has six figures in five families. Select one by the explanatory task, then adapt its data. These are implemented compositions, not merely examples of visual inspiration.

## Selection map

| Pattern | Source | Keep this structure | Suitable requests |
|---|---|---|---|
| `architecture` | 01 | Client column, central platform with capability grid, resource column, optional change-capture fan-out | Platform boundaries, shared responsibilities, dependencies |
| `request-flow` | 02 | Client, ingress, parallel service instances, egress, downstream accounts; directed request/response rails | Request routing, service decomposition, proxy hops |
| `timeline-comparison` | 03 | Two scenarios on the same scale, one execution-thread track plus request tracks, I/O-ready markers and blocked intervals | Event-loop delay, concurrency versus serialized CPU work, scheduling bottlenecks |
| `pool-reuse` / `lifo` | 04A | Ordered returned-connection pills, three server columns, moving requests, server work and assignment history | Last-returned resource selection and its feedback on slow servers |
| `pool-reuse` / `fifo` | 04B | Same initial work, layout and arrivals as LIFO; select the other end of the returned queue | Policy comparison, oldest-returned resource selection |
| `connection-aggregation` | 05 | Three vertically stacked scenarios; same clients and storage, local pools / shared pool / multiplexed connection | Retained connections, pooling, multiplexing, same load with different connection counts |

Prefer the main explanatory relationship over surface nouns. Do not use an architecture graph to explain queue selection, or a time chart to compare retained connections. For combined topics, separate suitable cases into figures with consistent labels.

## Common configuration

Copy a matching file from `examples/blog/`, then edit it in the task workspace:

```json
{
  "pattern": "pool-reuse",
  "locale": "en",
  "kicker": "Figure 01",
  "title": "What this case explains",
  "intro": "State the scenario and assumptions.",
  "legend": [],
  "model": {"policy": "fifo"},
  "content": {"labels": {}},
  "notes": ["Illustrative model; not a benchmark."]
}
```

Pattern dimensions are computed. Do not supply `width` or `height`. Keep the automatically selected cycle duration unless deliberately adjusting playback. `animated: false` yields a static meaningful state without playback controls. `initialTime` selects a playback starting point; `?time=` overrides it. Aggregation starts at a steady state by default and replay starts at zero.

Use the common locale/UI contract in [scene-format.md](scene-format.md), including `ui.replay` when replay is present. English internal labels have defaults; other languages require the pattern's complete `content.labels` set. The bundled JSON files list those keys.

## 01 — Platform architecture

Example: `examples/blog/01-architecture.json`.

`content`: `clients`, `platform`, `features`, optional `routing`, `resources`, optional `changeService` and `consumers`. Participants are strings or `{title, subtitle}` objects. Up to eight clients/resources, nine capabilities and six consumers are supported. The routing capability spans the platform width; capabilities are parallel responsibilities, not a processing sequence. Omit consumers to remove the change-capture branch.

Use for what exists and how it depends on other components. Use request flow for the stages traversed by an operation instead.

## 02 — Branched request path

Example: `examples/blog/02-request-flow.json`.

`content`: `client`, `ingress`, `workers`, `egress`, `resources`. One to five workers/resources are supported. Participants are strings or `{title, subtitle}` objects. Desktop uses the article's horizontal path with an enclosing service group; phones use a separate vertical layout with branch rails. SVG markers indicate direction only.

Use parallel workers for alternatives, not an asserted sequence. A request traverses one applicable branch; moving markers do not establish latency, routing probability or packet counts.

## 03 — Paired CPU / I/O timelines

Example: `examples/blog/03-timeline.json`.

`content.scenarios`: exactly two `{title, subtitle}` objects.

`model`: `cpu` (two positive durations), `requests` (1–6), `wait` (I/O duration), `network` (read/write thread time), `scale` (shared axis maximum). The model runs one FIFO ready queue. Each request performs CPU work, network write, I/O wait, network read and CPU response work. I/O completion queues a continuation; it cannot preempt work on the thread.

The default parameters finish at 11.6 and 38.4 illustrative units. Every request waits six units for I/O in both scenarios. These are model outcomes, not runtime measurements. A vertical mark identifies I/O readiness; a bordered interval shows readiness waiting for the thread. One playback second advances two model units. `?time=8` shows unit 16. The range input seeks and pauses.

This supplied scheduler is for the article's event-loop explanation. Do not relabel it as a measured distributed trace or a general-purpose CPU scheduler without changing the model.

## 04A / 04B — Returned connection reuse

Examples: `examples/blog/04a-pool-lifo.json`, `04b-pool-fifo.json`.

`model`: `policy` (`lifo` or `fifo`), optional three `servers` (`{id, service}`), `connectionsPerServer` (1–4), sorted `arrivals` (1–30 model-millisecond times), `transfer` (each one-way transit duration).

The initial burst consumes every connection. Each server serializes its work independently. Connections return after response transit and enter an ordered deque. LIFO selects the most recent return; FIFO selects the earliest. Pills show available connections, rectangles show server work, and the history records subsequent assignments.

The defaults use 150 ms transit, A/B work of 100 ms, C work of 1200 ms, and eighteen subsequent arrivals at `1600 + 600*i`. Both policies share these values. Subsequent assignments are A/B/C = 9/0/9 for LIFO and 7/7/4 for FIFO. Outcome inspection occurs just after the final assignment while some work is still pending; it does not imply every request has finished.

Playback is slowed sixfold: `?time=26.4` shows model millisecond 4400. Phase buttons seek and pause at initial burst, reuse and outcome. Replay resets the model. The three-server composition follows the source case; for a different number, adapt a scene from this structure and verify its model and layout.

## 05 — Connection aggregation

Example: `examples/blog/05-aggregation.json`.

`content`: `proxy`, `storage`, three `scenarios` (`{title, subtitle, protocol?}`), and localized labels.

`model`: `pods` (2–8), `peakPerPod` (1–4), `concurrent` (1 to total local capacity). The illustrative workload starts one request per second; its round trip lasts `concurrent` seconds. Requests visit clients in groups of `peakPerPod`, allowing every local pool to reach its peak. Retained local connections never disappear merely because they become idle.

All three panels show the same active requests. Local pools retain each client's peak; the shared HTTP/1 pool retains the aggregate concurrency peak; HTTP/2 carries the workload on one connection using independent streams. Dashed rails are idle, solid rails are busy, blue squares travel outbound and outlined circles return. Default steady counts are 18 / 6 / 1 with six concurrent requests in each panel.

The scene starts at playback second 40. Replay rebuilds from zero; `?time=0` or `?time=10` inspect startup. This is a finite illustrative workload model, not a claim that every deployment always needs these connection counts. Flow control, limits, reconnection and protocol costs are outside the model.

## Fidelity and adaptation

Keep the selected case's layout vocabulary, comparison conditions and behavior. Change labels and supported parameters first. If more participants or different behavior require a scene adaptation, reuse the case structure rather than defaulting to a new chart style.

The public package uses original code and system fonts. Reference article geometry and semantics inform the design; original website DOM, JavaScript, icons and font bytes are not distributed. Verify desktop/narrow layout, label fit, controls and meaningful model states. Do not claim pixel identity or general performance guarantees from a schematic example.
