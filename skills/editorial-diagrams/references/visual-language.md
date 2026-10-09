# Shared visual language

Select a composition from [pattern-catalog.md](pattern-catalog.md), then adapt its content. Shared visual decisions hold the case library together; each source figure has its own layout vocabulary.

## Shared decisions

- White paper, near-black ink, subtle neutral gray for secondary information.
- Thin 1px structural strokes. Use small 4px radii for bounded regions when rounded corners are appropriate.
- Restrained accent colors. The theme exposes blue, green and purple; assign semantic roles within each figure and explain them when useful.
- System sans-serif for main labels and headings; a small monospace face for identifiers, scales and secondary annotations.
- A clear editorial hierarchy: figure label, heading, concise explanation, figure, and assumptions or sources. Legends and playback controls are conditional on what the figure needs.
- Calm spacing and intentional alignment. Repeat dimensions for comparable objects; use differences in size only when they convey a meaningful distinction.
- A subtle 5px dot grid is available behind the scene. It must not compete with the data or dictate the geometry.

The implementation exposes these CSS variables within `.ed-root`:

| Token | Default |
|---|---|
| `--ed-paper` | `#fff` |
| `--ed-ink` | `#141414` |
| `--ed-muted` | `#666` |
| `--ed-rule` | `#d9d9d9` |
| `--ed-stroke` | `1px` |
| `--ed-radius` | `4px` |
| `--ed-blue` | `#70a0ff` |
| `--ed-green` | `#9ae8c5` |
| `--ed-purple` | `#bb8ae8` |
| `--ed-sans`, `--ed-mono` | System font stacks |

Assign accents to meanings within each figure. The legacy aliases `--ed-request`, `--ed-response` and `--ed-change` point to blue, green and purple for graph compatibility; custom scenes should prefer the neutral color tokens.

## Decisions that belong to each figure

Within the selected case, preserve the visual roles of position, area, repetition, order, grouping, connectors and time. An ordered row can preserve sequence; a scale can encode a quantity; a repeated mark can count objects; containment can show ownership. Combine these when necessary. Use the encodings of the selected blog case.

Use each case's vocabulary: architecture cards and branches, aligned timeline tracks, returned-resource pills and server work, or repeated connection rails. Adapt these when necessary; do not replace a suitable case with an unrelated chart metaphor.

Prefer the smallest visual vocabulary that makes the important relationship evident. Make equivalent objects look equivalent. A change in geometry or color should carry meaning or improve reading, rather than decorate the page.

## Motion

Motion should reveal a changing state or relationship. Derive all related positions, counts and labels from the same time or state model. Keep relevant invariants intact and make paused states readable. Document illustrative timings and avoid apparent measurements when no measurements exist.

Use reduced motion, visibility pausing and the common clock. Keep meaningful transitions deliberate; independent flow markers are appropriate only when the explanation is about direction rather than allocation, ordering or a changing count.
