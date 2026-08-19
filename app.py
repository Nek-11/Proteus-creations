"""Local-first Bordeaux job-search cockpit. Standard library only."""
from __future__ import annotations
import argparse, json, os
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "jobs.json"


def load_jobs(path: Path = DATA_PATH):
    with path.open(encoding="utf-8") as f:
        jobs = json.load(f)
    if not isinstance(jobs, list) or not all("id" in j and "company" in j for j in jobs):
        raise ValueError("jobs.json must contain a list of jobs with id and company")
    return jobs


def build_summary(jobs):
    active = [j for j in jobs if j.get("status") != "applied"]
    top = sorted(jobs, key=lambda j: (-j.get("priority", 0), j.get("company", "")))[0]
    return {"total": len(jobs), "active": len(active), "ready": sum(j.get("status") == "ready-to-apply" for j in jobs), "top_priority": top}


def card(job):
    tags = " ".join(f'<span class="tag">{escape(t)}</span>' for t in job.get("tags", []))
    return f'''<article class="card" data-job-id="{escape(job["id"])}" data-status="{escape(job["status"])}" data-search="{escape((job["company"]+" "+job["role"]+" "+" ".join(job.get("tags", []))).lower())}">
      <div class="card-top"><span class="priority">{'★' * job.get('priority', 1)}</span><button class="done" title="Mark applied">✓</button></div>
      <h3>{escape(job["company"])}</h3><p class="role">{escape(job["role"])}</p><p class="muted">{escape(job["location"])} · {escape(job.get("arrangement", "work arrangement to confirm"))}</p>
      <div class="tags">{tags}</div><p>{escape(job["fit"])}</p>
      <div class="action"><strong>Next:</strong> {escape(job["next_action"])}</div>
      <div class="meta">{('Checked '+escape(job['checked'])+' · '+escape(job.get('source_type','source not recorded'))) if job.get('checked') else 'Original lead · source date not recorded'}</div>
      <div class="links"><a class="link" href="{escape(job.get("official_url", job["url"]))}" target="_blank" rel="noreferrer">Official offer ↗</a>{('<a class="source-link" href="'+escape(job['discovery_url'])+'" target="_blank" rel="noreferrer">Found via '+escape(job.get('discovered_via','job board'))+' ↗</a>') if job.get('discovery_url') else ''}</div>
    </article>'''


def render_page(jobs):
    summary = build_summary(jobs)
    cards = "\n".join(card(j) for j in jobs)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bordeaux Job Cockpit</title>
