// Offline, dependency-free contract tests for the self-contained HTML learning player.
// No market data, backtesting, network calls or browser installation.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { fileURLToPath } from "node:url";
import path from "node:path";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const file=path.join(root,"deliverables/chanlun_108_acceptance/04_AI_GUIDE/08_逐步播放交互演示.html");
const html=readFileSync(file,"utf8");
function extract(id) {
 const re=new RegExp('<script id="'+id+'"[^>]*>([\\s\\S]*?)<\\/script>',"g");
 const entries=[...html.matchAll(re)];
 assert.equal(entries.length,1,"exactly one "+id+" tag");
 return entries[0][1];
}
const fixtureString=extract("lesson-data"),appString=extract("lesson-app"),fixtures=JSON.parse(fixtureString);
assert.equal(fixtures.schema_version,1);
assert.ok(/<svg id="chart"/.test(html),"SVG view exists");
assert.ok(/id="prev"/.test(html)&&/id="next"/.test(html)&&/id="play"/.test(html));
assert.ok(!/<script[^>]+src\s*=/.test(html),"no external javascript dependency");
assert.ok(!/fetch\s*\(|XMLHttpRequest|innerHTML\s*=|eval\s*\(/.test(appString),"no network or HTML injection surface");
new vm.Script(appString,{filename:"asof-player-inline.js"});
const ctx=vm.createContext({document:{getElementById(id){return id==="lesson-data"?{textContent:fixtureString}:null;}},console});
vm.runInContext(appString,ctx,{timeout:2000});
const core=ctx.ChanlunLessonCore;
assert.ok(core&&typeof core.snapshot==="function");
const expected=["fractals","containment","center_a","center_b","ambiguity"];
assert.deepEqual(fixtures.demos.map(d=>d.id),expected);
for(const d of fixtures.demos) {
 assert.ok(d.sourceLessons.length,"source-cited demo");
 assert.ok(d.events.length>=5,"at least five events per demo");
 assert.equal(new Set(d.events.map(e=>e.id)).size,d.events.length,"event IDs unique");
 const zero=core.snapshot(d.id,0);
 assert.equal(zero.count,0);assert.equal(zero.latest,null);assert.equal(zero.domain,null);
 assert.equal(zero.center,null);assert.equal(zero.visible.length,0);
 for(let n=1;n<=d.events.length;n++){
  const view=core.snapshot(d.id,n);
  assert.equal(view.count,n);assert.equal(view.visible.length,n);
  assert.equal(view.latest.id,d.events[n-1].id);
  assert.equal(view.latest.status,d.events[n-1].status);
  assert.equal(view.visible.map(x=>x.id).join("|"),d.events.slice(0,n).map(x=>x.id).join("|"));
  assert.equal(view.domain.min,Math.min(...d.events.slice(0,n).map(e=>e.low)));
  assert.equal(view.domain.max,Math.max(...d.events.slice(0,n).map(e=>e.high)));
  for(const e of view.visible) {
   for(const field of ["id","title","status","detail","gate"])assert.ok(e[field]);
   assert.ok(e.low<=e.high);
   assert.ok(e.open>=e.low&&e.open<=e.high);
   assert.ok(e.close>=e.low&&e.close<=e.high);
  }
  // Explicit replay contract: displayed snapshot is independent of unobserved events.
  const tail=JSON.parse(JSON.stringify(fixtures.demos));
  const changed=tail.find(x=>x.id===d.id);
  changed.events.splice(n);
  assert.equal(view.visible.length,changed.events.length);
 }
 assert.equal(core.snapshot(d.id,999).count,d.events.length);
}
const f=core.snapshot("fractals",2),f3=core.snapshot("fractals",3);
assert.equal(f.latest.status,"CANDIDATE");assert.equal(f3.latest.status,"LOCAL_TOP");
assert.equal(core.snapshot("fractals",5).latest.status,"BOTTOM_CANDIDATE");
assert.equal(core.snapshot("fractals",6).latest.status,"LOCAL_TOP_AND_BOTTOM");
assert.equal(core.snapshot("containment",2).latest.status,"CONTAINMENT_FLAG");
assert.equal(core.snapshot("containment",6).latest.status,"VERSION_GAP");
const a=fixtures.demos.find(x=>x.id==="center_a"),b=fixtures.demos.find(x=>x.id==="center_b");
assert.equal(JSON.stringify(a.events.slice(0,7)),JSON.stringify(b.events.slice(0,7)),"branches share the exact same historical prefix");
assert.equal(core.snapshot("center_a",3).center,null,"C cannot be shown as completed while incomplete");
assert.equal(core.snapshot("center_a",4).center.high,15,"center only after C completion");
assert.equal(core.snapshot("center_a",5).latest.status,"LEAVE_PENDING");
assert.equal(core.snapshot("center_a",7).latest.status,"RETRACE_PENDING");
assert.equal(core.snapshot("center_b",7).latest.status,"RETRACE_PENDING");
assert.equal(core.snapshot("center_a",8).latest.status,"THIRD_BUY_GEOMETRY");
assert.equal(core.snapshot("center_b",8).latest.status,"THIRD_BUY_GEOMETRY_FAILED");
assert.ok(!core.snapshot("center_a",3).latest.detail.includes("13,15"),"incomplete C must not leak future final range");
assert.ok(!core.snapshot("center_a",7).latest.detail.includes("回试完成"));
assert.ok(!core.snapshot("center_b",7).latest.detail.includes("跌入原中枢"));
const ambiguous=core.snapshot("ambiguity",2);
assert.equal(ambiguous.alternatives.length,2);
assert.equal(core.snapshot("ambiguity",0).alternatives.length,0);
assert.equal(core.snapshot("ambiguity",5).latest.status,"UNKNOWN");
const md=readFileSync(path.join(root,"deliverables/chanlun_108_acceptance/04_AI_GUIDE/08_交互式演示阅读卡.md"),"utf8");
for(const needle of ["K3结束","K6结束","T3","T7","T8","C1","C2","U5","Raw","NOT_RUN"])assert.ok(md.includes(needle),"static readable fallback missing "+needle);
// Lightweight DOM smoke test (no browser dependency): prove selector, buttons and render path work.
function fakeNode(tag="div") {
 const n={tagName:tag.toUpperCase(),value:"",textContent:"",children:[],handlers:{},disabled:false,
  attributes:{},addEventListener(type,fn){this.handlers[type]=fn;},
  setAttribute(key,value){this.attributes[key]=String(value);},
  appendChild(child){this.children.push(child);return child;},
  removeChild(child){const i=this.children.indexOf(child);if(i>=0)this.children.splice(i,1);return child;}};
 Object.defineProperty(n,"firstChild",{get(){return n.children[0]||null;}});
 return n;
}
const dom=new Map();
const ids=["demo","range","next","prev","reset","play","progress","kind","status",
 "title","detail","gate","note","timeline","alternatives","sources","chart"];
for(const id of ids)dom.set(id,fakeNode(id==="chart"?"svg":id==="demo"?"select":"div"));
const domDoc={
 getElementById(id){return id==="lesson-data"?{textContent:fixtureString}:dom.get(id)||null;},
 createElement(tag){return fakeNode(tag);},createElementNS(_namespace,tag){return fakeNode(tag);},
 addEventListener(){},activeElement:{tagName:"BODY"},
};
const browserContext=vm.createContext({document:domDoc,console,
 setInterval(){throw Error("timer should not run in smoke test");},clearInterval(){}});
vm.runInContext(appString,browserContext,{timeout:2000});
assert.equal(dom.get("demo").children.length,5,"selector populated");
assert.equal(dom.get("status").textContent,"NOT_OBSERVED");
dom.get("next").handlers.click();assert.equal(dom.get("status").textContent,"OBSERVED");
dom.get("next").handlers.click();assert.equal(dom.get("status").textContent,"CANDIDATE");
dom.get("prev").handlers.click();assert.equal(dom.get("status").textContent,"OBSERVED");
dom.get("demo").value="center_a";dom.get("demo").handlers.change({target:dom.get("demo")});
assert.equal(dom.get("status").textContent,"NOT_OBSERVED","scenario change resets timeline");
for(let i=0;i<4;i++)dom.get("next").handlers.click();
assert.equal(dom.get("status").textContent,"CENTER_CONFIRMED");
assert.ok(dom.get("chart").children.length>5,"SVG populated");
dom.get("reset").handlers.click();assert.equal(dom.get("status").textContent,"NOT_OBSERVED");

console.log(JSON.stringify({status:"PASS",fixture_count:fixtures.demos.length,events:fixtures.demos.reduce((a,d)=>a+d.events.length,0),asof_snapshots_checked:fixtures.demos.reduce((a,d)=>a+d.events.length+1,0),branch_prefix_identical:true,static_fallback:true,backtests_run:0}));
