# Bordeaux Job Cockpit

A small, local-first dashboard for turning Nikitas's Bordeaux / remote AI job notes into a next-action pipeline.

![local-first](https://img.shields.io/badge/local--first-no%20account-385b8c)

## Run it

Requires Python 3.10+ and no third-party packages:

```bash
cd /opt/data/overnight-surprise
python3 app.py
```

Open <http://127.0.0.1:8765>. Use `--port 8787` if the default is busy.

## What it does

- Tracks Bordeaux-area and nearby AI, data, product, and robotics opportunities.
- Shows priority, fit rationale, and one concrete next action per lead.
- Supports instant search and stage filtering.
- Lets you hide completed leads with ✓. That preference stays only in this browser's `localStorage`.
- Exposes a tiny read-only JSON endpoint at `/api/jobs` for future integrations.

This is intentionally a self-contained copy. It does **not** read, write, or import the Obsidian vault; it does not touch Hermes, credentials, cron, or any existing project. Edit `data/jobs.json` when you want to add or revise leads.

## Verify

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile app.py
```

## Undo

The artifact is additive and reversible. If no longer useful, stop the server and optionally remove only this directory:

```bash
rm -rf /opt/data/overnight-surprise
```

## Data provenance

`data/jobs.json` is demo/sample data distilled from `/opt/data/vault/Jobs & Companies.md` on 2026-08-19. It is deliberately a separate copy so the cockpit remains safe to experiment with.

## Design note

The useful unit here is not a job bookmark; it is a **next action**. Every card therefore contains a suggested move that turns passive research into outreach, tailoring, or a recurring check.

License: personal utility; use and modify freely.

Created as an overnight surprise artifact.

---

### Smoke check

Start the server, then in another terminal:

```bash
curl -s http://127.0.0.1:8765/api/jobs | python3 -c 'import json,sys; d=json.load(sys.stdin); print(len(d["jobs"]), d["summary"]["active"])'
```

Expected sample output: `9 9`.
