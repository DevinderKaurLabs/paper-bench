"""Where projects live: one JSON file, seeded with the five demo projects on first run."""
from __future__ import annotations

import copy
import json
import os
import time
import uuid
from pathlib import Path

from demo_data import DEMO_PROJECTS

DATA_FILE = Path(os.getenv("PAPER_BENCH_DATA", Path(__file__).parent / "data" / "projects.json"))


def _seed():
    out = []
    for p in copy.deepcopy(DEMO_PROJECTS):
        p.setdefault("chat", [])
        p.setdefault("created_at", 0)
        out.append(p)
    return out


def load() -> list:
    try:
        if DATA_FILE.exists():
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list) and data:
                return data
    except Exception:
        pass
    projects = _seed()
    save(projects)
    return projects


def save(projects: list) -> bool:
    try:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = DATA_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(projects, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(DATA_FILE)
        return True
    except Exception:
        return False


def reset_demos(projects: list) -> list:
    own = [p for p in projects if not p.get("demo")]
    return _seed() + own


def new_project(name: str, problem: str, context: str = "", constraints: str = "") -> dict:
    return {"id": "p-" + uuid.uuid4().hex[:10], "name": name.strip(), "problem": problem.strip(),
            "context": context.strip(), "constraints": constraints.strip(), "demo": False,
            "created_at": time.time(), "map": None, "papers": [], "synthesis": None, "solutions": None, "chat": []}


def new_paper(p: dict, title: str, source: str, text: str = "", **extra) -> dict:
    num = max([x["num"] for x in p.get("papers", [])] or [0]) + 1
    paper = {"id": "x-" + uuid.uuid4().hex[:10], "num": num, "title": title, "source": source,
             "text": (text or "")[:60000], "card": None}
    paper.update(extra)
    p.setdefault("papers", []).append(paper)
    return paper


def norm(s: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def find_in_library(p: dict, title: str):
    n = norm(title)
    if not n:
        return None
    for x in p.get("papers", []):
        if norm(x.get("title")) == n or norm((x.get("card") or {}).get("title")) == n:
            return x
    return None


def to_markdown(p: dict) -> str:
    L = [f"# {p['name']}", "", f"**Problem:** {p['problem']}", ""]
    m = p.get("map")
    if m:
        L += ["## Research map", m.get("reframed_problem", ""), "", "Sub-questions:"] + [f"- {q}" for q in m.get("sub_questions", [])] + [""]
    if p.get("papers"):
        L.append("## Library")
        for x in sorted(p["papers"], key=lambda x: x["num"]):
            c = x.get("card") or {}
            L.append(f"- **P{x['num']}** {c.get('title') or x['title']} ({c.get('authors', '')} {c.get('year', '')}) — {c.get('one_liner', 'not summarised')}")
        L.append("")
    s = p.get("synthesis")
    if s:
        L += ["## Synthesis", s.get("state_of_field", ""), "", "Gaps:"] + [f"- {g.get('gap')} → {g.get('opportunity')}" for g in s.get("gaps", [])] + [""]
    sol = p.get("solutions")
    if sol:
        L.append("## Solutions")
        for x in sol.get("solutions", []):
            e = x.get("experiment", {})
            L += [f"### {x.get('name')} ({x.get('effort', '?')} effort, {x.get('confidence', '')})", x.get("pitch", ""),
                  f"Grounded in: {', '.join(x.get('grounded_in', []))}"]
            L += [f"{i + 1}. {h}" for i, h in enumerate(x.get("how_it_works", []))]
            L += [f"MVP: {x.get('mvp', '')}",
                  f"Experiment: {e.get('hypothesis', '')} | metric: {e.get('metric', '')} | success: {e.get('success_threshold', '')} | drop if: {e.get('change_our_mind', '')}", ""]
        r = sol.get("recommendation")
        if r:
            L.append(f"**Start with:** {r.get('pick')} — {r.get('why')}")
    return "\n".join(L)