<style>
:root{{--ink:#20242c;--muted:#6b7280;--line:#e8e4dc;--paper:#fffdf8;--cream:#f5f1e8;--coral:#e66b52;--blue:#385b8c}}*{{box-sizing:border-box}}body{{margin:0;background:var(--cream);color:var(--ink);font:15px/1.5 Inter,ui-sans-serif,system-ui,sans-serif}}.wrap{{max-width:1180px;margin:auto;padding:38px 22px 70px}}header{{display:flex;justify-content:space-between;gap:24px;align-items:end;margin-bottom:32px}}h1{{font:700 clamp(34px,5vw,62px)/.95 Georgia,serif;letter-spacing:-2px;margin:6px 0 13px}}h2,h3{{margin:0 0 5px}}.eyebrow{{color:var(--coral);font-weight:800;text-transform:uppercase;letter-spacing:2px;font-size:11px}}.intro{{max-width:610px;color:var(--muted);font-size:16px}}.privacy{{font-size:12px;color:var(--muted);border:1px solid var(--line);padding:10px 13px;border-radius:10px;background:#ffffff80;white-space:nowrap}}.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:24px}}.stat,.card,.toolbar{{background:var(--paper);border:1px solid var(--line);border-radius:14px}}.stat{{padding:17px 19px}}.stat b{{display:block;font-size:28px}}.stat span,.muted{{color:var(--muted);font-size:13px}}.toolbar{{padding:12px;display:flex;gap:10px;margin-bottom:18px}}input,select{{border:1px solid var(--line);background:white;border-radius:9px;padding:10px 12px;font:inherit;color:inherit}}input{{flex:1}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:14px}}.card{{padding:17px;display:flex;flex-direction:column;min-height:305px;transition:.2s}}.card:hover{{transform:translateY(-2px);box-shadow:0 8px 20px #44331b10}}.card-top{{display:flex;justify-content:space-between;margin-bottom:8px}}.priority{{color:#d99d32;letter-spacing:1px;font-size:12px}}button.done{{border:0;background:#eee9de;color:#777;border-radius:50%;width:25px;height:25px;cursor:pointer}}.role{{margin:0;color:var(--blue);font-weight:650}}.tags{{margin:12px 0 3px}}.tag{{background:#e8eef5;color:#385b8c;border-radius:20px;padding:3px 8px;margin:0 4px 4px 0;display:inline-block;font-size:11px}}.links{{display:flex;flex-wrap:wrap;gap:10px;margin-top:auto;padding-top:10px}}.link,.source-link{{color:var(--blue);font-weight:700;text-decoration:none}}.source-link{{color:var(--coral)}}.meta{{color:var(--muted);font-size:11px;margin-top:12px}}.card p{{font-size:13px}}.action{{background:#f8f3e8;border-left:3px solid var(--coral);padding:8px 10px;margin-top:auto;font-size:12px}}.link{{color:var(--blue);font-weight:700;text-decoration:none;margin-top:13px;font-size:13px}}.empty{{padding:35px;text-align:center;color:var(--muted);grid-column:1/-1}}footer{{margin-top:30px;color:var(--muted);font-size:12px}}@media(max-width:650px){{header{{display:block}}.privacy{{display:inline-block;margin-top:14px}}.stats{{grid-template-columns:1fr 1fr}}.stats .stat:last-child{{grid-column:1/-1}}.toolbar{{flex-direction:column}}}}
</style></head><body><main class="wrap"><header><div><div class="eyebrow">Local-first · Bordeaux / remote</div><h1>Bordeaux Job<br>Cockpit</h1><p class="intro">A calm, actionable view of Nikitas's AI, robotics and product opportunities — with a concrete next move for every lead.</p></div><div class="privacy">↗ No account · no tracking · your browser</div></header>
<section class="stats"><div class="stat"><b>{summary['total']}</b><span>tracked opportunities</span></div><div class="stat"><b>{summary['active']}</b><span>active leads</span></div><div class="stat"><b>{summary['ready']}</b><span>ready to apply</span></div></section>
<div class="toolbar"><input id="search" placeholder="Search company, role or tag…" aria-label="Search jobs"><select id="filter" aria-label="Filter status"><option value="all">All stages</option><option value="researching">Researching</option><option value="to-contact">To contact</option><option value="watching">Watching</option><option value="ready-to-apply">Ready to apply</option><option value="applied">Applied</option></select></div>
<section id="grid" class="grid">{cards}</section><footer>Sample data distilled from the local Jobs & Companies note. This project is additive: it reads only its own copy in <code>data/jobs.json</code>. Click ✓ to hide a lead locally; reset with <code>localStorage.clear()</code>.</footer></main>
<script>
const cards=[...document.querySelectorAll('.card')], search=document.querySelector('#search'), filter=document.querySelector('#filter'), grid=document.querySelector('#grid');
const hidden=new Set(JSON.parse(localStorage.getItem('applied-jobs')||'[]'));
function draw(){{let q=search.value.toLowerCase(), f=filter.value, shown=0; cards.forEach(c=>{{let ok=(f==='all'||c.dataset.status===f)&&c.dataset.search.includes(q)&&!hidden.has(c.dataset.jobId); c.style.display=ok?'flex':'none'; if(ok)shown++}}); let e=grid.querySelector('.empty'); if(!shown&&!e){{e=document.createElement('div');e.className='empty';e.textContent='No leads match this view.';grid.append(e)}} if(e)e.style.display=shown?'none':'block'}}
cards.forEach(c=>c.querySelector('.done').addEventListener('click',()=>{{hidden.add(c.dataset.jobId);localStorage.setItem('applied-jobs',JSON.stringify([...hidden]));draw()}})); search.addEventListener('input',draw); filter.addEventListener('change',draw); draw();
</script></body></html>'''


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        jobs = load_jobs()
        if self.path == "/api/jobs":
            body = json.dumps({"jobs": jobs, "summary": build_summary(jobs)}).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(body); return
        body = render_page(jobs).encode()
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers(); self.wfile.write(body)
    def log_message(self, *_): pass


def main():
    parser = argparse.ArgumentParser(description="Run the local Bordeaux Job Cockpit")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    print(f"Bordeaux Job Cockpit: http://127.0.0.1:{args.port}")
    HTTPServer(("127.0.0.1", args.port), Handler).serve_forever()

if __name__ == "__main__": main()

# Source note: sample records are a separate, user-editable copy of the vault leads.
# The app does not access or modify the vault, credentials, cron, or Hermes config.
# Remove only this directory to undo the artifact: rm -rf /opt/data/overnight-surprise

