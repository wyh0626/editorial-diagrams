#!/usr/bin/env python3
"""Build a self-contained editorial illustration from graph or authored scene input.

SPDX-License-Identifier: MIT
"""
import argparse
import html
import importlib.util
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit
import uuid

ASSETS = Path(__file__).resolve().parent.parent / "assets"
KINDS = {"request": 8, "response": 9, "change": 7}
ICONS = json.loads((ASSETS / "icons.json").read_text(encoding="utf-8"))
DEFAULT_UI = {
    "play": "Play",
    "pause": "Pause",
    "playAnimation": "Play animation",
    "pauseAnimation": "Pause animation",
    "legend": "Legend",
    "scrollHint": "Scroll horizontally to explore the diagram",
}


def escape(value):
    return html.escape(str(value), quote=True)


def number(value, label, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    if positive and value <= 0:
        raise ValueError(f"{label} must be positive")
    return value


def text(value, label):
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")


def rectangle(item, width, height):
    for key in ("x", "y", "w", "h"):
        number(item[key], f"{item['id']}.{key}", positive=key in ("w", "h"))
    if not (0 <= item["x"] and 0 <= item["y"] and item["x"] + item["w"] <= width
            and item["y"] + item["h"] <= height):
        raise ValueError(f"Outside board: {item['id']}")


def on_boundary(point, node):
    px, py = point
    x, y, w, h = (node[key] for key in ("x", "y", "w", "h"))
    return ((abs(px-x) < .01 or abs(px-x-w) < .01) and y <= py <= y+h
            or (abs(py-y) < .01 or abs(py-y-h) < .01) and x <= px <= x+w)


def unique(items, label):
    ids = []
    for item in items:
        text(item["id"], f"{label} ID")
        if not item["id"]:
            raise ValueError(f"Empty {label} ID")
        ids.append(item["id"])
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate {label} ID")


def validate_frame(data):
    locale = data.get("locale", "en")
    if not isinstance(locale, str) or not re.fullmatch(r"[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*", locale):
        raise ValueError("locale must be a language tag such as en, es or zh-Hans")
    if data.get("direction", "ltr") not in ("ltr", "rtl"):
        raise ValueError("direction must be ltr or rtl")
    if "ui" in data:
        if not isinstance(data["ui"], dict):
            raise ValueError("ui must be an object containing all UI labels")
        for key in DEFAULT_UI:
            value = data["ui"].get(key)
            text(value, f"ui.{key}")
            if not value.strip():
                raise ValueError(f"ui.{key} must not be empty")
    elif locale.split("-")[0].lower() != "en":
        raise ValueError("Non-English diagrams require all translated labels in ui")
    number(data["width"], "width", positive=True)
    number(data["height"], "height", positive=True)
    for key in ("kicker", "title", "intro"):
        text(data[key], key)
    if "animated" in data and not isinstance(data["animated"], bool):
        raise ValueError("animated must be a boolean")
    number(data.get("duration", 8), "duration", positive=True)
    initial = number(data.get("initialTime", 0), "initialTime")
    if initial < 0:
        raise ValueError("initialTime must be nonnegative")
    if data.get("replay") and locale.split("-")[0].lower() != "en":
        text(data.get("ui", {}).get("replay"), "ui.replay")
        if not data["ui"]["replay"].strip():
            raise ValueError("ui.replay must not be empty")
    for item in data.get("legend", []):
        text(item["label"], "legend label")
        if "kind" in item:
            if item["kind"] not in KINDS:
                raise ValueError("Unknown legend kind")
        else:
            if item.get("shape") not in ("square", "circle", "diamond", "line"):
                raise ValueError("Unknown legend mark shape")
            color = item.get("color", "")
            if not isinstance(color, str) or not re.fullmatch(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?", color):
                raise ValueError("Legend color must be a hexadecimal RGB color")
    for note in data.get("notes", []):
        text(note, "note")
    for source in data.get("sources", []):
        text(source["title"], "source title")
        parsed = urlsplit(source["url"])
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("Source links must be HTTP or HTTPS URLs")
    return data


def validate(data):
    validate_frame(data)
    width, height = data["width"], data["height"]
    if not data["nodes"]:
        raise ValueError("A graph must contain at least one node")
    for key in ("nodes", "edges", "groups"):
        unique(data.get(key, []), key)
    groups = {g["id"]: g for g in data.get("groups", [])}
    for group in groups.values():
        rectangle(group, width, height)
        text(group["title"], "group title")
    nodes = {n["id"]: n for n in data["nodes"]}
    for node in nodes.values():
        rectangle(node, width, height)
        text(node["title"], "node title")
        text(node.get("subtitle", ""), "node subtitle")
        if node.get("group") and node["group"] not in groups:
            raise ValueError(f"Unknown group for node {node['id']}")
        if node.get("icon", "service") not in ICONS:
            raise ValueError(f"Unknown icon for node {node['id']}")
        if node.get("features"):
            if node.get("featureColumns", 2 if len(node["features"]) <= 4 else 3) not in (2, 3):
                raise ValueError("featureColumns must be 2 or 3")
            for feature in node["features"]:
                text(feature["title"], "feature title")
                text(feature["description"], "feature description")
    boxes = list(nodes.values())
    for i, a in enumerate(boxes):
        for b in boxes[i+1:]:
            if (max(a["x"], b["x"]) < min(a["x"]+a["w"], b["x"]+b["w"])
                    and max(a["y"], b["y"]) < min(a["y"]+a["h"], b["y"]+b["h"])):
                raise ValueError(f"Overlapping nodes: {a['id']}, {b['id']}")
    for edge in data["edges"]:
        if edge["from"] not in nodes or edge["to"] not in nodes:
            raise ValueError(f"Unknown endpoint: {edge['id']}")
        if edge["kind"] not in KINDS:
            raise ValueError(f"Unknown edge kind: {edge['id']}")
        number(edge.get("duration", KINDS[edge["kind"]]), "duration", positive=True)
        number(edge.get("begin", 0), "begin")
        if edge.get("reverse"):
            raise ValueError("Use points ordered from the actual source to destination")
        if edge.get("label"):
            text(edge["label"], "edge label")
            number(edge["labelX"], "labelX")
            number(edge["labelY"], "labelY")
        points = edge["points"]
        if len(points) < 2:
            raise ValueError(f"Too few path points: {edge['id']}")
        for point in points:
            if len(point) != 2:
                raise ValueError("Each path point must have two coordinates")
            px, py = (number(v, "path coordinate") for v in point)
            if not (0 <= px <= width and 0 <= py <= height):
                raise ValueError(f"Path outside board: {edge['id']}")
        if not on_boundary(points[0], nodes[edge["from"]]) or not on_boundary(points[-1], nodes[edge["to"]]):
            raise ValueError(f"Disconnected endpoint: {edge['id']}")
        for a, b in zip(points, points[1:]):
            if a == b or (a[0] != b[0] and a[1] != b[1]):
                raise ValueError(f"Path must have nonzero orthogonal segments: {edge['id']}")
            for node in nodes.values():
                if node["id"] in (edge["from"], edge["to"]):
                    continue
                x, y, w, h = (node[k] for k in ("x", "y", "w", "h"))
                vertical = a[0] == b[0] and x < a[0] < x+w and max(min(a[1], b[1]), y) < min(max(a[1], b[1]), y+h)
                horizontal = a[1] == b[1] and y < a[1] < y+h and max(min(a[0], b[0]), x) < min(max(a[0], b[0]), x+w)
                if vertical or horizontal:
                    raise ValueError(f"Edge {edge['id']} crosses node {node['id']}")
    return data


def rounded_path(points, radius=8):
    path = [f"M{points[0][0]:g} {points[0][1]:g}"]
    for previous, current, following in zip(points, points[1:], points[2:]):
        incoming = math.dist(previous, current)
        outgoing = math.dist(current, following)
        if (previous[0]-current[0])*(following[1]-current[1]) == (previous[1]-current[1])*(following[0]-current[0]):
            path.append(f"L{current[0]:g} {current[1]:g}")
            continue
        r = min(radius, incoming/2, outgoing/2)
        start = [current[j]+(previous[j]-current[j])*r/incoming for j in (0, 1)]
        end = [current[j]+(following[j]-current[j])*r/outgoing for j in (0, 1)]
        path.append(f"L{start[0]:g} {start[1]:g}Q{current[0]:g} {current[1]:g} {end[0]:g} {end[1]:g}")
    path.append(f"L{points[-1][0]:g} {points[-1][1]:g}")
    return "".join(path)


def box_style(item):
    return ";".join(f"{name}:{item[key]:g}px" for name, key in (("left", "x"), ("top", "y"), ("width", "w"), ("height", "h")))


def graph_content(data, root):
    width, height = data["width"], data["height"]
    parts = []
    for g in data.get("groups", []):
        parts.append(f'<section class="ed-group" style="{box_style(g)}" aria-label="{escape(g["title"])}"><h3 class="ed-group-title">{escape(g["title"])}</h3></section>')
    rails, labels, moving = [], [], []
    for edge in data["edges"]:
        path = rounded_path(edge["points"])
        rails.append(f'<path data-edge="{escape(edge["id"])}" d="{path}" marker-end="url(#{root}-arrow)"/>')
        if edge.get("label"):
            labels.append(f'<span class="ed-edge-label" style="left:{edge["labelX"]:g}px;top:{edge["labelY"]:g}px">{escape(edge["label"])}</span>')
        duration = edge.get("duration", KINDS[edge["kind"]])
        shape = {"request": '<rect x="-4" y="-4" width="8" height="8" rx="1"/>',
                 "response": '<circle r="4"/>',
                 "change": '<path d="M0-5 5 0 0 5-5 0Z"/>'}[edge["kind"]]
        for phase in (0, .5):
            begin = edge.get("begin", 0) - phase * duration
            moving.append(f'<g class="ed-motion-{edge["kind"]}" opacity="0">{shape}<animateMotion path="{path}" dur="{duration:g}s" begin="{begin:g}s" repeatCount="indefinite" calcMode="linear"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.03;.97;1" dur="{duration:g}s" begin="{begin:g}s" repeatCount="indefinite"/></g>')
    parts.append(f'<svg class="ed-rails" viewBox="0 0 {width:g} {height:g}" aria-hidden="true"><defs><marker id="{root}-arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" orient="auto" markerUnits="userSpaceOnUse"><path d="M2 1 7 4 2 7" fill="none" stroke="#141414" stroke-width="1"/></marker></defs>{"".join(rails)}</svg>')
    for node in data["nodes"]:
        capabilities = bool(node.get("features"))
        parts.append(f'<article class="ed-node{" ed-capabilities" if capabilities else ""}" data-node="{escape(node["id"])}" style="{box_style(node)}" aria-label="{escape(node["title"])}">')
        if capabilities:
            columns = node.get("featureColumns", 2 if len(node["features"]) <= 4 else 3)
            parts.append(f'<h3 class="ed-node-title">{escape(node["title"])}</h3><div class="ed-features" style="--ed-columns:{columns}">')
            for f in node["features"]:
                parts.append(f'<div class="ed-feature"><span class="ed-feature-title">{escape(f["title"])}</span><span class="ed-feature-description">{escape(f["description"])}</span></div>')
            parts.append('</div>')
        else:
            icon = ICONS[node.get("icon", "service")]
            parts.append(f'<span class="ed-node-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">{icon}</svg></span><div class="ed-node-copy"><h3 class="ed-node-title">{escape(node["title"])}</h3><p class="ed-node-subtitle">{escape(node.get("subtitle", ""))}</p></div>')
        parts.append('</article>')
    parts.append(f'<svg class="ed-motion" viewBox="0 0 {width:g} {height:g}" aria-hidden="true">{"".join(moving)}</svg>{"".join(labels)}')
    return "".join(parts)


def load_scene(data, base_dir):
    scene = data.get("scene")
    if not isinstance(scene, dict):
        raise ValueError("scene must be an object with a markup file path")
    result = {}
    for key in ("markup", "style", "script"):
        path = scene.get(key)
        if path is None and key != "markup":
            result[key] = ""
            continue
        if not isinstance(path, str) or not path.strip():
            raise ValueError(f"scene.{key} must be a non-empty local file path")
        result[key] = (Path(base_dir) / path).read_text(encoding="utf-8")
    return result


def legend_markup(items):
    marks = {"request": "square", "response": "circle", "change": "diamond"}
    colors = {"request": "var(--ed-request)", "response": "var(--ed-response)", "change": "var(--ed-change)"}
    result = []
    for item in items:
        kind = item.get("kind")
        shape = marks[kind] if kind else item["shape"]
        color = colors[kind] if kind else item["color"]
        result.append(f'<li><span class="ed-key ed-mark-{shape}" style="--ed-mark-color:{color}" aria-hidden="true"></span>{escape(item["label"])}</li>')
    return "".join(result)


def render(data, *, fragment=False, instance=None, scene_markup=None, scene_style="", scene_script=""):
    if "pattern" in data:
        if "scene" in data or "nodes" in data or scene_markup is not None:
            raise ValueError("Use pattern, graph or scene input separately")
        spec = importlib.util.spec_from_file_location("editorial_patterns", Path(__file__).with_name("patterns.py"))
        patterns = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(patterns)
        built = patterns.build(data)
        data = dict(data)
        for key in ("width", "height", "replay", "duration", "initialTime"):
            if key in built:
                data.setdefault(key, built[key])
        if data["width"] != built["width"] or data["height"] != built["height"]:
            raise ValueError("Pattern dimensions are computed; adjust content or model instead")
        scene_markup, scene_style, scene_script = built["markup"], built["style"], built["script"]
    is_scene = "scene" in data or scene_markup is not None
    if is_scene:
        validate_frame(data)
        if not isinstance(scene_markup, str) or not scene_markup.strip():
            raise ValueError("Load scene markup before rendering, or use the CLI")
        if re.search(r"<!doctype|</?(?:html|head|body)(?:\s|>)", scene_markup, re.I):
            raise ValueError("Scene markup must be a body fragment, not a document")
    else:
        validate(data)
    root = instance or "ed-" + uuid.uuid4().hex[:12]
    if not re.fullmatch(r"[a-z][a-z0-9-]*", root):
        raise ValueError("Instance must start with a lowercase letter and use letters, digits or hyphens")
    width, height = data["width"], data["height"]
    locale, direction = data.get("locale", "en"), data.get("direction", "ltr")
    ui = data.get("ui", DEFAULT_UI)
    animated = data.get("animated", True)
    duration = data.get("duration", 8)
    css = (ASSETS / "diagram.css").read_text(encoding="utf-8").replace(".ed-root", "#" + root)
    css += f"\n#{root}{{max-width:{width+2:g}px;margin-inline:auto}}"
    if is_scene:
        css += "\n" + scene_style.replace("__ROOT__", "#" + root).replace("__ID__", root)
        content = '<div class="ed-scene">' + scene_markup.replace("__ID__", root) + '</div>'
    else:
        content = graph_content(data, root)
    parts = [f'<div id="{root}" class="ed-root" lang="{escape(locale)}" dir="{direction}" data-animated="{str(animated).lower()}" data-duration="{duration:g}" data-initial-time="{data.get("initialTime", 0):g}"><figure aria-label="{escape(data["title"])}">',
             '<figcaption class="ed-header"><div class="ed-copy">',
             f'<p class="ed-kicker">{escape(data["kicker"])}</p><h2 class="ed-heading">{escape(data["title"])}</h2>',
             f'<p class="ed-intro">{escape(data["intro"])}</p></div>']
    if animated:
        parts.append('<div class="ed-actions">')
        if data.get("replay"):
            replay = ui.get("replay", "Replay")
            parts.append(f'<button type="button" class="ed-control ed-replay" data-ed-replay aria-label="{escape(replay)}"><svg viewBox="0 0 14 14" aria-hidden="true"><path d="M11 5a5 5 0 1 0 0 5M11 1v4H7" fill="none" stroke="currentColor"/></svg><span>{escape(replay)}</span></button>')
        parts.extend([
            f'<button type="button" class="ed-control" aria-label="{escape(ui["pauseAnimation"])}" aria-controls="{root}-board" aria-pressed="true" data-play-label="{escape(ui["play"])}" data-pause-label="{escape(ui["pause"])}" data-play-description="{escape(ui["playAnimation"])}" data-pause-description="{escape(ui["pauseAnimation"])}">',
            '<svg data-play hidden viewBox="0 0 14 14" aria-hidden="true"><path d="M3 2 12 7 3 12Z" fill="none" stroke="currentColor"/></svg>',
            '<svg data-pause viewBox="0 0 14 14" aria-hidden="true"><path d="M4 3v8M10 3v8" stroke="currentColor" stroke-width="2"/></svg>',
            f'<span data-caption>{escape(ui["pause"])}</span></button></div>'])
    parts.append('</figcaption>')
    if data.get("legend"):
        parts.append(f'<ul class="ed-legend" aria-label="{escape(ui["legend"])}">{legend_markup(data["legend"])}</ul>')
    parts.append(f'<div class="ed-viewport" role="region" tabindex="0" aria-label="{escape(data["title"] + "; " + ui["scrollHint"])}"><div id="{root}-board" class="ed-board" style="width:{width:g}px;height:{height:g}px">{content}</div></div>')
    if data.get("notes") or data.get("sources"):
        parts.append('<footer class="ed-notes">')
        parts.extend(f'<p>{escape(note)}</p>' for note in data.get("notes", []))
        if data.get("sources"):
            parts.append('<p>' + ''.join(f'<a href="{escape(s["url"])}" rel="noreferrer">{escape(s["title"])}</a>' for s in data["sources"]) + '</p>')
        parts.append('</footer>')
    parts.append('</figure></div>')
    runtime = (ASSETS / "playback.js").read_text(encoding="utf-8").replace("__DIAGRAM_ID__", json.dumps(root))
    if is_scene and scene_script:
        authored = scene_script.replace("__ID__", root)
        runtime = "(() => { const root = document.getElementById(" + json.dumps(root) + ");\n" + authored + "\n})();\n" + runtime
    runtime = re.sub(r"</script", lambda match: "<\\/script", runtime, flags=re.I)
    result = f'<style>{css}</style>{"".join(parts)}<script>{runtime}</script>'
    if fragment:
        return result
    return (f'<!doctype html><html lang="{escape(locale)}" dir="{direction}"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="color-scheme" content="light">'
            f'<title>{escape(data["title"])}</title><style>body{{margin:0;background:#fff}}</style>'
            '</head><body>' + result + '</body></html>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--instance")
    parser.add_argument("--fragment", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.data.read_text(encoding="utf-8"))
        scene = load_scene(data, args.data.parent) if "scene" in data else None
        result = render(data, fragment=args.fragment, instance=args.instance,
                        scene_markup=scene["markup"] if scene else None,
                        scene_style=scene["style"] if scene else "",
                        scene_script=scene["script"] if scene else "")
    except KeyError as exc:
        parser.exit(2, f"Invalid figure: missing field {exc}\n")
    except (ValueError, TypeError, OSError) as exc:
        parser.exit(2, f"Invalid figure: {exc}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    print(f"Wrote {args.output} ({len(result.encode('utf-8'))} bytes)")


if __name__ == "__main__":
    main()
