import copy
import importlib.util
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

SKILL = Path(__file__).resolve().parents[1] / 'skills/editorial-diagrams'


def module(name):
    spec = importlib.util.spec_from_file_location(name, SKILL / 'scripts' / (name+'.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


patterns, renderer = module('patterns'), module('render')


class BlogPatterns(unittest.TestCase):
    def example(self, name):
        return json.loads((SKILL / 'examples/blog' / (name+'.json')).read_text())

    def test_all_six_article_cases_render_from_parameters(self):
        files = list((SKILL / 'examples/blog').glob('*.json'))
        self.assertEqual(len(files), 6)
        self.assertEqual({json.loads(p.read_text())['pattern'] for p in files}, set(patterns.PATTERNS))
        for path in files:
            with self.subTest(path=path.name):
                page = renderer.render(json.loads(path.read_text()))
                self.assertIn('class="ed-scene"', page)
                self.assertNotIn('__ID__', page)
                self.assertNotIn('__ROOT__', page)

    def test_event_loop_is_serial_and_preserves_io_wait(self):
        for cpu, end in ((1, 11.6), (6, 38.4)):
            trace = patterns.scheduling_trace(cpu)
            self.assertAlmostEqual(trace['end'], end)
            self.assertTrue(all(a['end'] <= b['start']+1e-9 for a,b in zip(trace['thread'], trace['thread'][1:])))
            for request in trace['requests']:
                waits = [s for s in request if s['phase']=='wait']
                self.assertEqual(len(waits), 1)
                self.assertAlmostEqual(waits[0]['end']-waits[0]['start'], 6)
        slow = patterns.scheduling_trace(6)
        self.assertTrue(all(any(s['phase']=='blocked' for s in r) for r in slow['requests']))

    def test_pool_policies_share_workload_but_change_assignments(self):
        servers=[dict(id='A',service=100),dict(id='B',service=100),dict(id='C',service=1200)]
        for policy, expected in [('lifo',dict(A=9,B=0,C=9)),('fifo',dict(A=7,B=7,C=4))]:
            trace = patterns.pool_trace(policy, servers)
            counts = {s:len([r for r in trace['requests'] if not r['initial'] and r['server']==s]) for s in 'ABC'}
            self.assertEqual(counts, expected)
            for event in trace['events']:
                time = event['time']
                # Intermediate events at the same time are projected only after all such events.
                if event is not [e for e in trace['events'] if e['time']==time][-1]:
                    continue
                active = [r for r in trace['requests'] if r['start']<=time<r['end']]
                self.assertEqual(len(event['idle'])+len(active), 9)
                self.assertEqual(len(set(event['idle']+[r['connection'] for r in active])), 9)
            for server in servers:
                work = sorted([r for r in trace['requests'] if r['server']==server['id']],key=lambda r:r['workStart'])
                self.assertTrue(all(a['responseStart']<=b['workStart'] for a,b in zip(work,work[1:])))

    def test_policy_only_change_does_not_change_arrival_schedule(self):
        lifo = patterns.build(self.example('04a-pool-lifo'))['trace']
        fifo = patterns.build(self.example('04b-pool-fifo'))['trace']
        self.assertEqual([r['start'] for r in lifo['requests']], [r['start'] for r in fifo['requests']])

    def test_mobile_flow_has_unique_ids_and_contains_all_cards(self):
        data = self.example('02-request-flow')
        for count in [1, 3, 5]:
            data['content']['workers'] = ['Worker']*count
            data['content']['resources'] = ['Store']*count
            built=patterns.build(data)
            root=ET.fromstring('<root>'+built['markup']+'</root>')
            ids=[el.attrib['id'] for el in root.iter() if 'id' in el.attrib]
            self.assertEqual(len(ids),len(set(ids)))
            for svg in root:
                _,_,width,height=map(float,svg.attrib['viewBox'].split())
                for rect in svg.iter('rect'):
                    if rect.attrib.get('class')=='bp-box':
                        self.assertLessEqual(float(rect.attrib['x'])+float(rect.attrib['width']),width)
                        self.assertLessEqual(float(rect.attrib['y'])+float(rect.attrib['height']),height)

    def test_localized_pattern_labels_and_replay_are_required(self):
        data=self.example('04a-pool-lifo');data['locale']='zh-Hans'
        del data['content']['labels']['outcome']
        with self.assertRaisesRegex(ValueError,'content.labels.outcome'):
            renderer.render(data)
        data=self.example('04a-pool-lifo');data['locale']='zh-Hans';del data['ui']['replay']
        with self.assertRaisesRegex(ValueError,'ui.replay'):
            renderer.render(data)

    def test_invalid_models_fail_instead_of_drawing_misleading_cases(self):
        data=self.example('03-timeline');data['model']['scale']=10
        with self.assertRaisesRegex(ValueError,'complete timelines'):patterns.build(data)
        data=self.example('04a-pool-lifo');data['model']['policy']='random'
        with self.assertRaisesRegex(ValueError,'lifo or fifo'):patterns.build(data)
        data=self.example('05-aggregation');data['model']['concurrent']=100
        with self.assertRaises(ValueError):patterns.build(data)
        data=self.example('02-request-flow');data['scene']={'markup':'wrong.svg'}
        with self.assertRaisesRegex(ValueError,'separately'):renderer.render(data)


if __name__=='__main__':
    unittest.main()
