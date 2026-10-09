"""Original, parameterized compositions studied from six engineering-blog figures.

SPDX-License-Identifier: MIT
No extracted website markup, scripts, fonts or images are used here.
"""
import html
import json
import math
import re

PATTERNS = ("architecture", "request-flow", "timeline-comparison", "pool-reuse", "connection-aggregation")

STYLE = """
__ROOT__ .bp text { font-size:14px; }
__ROOT__ .bp .bp-small { font:500 10px var(--ed-mono); }
__ROOT__ .bp .bp-title { font:600 15px var(--ed-sans); }
__ROOT__ .bp .bp-copy { font:400 12px var(--ed-sans); }
__ROOT__ .bp .bp-muted { fill:var(--ed-muted); }
__ROOT__ .bp-box { fill:var(--ed-paper);stroke:var(--ed-ink);stroke-width:1; }
__ROOT__ .bp-rail { fill:none;stroke:var(--ed-ink);stroke-width:1;vector-effect:non-scaling-stroke; }
__ROOT__ .bp-rule { stroke:#e8e8e8;stroke-width:1; }
__ROOT__ .bp-request { fill:var(--ed-blue);stroke:var(--ed-ink);stroke-width:1; }
__ROOT__ .bp-response { fill:var(--ed-paper);stroke:var(--ed-ink);stroke-width:1; }
__ROOT__ .bp-change { fill:var(--ed-purple);stroke:var(--ed-ink);stroke-width:1; }
__ROOT__ .bp-controls { display:flex;align-items:center;gap:16px;padding:18px 32px;font:500 10px var(--ed-mono); }
__ROOT__ .bp-controls input { flex:1;min-width:80px;accent-color:var(--ed-ink); }
__ROOT__ .bp-controls output { min-width:100px;text-align:end; }
__ROOT__ .bp-mobile { display:none!important; }
"""


def esc(value):
    return html.escape(str(value), quote=True)


