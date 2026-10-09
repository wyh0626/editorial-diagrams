"""Contract and compatibility checks for the open scene interface."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1] / "skills" / "editorial-diagrams"
spec = importlib.util.spec_from_file_location("renderer", SKILL / "scripts" / "render.py")
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class SceneContract(unittest.TestCase):
    def setUp(self):
        self.data = dict(locale="en", kicker="Study", title="An original composition",
                         intro="Explain a relationship.", width=600, height=300)
        self.markup = '<svg viewBox="0 0 600 300"><path id="__ID__-curve" d="M0 0 C100 80 300 80 400 0"/><circle cx="80" cy="80" r="40"/><circle cx="90" cy="80" r="40"/></svg>'

    def test_arbitrary_geometry_without_graph_fields(self):
        page = renderer.render(self.data, instance="study", scene_markup=self.markup)
        self.assertIn('id="study-curve"', page)
        self.assertIn('C100 80', page)
        self.assertNotIn('data-node=', page)

    def test_static_scene_has_no_control(self):
        self.data["animated"] = False
        self.data["legend"] = []
        page = renderer.render(self.data, scene_markup=self.markup)
        self.assertNotIn('<button', page)
        self.assertNotIn('<ul class="ed-legend"', page)
        self.assertIn('data-animated="false"', page)

    def test_multiple_fragments_scope_styles_ids_and_scripts(self):
        fragments = [renderer.render(self.data, fragment=True, instance=id,
                     scene_markup=self.markup, scene_style="__ROOT__ .x {color:var(--ed-ink)}",
                     scene_script="root.dataset.owner = '__ID__';") for id in ("first", "second")]
        for id, page in zip(("first", "second"), fragments):
            self.assertIn(f'#{id} .x', page)
            self.assertIn(f'const root = document.getElementById("{id}")', page)
            self.assertNotIn('__ID__', page)
            self.assertNotIn('__ROOT__', page)
            self.assertNotIn('<html', page)

    def test_localized_controls_and_escaped_metadata(self):
        self.data.update(locale="zh-Hans", title='<script>title</script>',
                         ui=dict(play="播放", pause="暂停", playAnimation='播放 "动画"',
                                 pauseAnimation="暂停动画", legend="图例", scrollHint="横向滚动"))
        page = renderer.render(self.data, scene_markup=self.markup)
        self.assertIn('lang="zh-Hans"', page)
        self.assertIn('播放 &quot;动画&quot;', page)
        self.assertIn('&lt;script&gt;title&lt;/script&gt;', page)
        del self.data["ui"]["legend"]
        with self.assertRaises(ValueError):
            renderer.render(self.data, scene_markup=self.markup)

    def test_custom_legend_and_invalid_color(self):
        self.data["legend"] = [dict(label="Occupancy", shape="line", color="#abc")]
        self.assertIn('ed-mark-line', renderer.render(self.data, scene_markup=self.markup))
        self.data["legend"][0]["color"] = 'red;position:fixed'
        with self.assertRaises(ValueError):
            renderer.render(self.data, scene_markup=self.markup)

    def test_inline_script_does_not_terminate_at_authored_string(self):
        page = renderer.render(self.data, scene_markup=self.markup,
                               scene_script='root.dataset.example = "</script>";')
        self.assertEqual(page.count('</script>'), 1)
        self.assertIn('"<\\/script>"', page)

    def test_scene_files_resolve_relative_to_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / 'figure.json').write_text(json.dumps(dict(self.data, scene=dict(markup='custom.svg'))))
            (base / 'custom.svg').write_text(self.markup)
            output = base / 'nested' / 'figure.html'
            result = subprocess.run([sys.executable, str(SKILL / 'scripts' / 'render.py'),
                                     '--data', str(base / 'figure.json'), '--output', str(output)],
                                    cwd='/', capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('C100 80', output.read_text())
            (base / 'custom.svg').unlink()
            result = subprocess.run([sys.executable, str(SKILL / 'scripts' / 'render.py'),
                                     '--data', str(base / 'figure.json'), '--output', str(output)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('Invalid figure:', result.stderr)
            self.assertNotIn('Traceback', result.stderr)

    def test_scene_rejects_whole_document(self):
        with self.assertRaises(ValueError):
            renderer.render(self.data, scene_markup='<!doctype html><html><body>bad</body></html>')

    def test_existing_graphs_and_their_geometry_checks_survive(self):
        examples = list((SKILL / 'examples').glob('*.json'))
        self.assertEqual(len(examples), 6)
        for file in examples:
            data = json.loads(file.read_text())
            with self.subTest(file=file.name):
                self.assertIn('data-node=', renderer.render(data))
        bad = copy.deepcopy(json.loads(examples[0].read_text()))
        bad['nodes'][1].update({key: bad['nodes'][0][key] for key in ('x', 'y', 'w', 'h')})
        with self.assertRaisesRegex(ValueError, 'Overlapping nodes'):
            renderer.render(bad)


if __name__ == '__main__':
    unittest.main()
