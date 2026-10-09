// Shared clock behavior; run with node --test tests/playback.test.cjs.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../skills/editorial-diagrams/assets/playback.js'), 'utf8');

async function fixture({animated = true, search = '', reduced = false, initialTime = 0} = {}) {
  const events = [], raf = new Map(), listeners = {}, rootListeners = {}, parts = {};
  let now = 0, nextFrame = 0, intersection, preferenceChange;
  const part = () => ({toggleAttribute() {}, textContent: ''});
  const button = {dataset: {playLabel: '播放', pauseLabel: '暂停', playDescription: '播放动画', pauseDescription: '暂停动画'},
    attrs: {}, setAttribute(k, v) {this.attrs[k] = v;}, querySelector(k) {return parts[k] ||= part();},
    addEventListener(k, fn) {listeners[k] = fn;}};
  const svg = {time: null, paused: true, setCurrentTime(t) {this.time = t;},
    pauseAnimations() {this.paused = true;}, unpauseAnimations() {this.paused = false;}};
  const animation = {currentTime: null, play() {this.paused = false;}, pause() {this.paused = true;}};
  const board = {querySelectorAll: () => [svg], getAnimations: () => [animation]};
  const viewport = {scrollLeft: 0};
  const replay = {addEventListener: (key, fn) => {listeners.replay = fn;}};
  const root = {dataset: {animated: String(animated), duration: '10', initialTime: String(initialTime)},
    querySelector: selector => ({'.ed-board': board, '.ed-control': animated ? replay : null, '[data-play-label]': animated ? button : null, '.ed-viewport': viewport})[selector],
    querySelectorAll: selector => selector === '[data-ed-replay]' && animated ? [replay] : [], addEventListener: (key, fn) => {rootListeners[key] = fn;},
    dispatchEvent: event => {if(event.type === 'ed:frame') events.push(event.detail); else rootListeners[event.type]?.(event);}};
  const document = {hidden: false, getElementById: () => root, fonts: {ready: Promise.resolve()},
    addEventListener: (key, callback) => {listeners[key] = callback;}};
  const preference = {matches: reduced, addEventListener: (_, fn) => {preferenceChange = fn;}};
  vm.runInNewContext(source.replace('__DIAGRAM_ID__', '"test"'), {
    document, window: {location: {search}, matchMedia: () => preference}, URLSearchParams,
    CustomEvent: class {constructor(type, data) {this.type = type; this.detail = data.detail;}},
    performance: {now: () => now}, console,
    requestAnimationFrame: fn => {const id = ++nextFrame; raf.set(id, fn); return id;},
    cancelAnimationFrame: id => raf.delete(id),
    IntersectionObserver: class {constructor(fn) {intersection = fn;} observe() {}},
    ResizeObserver: class {observe() {}}
  });
  await Promise.resolve();
  return {root, button, svg, animation, events, raf, viewport,
    advance(ms) {now += ms; const callbacks = [...raf.values()]; raf.clear(); callbacks.forEach(fn => fn(now));},
    click() {listeners.click();},
    replay() {listeners.replay();},
    visible(value) {intersection([{isIntersecting: value}]);},
    hidden(value) {document.hidden = value; listeners.visibilitychange();},
    reduced(value) {preference.matches = value; preferenceChange({matches: value});},
    seek(time, playing = false) {root.dispatchEvent({type: 'ed:seek', detail: {time, playing}});},
    last: () => events.at(-1)};
}

test('frozen captures initialize authored scenes and native media at the same time', async () => {
  const f = await fixture({search: '?time=23.5&scroll=300'});
  assert.equal(f.last().time, 23.5);
  assert.equal(f.last().progress, .35);
  assert.equal(f.last().cycle, 2);
  assert.equal(f.svg.time, 23.5);
  assert.equal(f.animation.currentTime, 23500);
  assert.equal(f.raf.size, 0);
  assert.equal(f.viewport.scrollLeft, 300);
});

test('pause and resume preserve elapsed time and localized controls', async () => {
  const f = await fixture();
  f.advance(1200);
  f.click();
  assert.equal(f.last().time, 1.2);
  assert.equal(f.button.attrs['aria-label'], '播放动画');
  assert.equal(f.svg.paused, true);
  assert.equal(f.animation.paused, true);
  f.advance(5000);
  f.click();
  assert.equal(f.button.attrs['aria-label'], '暂停动画');
  f.advance(500);
  assert.equal(f.last().time, 1.7);
  assert.equal(f.last().active, true);
});

test('offscreen and hidden periods do not advance scene time', async () => {
  const f = await fixture();
  f.advance(500);
  f.visible(false);
  f.advance(9000);
  assert.equal(f.last().active, false);
  assert.equal(f.raf.size, 0);
  f.visible(true);
  f.advance(500);
  assert.equal(f.last().time, 1);
  f.hidden(true);
  f.advance(9000);
  f.hidden(false);
  f.advance(250);
  assert.equal(f.last().time, 1.25);
});

test('static output initializes without a button or running animation loop', async () => {
  const f = await fixture({animated: false});
  assert.equal(f.last().time, 0);
  assert.equal(f.last().playing, false);
  assert.equal(f.raf.size, 0);
  f.reduced(false);
  f.visible(true);
  f.advance(1000);
  assert.equal(f.last().time, 0);
  assert.equal(f.raf.size, 0);
  assert.equal(f.svg.paused, true);
});

test('reduced motion starts paused and can resume without accumulated waiting time', async () => {
  const f = await fixture({reduced: true});
  f.advance(3000);
  assert.equal(f.last().time, 0);
  assert.equal(f.last().playing, false);
  f.reduced(false);
  f.advance(200);
  assert.equal(f.last().time, .2);
});


test('pattern seek freezes an exact state, then resumes from that state', async () => {
  const f = await fixture();
  f.advance(800);
  f.seek(26.4);
  assert.equal(f.last().time, 26.4);
  assert.equal(f.last().playing, false);
  assert.equal(f.svg.time, 26.4);
  assert.equal(f.raf.size, 0);
  f.seek(0, true);
  f.advance(500);
  assert.equal(f.last().time, .5);
  assert.equal(f.last().playing, true);
});

test('a steady initial state can be overridden by a capture query', async () => {
  const f = await fixture({initialTime: 40});
  assert.equal(f.last().time, 40);
  const g = await fixture({initialTime: 40, search: '?time=0'});
  assert.equal(g.last().time, 0);
  f.replay();
  assert.equal(f.last().time, 0);
  assert.equal(f.last().playing, true);
  f.advance(500);
  assert.equal(f.last().time, .5);
});