def finite(value, label, low=0, high=math.inf, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be finite")
    if not low <= value <= high or integer and int(value) != value:
        raise ValueError(f"{label} must be {'an integer ' if integer else ''}in [{low}, {high}]")
    return value


def items(value, label, low=1, high=8):
    if not isinstance(value, list) or not low <= len(value) <= high:
        raise ValueError(f"{label} must contain {low} to {high} items")
    for item in value:
        if not isinstance(item, (str, dict)):
            raise ValueError(f"{label} items must be strings or objects")
        if not isinstance(item if isinstance(item, str) else item.get('title'), str):
            raise ValueError(f"{label} items need a title")
    return value


def labeler(data):
    labels = data.get("content", {}).get("labels", {})
    english = data.get("locale", "en").split("-")[0].lower() == "en"
    def label(key, default):
        value = labels.get(key, default if english else None)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Provide localized content.labels.{key}")
        return value
    return label


def rounded(path, radius=8):
    tokens=re.findall(r"[MHV]|-?(?:\d+(?:\.\d*)?|\.\d+)",path)
    points=[];i=0;x=y=0
    while i<len(tokens):
        command=tokens[i];i+=1
        if command=='M':x,y=float(tokens[i]),float(tokens[i+1]);i+=2
        elif command=='H':x=float(tokens[i]);i+=1
        elif command=='V':y=float(tokens[i]);i+=1
        points.append((x,y))
    result=[f'M{points[0][0]:g} {points[0][1]:g}']
    for a,b,c in zip(points,points[1:],points[2:]):
        incoming,outgoing=math.dist(a,b),math.dist(b,c)
        if not incoming or not outgoing or (a[0]-b[0])*(c[1]-b[1])==(a[1]-b[1])*(c[0]-b[0]):
            result.append(f'L{b[0]:g} {b[1]:g}');continue
        r=min(radius,incoming/2,outgoing/2)
        start=[b[j]+(a[j]-b[j])*r/incoming for j in (0,1)]
        end=[b[j]+(c[j]-b[j])*r/outgoing for j in (0,1)]
        result.append(f'L{start[0]:g} {start[1]:g}Q{b[0]:g} {b[1]:g} {end[0]:g} {end[1]:g}')
    result.append(f'L{points[-1][0]:g} {points[-1][1]:g}')
    return ''.join(result)


class Drawing:
    def __init__(self, width, height, title, extra=""):
        self.head = "__ID__-head" + ("-" + extra if extra else "")
        self.parts = [f'<svg class="bp {extra}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">',
                      f'<defs><marker id="{self.head}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="8" markerHeight="8" orient="auto"><path d="M2 1 7 4 2 7" fill="none" stroke="#141414"/></marker></defs>']

    def rect(self, x, y, w, h, cls="bp-box", extra=""):
        self.parts.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="4" class="{cls}" {extra}/>')

    def text(self, x, y, value, cls="", anchor="start", width=500, extra=""):
        lines = str(value).split("\n")
        spans = ''.join(f'<tspan x="{x:g}" dy="{0 if i == 0 else 18}">{esc(line)}</tspan>' for i, line in enumerate(lines))
        self.parts.append(f'<text x="{x:g}" y="{y:g}" class="{cls}" text-anchor="{anchor}" data-ed-label="" data-ed-max-width="{width:g}" {extra}>{spans}</text>')

    def path(self, d, cls="bp-rail", extra=""):
        self.parts.append(f'<path d="{d}" class="{cls}" {extra}/>')

    def card(self, x, y, w, h, item, center=False):
        item = {"title": item} if isinstance(item, str) else item
        self.rect(x, y, w, h)
        tx, anchor = (x+w/2, "middle") if center else (x+12, "start")
        line_offset = 9 * (len(item['title'].split('\n')) - 1)
        self.text(tx, y+h/2+(0 if item.get('subtitle') else 5)-line_offset, item['title'], anchor=anchor, width=w-24)
        if item.get('subtitle'):
            self.text(tx, y+h/2+18, item['subtitle'], "bp-small", anchor, w-24)

    def flow(self, d, index=0, change=False):
        d = rounded(d)
        self.path(d, extra=f'marker-end="url(#{self.head})"')
        if change:
            shape, cls = '<path d="M0-5 5 0 0 5-5 0Z"/>', 'bp-change'
            self.parts.append(f'<g class="{cls}">{shape}<animateMotion path="{d}" dur="7s" begin="{-index*.6:g}s" repeatCount="indefinite"/></g>')
        else:
            for reverse, shape, cls in [(False, '<rect x="-4" y="-4" width="8" height="8" rx="2"/>', 'bp-request'),
                                        (True, '<circle r="4"/>', 'bp-response')]:
                motion = 'keyPoints="1;0" keyTimes="0;1"' if reverse else ''
                self.parts.append(f'<g class="{cls}" opacity="0">{shape}<animateMotion path="{d}" dur="8s" begin="{-index*.5-(4 if reverse else 0):g}s" {motion} calcMode="linear" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.03;.97;1" dur="8s" begin="{-index*.5-(4 if reverse else 0):g}s" repeatCount="indefinite"/></g>')

    def finish(self):
        return ''.join(self.parts) + '</svg>'


def architecture(data):
    c, label = data['content'], labeler(data)
    clients, resources = items(c['clients'], 'clients'), items(c['resources'], 'resources')
    features = items(c['features'], 'features', 1, 9)
    consumers = items(c.get('consumers', []), 'consumers', 0, 6)
    rows = math.ceil(len(features)/3)
    ph = 64 + rows*68 + (54 if c.get('routing') else 0)
    main_height = max(len(clients)*68, len(resources)*68, ph) + 80
    height = main_height + (190 if consumers else 40)
    d = Drawing(1278, height, data['title'])
    for x, value in [(32, label('clients', 'Clients')), (430, label('platform', 'Platform')), (998, label('resources', 'Resources'))]:
        d.text(x, 34, value, 'bp-small', width=350)
    py = (main_height-ph)/2
    d.rect(430, py, 400, ph)
    d.text(630, py+28, c['platform'], 'bp-title', 'middle', 376)
    for i, feature in enumerate(features):
        d.card(446+(i%3)*126, py+48+(i//3)*68, 116, 56, feature, True)
    if c.get('routing'):
        d.card(446, py+48+rows*68, 368, 42, c['routing'], True)
    for i, item in enumerate(clients):
        y = (main_height-len(clients)*68)/2+i*68
        d.flow(f'M282 {y+27:g} H350 V{py+ph/2:g} H430', i)
        d.card(32, y, 250, 54, item)
    for i, item in enumerate(resources):
        y = (main_height-len(resources)*68)/2+i*68
        d.flow(f'M830 {py+ph/2:g} H920 V{y+27:g} H998', i+len(clients))
        d.card(998, y, 248, 54, item)
    if consumers:
        hy = main_height+12
        d.flow(f'M630 {py+ph:g} V{hy:g}', 0, True)
        d.card(530, hy, 200, 54, c.get('changeService', label('changeService', 'Change capture')), True)
        gap = 20; w = (1214-gap*(len(consumers)-1))/len(consumers)
        for i, item in enumerate(consumers):
            x = 32+i*(w+gap)
            d.flow(f'M630 {hy+54:g} V{hy+84:g} H{x+w/2:g} V{hy+112:g}', i, True)
            d.card(x, hy+112, w, 54, item)
    return dict(width=1278, height=height, markup=d.finish(), style=STYLE+'__ROOT__ .bp-response{fill:var(--ed-response);}', script='', replay=False)


def request_flow(data):
    c, label = data['content'], labeler(data)
    workers, stores = items(c['workers'], 'workers', 1, 5), items(c['resources'], 'resources', 1, 5)
    h = max(382, 150+max(len(workers),len(stores))*68)
    d = Drawing(1278, h, data['title'], 'bp-desktop')
    center = h/2+9
    d.text(152, center-44, label('client', 'Client'), 'bp-small', 'middle', 240)
    d.text(554, 50, label('service', 'Service'), 'bp-small', 'middle', 388)
    d.text(1131, center-len(stores)*34-10, label('resources', 'Resources'), 'bp-small', 'middle', 230)
    d.rect(360, 70, 388, h-124)
    d.flow(f'M272 {center:g} H372')
    d.card(32, center-28, 240, 56, c['client'])
    for i, worker in enumerate(workers):
        y = center-len(workers)*68/2+i*68+6
        d.flow(f'M496 {center:g} H528 V{y+28:g} H556', i)
        d.flow(f'M732 {y+28:g} H762 V{center:g} H788', i+3)
        d.card(556, y, 176, 56, worker)
    d.card(372, center-28, 124, 56, c['ingress'])
    for i, store in enumerate(stores):
        y = center-len(stores)*68/2+i*68+6
        d.flow(f'M912 {center:g} H986 V{y+28:g} H1016', i+6)
        d.card(1016, y, 230, 56, store)
    d.card(788, center-28, 124, 56, c['egress'])
    # A separate vertical composition preserves readable labels on phones.
    mobile_h = 420+len(workers)*80+len(stores)*80
    m = Drawing(343, mobile_h, data['title'], 'bp-mobile')
    m.text(32, 26, label('client', 'Client'), 'bp-small', width=279)
    m.card(32, 44, 279, 56, c['client'])
    m.flow('M171.5 100 V148')
    m.card(32, 148, 279, 56, c['ingress'])
    wy = 264
    for i, worker in enumerate(workers):
        y = wy+i*80
        m.flow(f'M171.5 204 V230 H16 V{y+28:g} H32', i)
        m.card(32, y, 279, 56, worker)
    ey = wy+len(workers)*80+44
    for i in range(len(workers)):
        m.flow(f'M311 {wy+i*80+28:g} H327 V{ey-20:g} H171.5 V{ey:g}', i+3)
    m.card(32, ey, 279, 56, c['egress'])
    sy = ey+116
    for i, store in enumerate(stores):
        y = sy+i*80
        m.flow(f'M171.5 {ey+56:g} V{ey+84:g} H16 V{y+28:g} H32', i+6)
        m.card(32, y, 279, 56, store)
    css = STYLE + '__ROOT__ .bp-response{fill:var(--ed-response);}' + f'''@media(max-width:767px){{
__ROOT__{{max-width:345px!important;}}
__ROOT__ .ed-board{{width:343px!important;height:{mobile_h}px!important;}}
__ROOT__ .bp-desktop{{display:none!important;}}
__ROOT__ .bp-mobile{{display:block!important;position:absolute;inset:0;}}
}}'''
    return dict(width=1278, height=h, markup=d.finish()+m.finish(), style=css, script='', replay=False)


def scheduling_trace(cpu, count=3, wait=6, network=.4):
    """One FIFO event-loop thread; I/O completions join its ready queue."""
    pending = [(i, False) for i in range(count)]
    arrivals, thread = [], []
    requests = [[] for _ in range(count)]
    time = 0
    while pending or arrivals:
        arrivals.sort()
        while arrivals and arrivals[0][0] <= time + 1e-9:
            _, request = arrivals.pop(0)
            pending.append((request, True))
        if not pending:
            time = arrivals[0][0]
            continue
        request, response = pending.pop(0)
        if response:
            ready = requests[request][-1]['end']
            if time > ready+1e-9:
                requests[request].append(dict(phase='blocked', start=ready, end=time))
        for phase, length in ([('network', network), ('cpu', cpu)] if response else [('cpu', cpu), ('network', network)]):
            segment = dict(phase=phase, start=time, end=time+length, request=request)
            thread.append(segment); requests[request].append(segment)
            time += length
        if not response:
            requests[request].append(dict(phase='wait', start=time, end=time+wait))
            arrivals.append((time+wait, request))
    return dict(requests=requests, thread=thread, end=time)


def timeline(data):
    c, model, label = data['content'], data.get('model', {}), labeler(data)
    count = int(finite(model.get('requests', 3), 'requests', 1, 6, True))
    cpus = model.get('cpu', [1, 6])
    if not isinstance(cpus,list) or len(cpus)!=2: raise ValueError('cpu must contain two scenario durations')
    for cpu in cpus: finite(cpu, 'cpu duration', .01, 100)
    wait = finite(model.get('wait', 6), 'wait', 0, 1000)
    network = finite(model.get('network', .4), 'network', .001, 100)
    traces = [scheduling_trace(cpu, count, wait, network) for cpu in cpus]
    scale = finite(model.get('scale', math.ceil(max(t['end'] for t in traces)/10)*10), 'scale', .1)
    if scale < max(t['end'] for t in traces)-1e-8: raise ValueError('scale must contain both complete timelines')
    scenarios = items(c['scenarios'], 'scenarios', 2, 2)
    row_height = 190+count*58
    height = row_height*2
    d = Drawing(1278, height, data['title'])
    left, available = 156, 1090
    colors = {'cpu':'#90a9e5', 'network':'#4b6bab', 'wait':'#c4d2ed', 'blocked':'#fff'}
    phase_labels = {k:label(k,v) for k,v in [('cpu','CPU'),('network','Network'),('wait','I/O'),('blocked','Ready / blocked')]}
    for s, (scenario, trace) in enumerate(zip(scenarios, traces)):
        top = s*row_height
        d.text(32, top+30, scenario['title'], 'bp-title', width=600)
        d.text(1246, top+30, scenario['subtitle'], 'bp-copy', 'end', 650)
        d.text(32, top+58, '', 'bp-copy', extra=f'data-timeline-status="{s}"', width=1214)
        d.text(32, top+90, label('timeAxis','Time →'), 'bp-small', width=110)
        for step in range(5):
            d.text(left+available*step/4, top+90, f'{scale*step/4:g}', 'bp-small', 'middle', 80)
        d.parts.append(f'<defs><clipPath id="__ID__-reveal-{s}"><rect data-timeline-clip="{s}" x="{left}" y="{top+98}" width="0" height="{82+count*58}"/></clipPath></defs>')
        tracks = [trace['thread']]+trace['requests']
        for row, segments in enumerate(tracks):
            y = top+104+(row*58+10 if row else 0)
            name = label('thread','Python thread') if row==0 else label('request','Request {id}').replace('{id}',chr(64+row))
            d.text(32, y+18, name, 'bp-copy', width=112)
            d.rect(left,y,available,28)
            d.parts.append(f'<g clip-path="url(#__ID__-reveal-{s})">')
            for seg in segments:
                x, w = left+seg['start']/scale*available, (seg['end']-seg['start'])/scale*available
                extra = f'style="fill:{colors[seg["phase"]]}"'
                if seg['phase'] in ('wait','blocked'):extra += ' stroke-dasharray="2 2"'
                d.rect(x,y,w,28,'bp-box',extra)
                caption = chr(65+seg['request']) if row==0 else phase_labels[seg['phase']]
                if w>55:d.text(x+w/2,y+18,caption,'bp-small','middle',w-4)
            d.parts.append('</g>')
            if row:
                ready = next(seg['end'] for seg in segments if seg['phase']=='wait')
                x = left+ready/scale*available
                d.path(f'M{x:g} {y-8:g} V{y+34:g}')
                d.path(f'M{x:g} {y-12:g} l4 4 -4 4 -4 -4Z',extra='fill="#141414"')
        d.path(f'M{left} {top+98} V{top+126+count*58}',extra=f'data-timeline-cursor="{s}" stroke="#777"')
        d.text(left,top+156+count*58,label('finished','All requests finish at {time} units.').replace('{time}',f'{trace["end"]:g}'),'bp-copy',width=1050)
        if s==0:d.path(f'M32 {row_height-1} H1246','bp-rule')
    duration = scale/2+2
    control = f'<div class="bp-controls"><label for="__ID__-seek">{esc(label("seek","Illustrative time"))}</label><input id="__ID__-seek" data-timeline-seek type="range" min="0" max="{scale:g}" step=".1" value="0"/><output data-timeline-output></output></div>'
    script = f'''const scale={scale!r}, traces={json.dumps(traces)}, labels={json.dumps({'thread':label('thread','Python thread'),'complete':label('complete','All requests complete'),'idle':label('idle','Idle'),'request':label('request','Request {id}'),**phase_labels})};
const seek=root.querySelector('[data-timeline-seek]');
seek.addEventListener('input',()=>root.dispatchEvent(new CustomEvent('ed:seek',{{detail:{{time:Number(seek.value)/2,playing:false}}}})));
root.addEventListener('ed:frame',({{detail}})=>{{
 const unit={str(data.get('animated',True)).lower()}?Math.min(scale,detail.progress*detail.duration*2):scale;
 root.dataset.modelTime=String(unit);seek.value=unit;
 root.querySelector('[data-timeline-output]').textContent=unit.toFixed(1)+' / '+scale;
 traces.forEach((trace,index)=>{{
  root.querySelector(`[data-timeline-clip="${{index}}"]`).setAttribute('width',1090*unit/scale);
  root.querySelector(`[data-timeline-cursor="${{index}}"]`).setAttribute('transform',`translate(${{1090*unit/scale}} 0)`);
  const segment=trace.thread.find(s=>s.start<=unit&&unit<s.end);
  const status=unit>=trace.end?labels.complete:segment?labels.request.replace('{{id}}',String.fromCharCode(65+segment.request))+' · '+labels[segment.phase]:labels.idle;
  root.querySelector(`[data-timeline-status="${{index}}"]`).textContent=labels.thread+': '+status;
 }});
}});'''
    css = STYLE + '__ROOT__ .ed-board{background:var(--ed-paper);height:auto!important;} __ROOT__ .ed-scene{position:relative;} __ROOT__ .ed-scene>svg{height:auto;}'
    return dict(width=1278,height=height+64,markup=d.finish()+control,style=css,script=script,replay=True,duration=duration)


def pool_trace(policy, servers, per_server=3, arrivals=None, transfer=150):
    """Returned connections form a deque; each server serializes its own work."""
    idle = [f'{server["id"]}{i+1}' for server in servers for i in range(per_server)]
    service = {s['id']:s['service'] for s in servers}
    work_end = {s['id']:0 for s in servers}
    requests, events, pending = [], [], []
    def release(time):
        ready = sorted([r for r in pending if r['end']<=time],key=lambda r:(r['end'],r['id']))
        for r in ready:
            idle.append(r['connection']);pending.remove(r)
            events.append(dict(time=r['end'],idle=idle[:]))
    def dispatch(time, initial):
        release(time)
        if not idle:raise ValueError('Arrival schedule exhausts all available connections')
        connection = idle.pop() if policy=='lifo' else idle.pop(0)
        server = connection[0]
        start = max(time+transfer,work_end[server]);end = start+service[server]
        work_end[server]=end
        r=dict(id=len(requests),connection=connection,server=server,initial=initial,start=time,
               requestEnd=time+transfer,workStart=start,responseStart=end,end=end+transfer)
        requests.append(r);pending.append(r);events.append(dict(time=time,idle=idle[:]))
    for _ in idle[:]:dispatch(0,True)
    for time in arrivals if arrivals is not None else [1600+600*i for i in range(18)]:dispatch(time,False)
    release(math.inf)
    return dict(requests=requests,events=events,end=max(r['end'] for r in requests))


def pool(data):
    c, model, label = data['content'], data.get('model',{}), labeler(data)
    policy = model.get('policy','fifo')
    if policy not in ('lifo','fifo'):raise ValueError('pool policy must be lifo or fifo')
    servers = model.get('servers',[{'id':'A','service':100},{'id':'B','service':100},{'id':'C','service':1200}])
    if not isinstance(servers,list) or len(servers)!=3:raise ValueError('pool-reuse needs three comparable servers')
    ids=[]
    for server in servers:
        if not isinstance(server.get('id'),str) or len(server['id'])!=1 or not server['id'].isascii() or not server['id'].isalpha():raise ValueError('Server IDs must be single ASCII letters')
        ids.append(server['id']);finite(server['service'],'service duration',1,10000)
    if len(set(ids))!=3:raise ValueError('Server IDs must be unique')
    connections=int(finite(model.get('connectionsPerServer',3),'connectionsPerServer',1,4,True))
    arrivals=model.get('arrivals',[1600+600*i for i in range(18)])
    if not isinstance(arrivals,list) or not 1<=len(arrivals)<=30:raise ValueError('arrivals needs 1 to 30 times')
    for time in arrivals:finite(time,'arrival time',0,100000)
    if arrivals!=sorted(arrivals):raise ValueError('arrivals must be sorted')
    transfer=finite(model.get('transfer',150),'transfer',1,1000)
    trace=pool_trace(policy,servers,connections,arrivals,transfer)
    all_connections=[f'{s}{i+1}' for s in ids for i in range(connections)]
    phases=[label('burst','Initial burst'),label('reuse','Connection reuse'),label('outcome','Outcome')]
    model_end=arrivals[-1]+min(50,transfer)
    duration=model_end*6/1000+1.6
    seek=[.2*6, (arrivals[0]+min(2800,(arrivals[-1]-arrivals[0])/2))*6/1000, model_end*6/1000]
    parts=[f'<p class="bp-pool-narrative" data-pool-narrative></p><div class="bp-phases">']
    for i,(name,time) in enumerate(zip(phases,seek)):
        parts.append(f'<button type="button" data-pool-phase="{i}" data-seek="{time:g}"><span>0{i+1}</span> {esc(name)}</button>')
    parts.append(f'</div><div class="bp-pool"><div class="bp-pool-client"><strong>{esc(label("client","Client process"))}</strong><p>{esc(label("key","A1 identifies one connection to server A. Only available connections appear in the pool."))}</p><div class="bp-pool-order"><span>{esc(label("first","Returned first"))}</span><span>{esc(label("last","Returned last"))}</span></div><div class="bp-pool-well" style="--slots:{len(all_connections)}">')
    parts.extend('<i class="bp-pool-empty"></i>' for _ in all_connections)
    for connection in all_connections:parts.append(f'<span class="bp-pool-chip" data-connection="{esc(connection)}">{esc(connection)}</span>')
    parts.append(f'</div><p class="bp-pool-selection">{esc(label("selected","Selected connection"))} <strong data-pool-choice>—</strong></p></div>')
    wire=Drawing(780,84,label('traffic','Request and response paths'))
    for i,server in enumerate(ids):
        x=(i+.5)*260
        wire.path(f'M{x-10:g} 0 V84',extra='marker-end="url(#__ID__-head)"')
        wire.path(f'M{x+10:g} 84 V0',extra='marker-end="url(#__ID__-head)"')
    for request in trace['requests']:
        wire.parts.append(f'<g data-pool-packet="{request["id"]}" visibility="hidden"><rect width="8" height="8" x="-4" y="-4" class="bp-request"/><circle r="4" class="bp-response"/></g>')
    parts.append('<div class="bp-pool-wires">'+wire.finish().replace('<svg ', '<svg preserveAspectRatio="none" ')+'</div><div class="bp-pool-servers">')
    for server in servers:
        parts.append(f'<section class="bp-pool-server" data-server="{esc(server["id"])}"><span>{esc(label("server","Server process"))}</span><strong class="bp-server-name">{esc(server["id"])}</strong><p data-server-note></p><strong data-server-count>0</strong><span>{esc(label("concurrent","Concurrent requests"))}</span><div class="bp-pool-load">')
        for i in range(connections):parts.append(f'<div class="bp-pool-job" data-load-slot="{i}"><span></span><i></i></div>')
        parts.append('</div></section>')
    parts.append(f'</div><div class="bp-pool-history"><span>{esc(label("history","Subsequent requests"))}</span><div>')
    for i in range(len(arrivals)):parts.append(f'<span data-history-slot="{i}"></span>')
    parts.append('</div></div></div>')
    copy={k:label(k,v) for k,v in [('initialNarrative','A burst occupies every connection; slower work returns later.'),('returnedNarrative','Fast servers return their connections first.'),('reuseNarrative','New requests select available connections according to the chosen policy.'),('finalNarrative','Compare the history of assignments under the same arrivals and service times.'),('slower','Slower server'),('overloaded','Queued work'),('request','Request {id}') ]}
    script=f'''const trace={json.dumps(trace)}, servers={json.dumps(servers)}, policy={json.dumps(policy)}, copy={json.dumps(copy)}, firstArrival={arrivals[0]!r}, modelEnd={model_end!r};
root.querySelectorAll('[data-pool-phase]').forEach(button=>button.addEventListener('click',()=>root.dispatchEvent(new CustomEvent('ed:seek',{{detail:{{time:Number(button.dataset.seek),playing:false}}}}))));
root.addEventListener('ed:frame',({{detail}})=>{{
 const t={str(data.get('animated',True)).lower()}?Math.min(modelEnd,detail.progress*detail.duration*1000/6):modelEnd;
 let idle={json.dumps(all_connections)};for(const event of trace.events){{if(event.time>t)break;idle=event.idle;}}
 const active=trace.requests.filter(r=>r.start<=t&&t<r.end), history=trace.requests.filter(r=>!r.initial&&r.start<=t);
 const phase=t<firstArrival?0:t<modelEnd?1:2;
 root.dataset.modelTime=String(t);root.dataset.available=String(idle.length);root.dataset.inFlight=String(active.length);root.dataset.connections=String(idle.length+active.length);
 root.querySelector('[data-pool-narrative]').textContent=phase===2?copy.finalNarrative:phase===1?copy.reuseNarrative:t<1050?copy.initialNarrative:copy.returnedNarrative;
 root.querySelectorAll('[data-pool-phase]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.poolPhase)===phase)));
 root.querySelectorAll('[data-connection]').forEach(el=>{{const slot=idle.indexOf(el.dataset.connection);el.hidden=slot<0;el.style.setProperty('--slot',Math.max(0,slot));}});
 const selected=history.at(-1)?.connection||(policy==='lifo'?idle.at(-1):idle[0])||'—';root.querySelector('[data-pool-choice]').textContent=selected;
 root.querySelectorAll('[data-pool-packet]').forEach(el=>{{
  const r=trace.requests[Number(el.dataset.poolPacket)], down=t>=r.start&&t<r.requestEnd,up=t>=r.responseStart&&t<r.end;
  el.setAttribute('visibility',down||up?'visible':'hidden');
  if(down||up){{const index=servers.findIndex(s=>s.id===r.server),p=down?(t-r.start)/(r.requestEnd-r.start):1-(t-r.responseStart)/(r.end-r.responseStart);el.setAttribute('transform',`translate(${{(index+.5)*260+(down?-10:10)}} ${{84*p}})`);el.querySelector('rect').style.display=down?'':'none';el.querySelector('circle').style.display=up?'':'none';}}
 }});
 servers.forEach(s=>{{
  const node=root.querySelector(`[data-server="${{s.id}}"]`), pending=active.filter(r=>r.server===s.id&&r.requestEnd<=t&&t<r.responseStart);
  node.dataset.count=String(pending.length);node.querySelector('[data-server-count]').textContent=pending.length;
  node.querySelector('[data-server-note]').textContent=pending.some(r=>t<r.workStart)?copy.overloaded:s.service>Math.min(...servers.map(s=>s.service))?copy.slower:'';
  node.querySelectorAll('[data-load-slot]').forEach((slot,index)=>{{const r=pending[index];slot.dataset.occupied=String(!!r);slot.querySelector('span').textContent=r?copy.request.replace('{{id}}',String(r.id+1)):'';slot.querySelector('i').style.width=r?Math.max(0,Math.min(1,(t-r.workStart)/(r.responseStart-r.workStart)))*100+'%':'0%';}});
 }});
 root.querySelectorAll('[data-history-slot]').forEach((slot,index)=>{{slot.textContent=history[index]?.server||'';slot.dataset.sent=String(!!history[index]);}});
}});'''
    css=STYLE+'''
__ROOT__ .ed-board{background:var(--ed-paper);height:auto!important;} __ROOT__ .ed-scene{position:relative;}
__ROOT__ .bp-pool-narrative{padding:24px 32px;min-height:70px;border-bottom:1px solid #e8e8e8;font-size:12px;}
__ROOT__ .bp-phases{display:grid;grid-template-columns:repeat(3,1fr);border-bottom:1px solid #ddd;}
__ROOT__ .bp-phases button{padding:26px 32px;border:0;border-bottom:2px solid transparent;text-align:start;background:white;font:600 10px var(--ed-mono);color:inherit;cursor:pointer;}
__ROOT__ .bp-phases button[aria-pressed=true]{border-bottom-color:#4b6bab;} __ROOT__ .bp-phases span{margin-inline-end:8px;}
__ROOT__ .bp-pool{width:812px;margin:28px auto 20px;padding:14px;border:1px solid #e8e8e8;border-radius:8px;font-size:12px;}
__ROOT__ .bp-pool-client>strong{font-size:15px;} __ROOT__ .bp-pool-client>p{margin-top:10px;}
__ROOT__ .bp-pool-order{display:flex;justify-content:space-between;margin-top:16px;font:500 10px var(--ed-mono);}
__ROOT__ .bp-pool-well{display:grid;grid-template-columns:repeat(var(--slots),1fr);gap:4px;position:relative;margin-top:8px;height:28px;}
__ROOT__ .bp-pool-empty{border:1px dashed #777;border-radius:18px;}
__ROOT__ .bp-pool-chip{position:absolute;top:0;left:calc(var(--slot)*(100% + 4px)/var(--slots));width:calc((100% + 4px)/var(--slots) - 4px);height:28px;border:1px solid #141414;border-radius:18px;background:white;text-align:center;font:600 10px/26px var(--ed-mono);}
__ROOT__ .bp-pool-selection{height:30px;text-align:center;font:500 10px/30px var(--ed-mono);}
__ROOT__ .bp-pool-wires{height:84px;} __ROOT__ .bp-pool-wires>svg{display:block;width:100%;height:84px;}
__ROOT__ .bp-pool-servers{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;}
__ROOT__ .bp-pool-server{border:1px solid #141414;border-radius:8px;min-height:220px;text-align:center;padding:10px 8px;display:flex;align-items:center;flex-direction:column;gap:3px;font-size:10px;}
__ROOT__ .bp-server-name{font:500 16px var(--ed-mono);} __ROOT__ [data-server-note]{min-height:22px;line-height:22px;background:#90a9e5;width:100%;}
__ROOT__ [data-server-note]:empty{background:transparent;} __ROOT__ [data-server-count]{font:500 14px var(--ed-mono);}
__ROOT__ .bp-pool-load{width:100%;margin-top:14px;} __ROOT__ .bp-pool-job{position:relative;height:18px;border:1px dashed #777;margin:5px 0;border-radius:2px;overflow:hidden;}
__ROOT__ .bp-pool-job[data-occupied=true]{border:1px solid #141414;background:#c4d2ed;}
__ROOT__ .bp-pool-job span{position:relative;z-index:1;font:500 9px/16px var(--ed-mono);} __ROOT__ .bp-pool-job i{position:absolute;left:0;top:0;height:100%;background:#90a9e5;}
__ROOT__ .bp-pool-history{border-top:1px solid #e8e8e8;margin-top:16px;padding:12px 0;font:500 10px var(--ed-mono);}
__ROOT__ .bp-pool-history>div{display:grid;grid-template-columns:repeat(18,minmax(0,1fr));gap:3px;margin-top:10px;}
__ROOT__ .bp-pool-history span[data-history-slot]{height:20px;border:1px dashed #777;border-radius:2px;text-align:center;line-height:18px;}
__ROOT__ .bp-pool-history span[data-sent=true]{border-style:solid;background:#c4d2ed;}
@media(max-width:767px){__ROOT__ .ed-board{width:100%!important;}__ROOT__ .bp-pool{width:calc(100% - 24px);padding:10px;}__ROOT__ .bp-pool-narrative{padding:20px 24px;min-height:100px;}__ROOT__ .bp-phases button{padding:20px 12px;}__ROOT__ .bp-pool-history>div{grid-template-columns:repeat(9,minmax(0,1fr));}}
'''
    return dict(width=1278,height=790,markup=''.join(parts),style=css,script=script,replay=True,duration=duration,trace=trace)


def aggregation(data):
    c, model, label = data['content'], data.get('model',{}), labeler(data)
    pods=int(finite(model.get('pods',6),'pods',2,8,True))
    peak=int(finite(model.get('peakPerPod',3),'peakPerPod',1,4,True))
    concurrent=int(finite(model.get('concurrent',6),'concurrent',1,pods*peak,True))
    if concurrent>pods*peak:raise ValueError('concurrent exceeds total local capacity')
    scenarios=items(c['scenarios'],'scenarios',3,3)
    panel_h=160+pods*40
    d=Drawing(1278,panel_h*3,data['title'])
    for s,scenario in enumerate(scenarios):
        top=s*panel_h;first_y=top+114;last_y=first_y+(pods-1)*40
        d.text(32,top+30,scenario['title'],'bp-title',width=1200)
        d.text(32,top+58,scenario['subtitle'],'bp-copy',width=1214)
        d.text(124,top+90,label('pods','Client processes'),'bp-small',width=220)
        d.text(1167,top+90,label('storage','Storage'),'bp-small','middle',158)
        d.text(870,top+90,'','bp-small','middle',340,extra=f'data-open="{s}"')
        if s:
            d.text(576,top+90,label('pool','Shared pool'),'bp-small','middle',150)
            d.card(510,first_y,132,last_y-first_y+34,{'title':c['proxy'],'subtitle':scenario.get('protocol','')},True)
        wire_start=642 if s else 248
        wires=pods*peak if s==0 else concurrent if s==1 else 1
        for index in range(wires):
            y=first_y+(index//peak)*40+17+(index%peak-(peak-1)/2)*(26/max(1,peak-1)) if s==0 else first_y+(last_y-first_y)*index/max(1,wires-1)+17
            if s==2:y=(first_y+last_y)/2+17
            d.path(f'M{wire_start} {y:g} H1088',extra=f'data-wire="{s}-{index}" visibility="hidden"')
        for pod in range(pods):
            y=first_y+pod*40
            d.path(f'M32 {y+17:g} H124')
            if s:d.path(f'M248 {y+17:g} H510',extra=f'data-local-wire="{s}-{pod}"')
            d.rect(124,y,124,34)
            d.text(186,y+13,label('pod','Pod {id}').replace('{id}',str(pod+1)),'bp-small','middle',116)
            d.text(186,y+27,'','bp-small','middle',116,extra=f'data-pod="{s}-{pod}"')
        d.card(1088,first_y,158,last_y-first_y+34,c['storage'],True)
        for index in range(concurrent):
            d.parts.append(f'<g data-aggregate-packet="{s}-{index}" visibility="hidden"><rect width="16" height="16" x="-8" y="-8" rx="2" class="bp-request"/><circle r="8" class="bp-response"/></g>')
        d.text(32,top+panel_h-18,'','bp-copy',width=1214,extra=f'data-aggregate-status="{s}"')
        if s<2:d.path(f'M32 {top+panel_h-1} H1246','bp-rule')
    copy={k:label(k,v) for k,v in [('open','{count} open connections'),('podStatus','{active} active · peak {peak}'),('status','{busy} busy · {idle} idle · {upstream} concurrent upstream requests')]}
    script=f'''const pods={pods},peak={peak},concurrent={concurrent},panelHeight={panel_h},copy={json.dumps(copy)};
function format(text,values){{return text.replace(/\\{{(\\w+)\\}}/g,(_,key)=>values[key]);}}
root.addEventListener('ed:frame',({{detail}})=>{{
 const t={str(data.get('animated',True)).lower()}?detail.time:40;
 const born=Math.max(0,Math.floor(t)),busy=Math.min(concurrent,born),retained=Math.min(concurrent,born);
 const peaks=Array.from({{length:pods}},(_,pod)=>Math.max(0,Math.min(peak,born-pod*peak)));
 const jobs=Array.from({{length:busy}},(_,index)=>{{const id=born-busy+index;return{{id,pod:Math.floor(id/peak)%pods,slot:id%peak,p:(t-(id+1))/concurrent}};}});
 const counts=[peaks.reduce((a,b)=>a+b,0),retained,born?1:0];
 root.dataset.connectionCounts=counts.join(',');root.dataset.upstream=String(busy);
 for(let scene=0;scene<3;scene++){{
  root.querySelector(`[data-open="${{scene}}"]`).textContent=format(copy.open,{{count:counts[scene]}});
  const occupied=scene===2?(busy?1:0):busy;
  root.querySelector(`[data-aggregate-status="${{scene}}"]`).textContent=format(copy.status,{{busy:occupied,idle:counts[scene]-occupied,upstream:busy}});
  for(let pod=0;pod<pods;pod++){{
   const active=jobs.filter(j=>j.pod===pod).length;
   root.querySelector(`[data-pod="${{scene}}-${{pod}}"]`).textContent=format(copy.podStatus,{{active,peak:peaks[pod]}});
   if(scene)root.querySelector(`[data-local-wire="${{scene}}-${{pod}}"]`).setAttribute('stroke-dasharray',active?'':'3 3');
  }}
  root.querySelectorAll(`[data-wire^="${{scene}}-"]`).forEach(wire=>{{
   const index=Number(wire.dataset.wire.split('-')[1]),open=scene===0?index%peak<peaks[Math.floor(index/peak)]:index<counts[scene];
   const active=scene===0?jobs.some(j=>j.pod*peak+j.slot===index):scene===1?jobs.some(j=>j.id%concurrent===index):busy>0;
   wire.setAttribute('visibility',open?'visible':'hidden');wire.setAttribute('stroke-dasharray',active?'':'3 3');
  }});
  root.querySelectorAll(`[data-aggregate-packet^="${{scene}}-"]`).forEach((node,index)=>{{
   const job=jobs[index];node.setAttribute('visibility',job?'visible':'hidden');if(!job)return;
   const top=scene*panelHeight,first=top+114,last=first+(pods-1)*40;
   const y=scene===0?first+job.pod*40+17+(job.slot-(peak-1)/2)*(26/Math.max(1,peak-1)):scene===1?first+(last-first)*(job.id%concurrent)/Math.max(1,concurrent-1)+17:(first+last)/2+17;
   const start=scene?642:248,p=job.p<.5?job.p*2:2-job.p*2;
   node.setAttribute('transform',`translate(${{start+(1088-start)*p}} ${{y}})`);
   node.querySelector('rect').style.display=job.p<.5?'':'none';node.querySelector('circle').style.display=job.p>=.5?'':'none';
  }});
 }}
}});'''
    return dict(width=1278,height=panel_h*3,markup=d.finish(),style=STYLE+'__ROOT__ .ed-board{background:var(--ed-paper);}__ROOT__ .ed-mark-line{height:0;border-top:1px dashed var(--ed-mark-color);background:none;}',script=script,replay=True,duration=60,initialTime=40)


def build(data):
    pattern=data.get('pattern')
    if pattern not in PATTERNS:raise ValueError(f'Unknown pattern; choose one of {", ".join(PATTERNS)}')
    if not isinstance(data.get('content'),dict):raise ValueError('Pattern content must be an object')
    if not isinstance(data.get('model',{}),dict):raise ValueError('Pattern model must be an object')
    return {'architecture':architecture,'request-flow':request_flow,'timeline-comparison':timeline,
            'pool-reuse':pool,'connection-aggregation':aggregation}[pattern](data)
