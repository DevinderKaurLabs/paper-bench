"""Paper Bench: turn a business problem into research-backed solutions.

Run locally:  streamlit run app.py
"""
from __future__ import annotations

import html
import io
import json
import os
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

import streamlit as st

import engine
import store
from styles import CSS

st.set_page_config(page_title="Paper Bench", page_icon="\U0001F4DA", layout="wide")
# blank lines would end the HTML block in markdown, so strip them
st.markdown(re.sub(r"\n\s*\n", "\n", CSS), unsafe_allow_html=True)

VIEWS = ["Map", "Library", "Synthesis", "Solutions", "Ask"]

# ------------------------------------------------------------------ state
if "projects" not in st.session_state:
    st.session_state.projects = store.load()
ss = st.session_state
ss.setdefault("cur", ss.projects[0]["id"] if ss.projects else None)
ss.setdefault("view", "Map")
ss.setdefault("flash", [])
ss.setdefault("confirm", None)


def persist():
    if not store.save(ss.projects):
        ss.flash.append(("warning", "Couldn't write to disk. Use Your data → Download all projects to keep a copy."))


def current():
    for p in ss.projects:
        if p["id"] == ss.cur:
            return p
    ss.cur = ss.projects[0]["id"]
    return ss.projects[0]


def flash(kind, msg):
    ss.flash.append((kind, msg))


# ------------------------------------------------------------------ text helpers
def esc(s):
    return html.escape(str(s if s is not None else ""))


CONFS = {"certain": "Certain", "likely": "Likely", "guessing": "Guessing"}


def conf(c):
    c = CONFS.get(str(c or "").lower())
    return f'<span class="conf conf-{c.lower()}">{c}</span>' if c else ""


def rich(s):
    t = esc(s)
    t = re.sub(r"\[(P\d+)\]", r'<span class="chip">\1</span>', t)
    t = re.sub(r"\[(Certain|Likely|Guessing)\]", lambda m: conf(m.group(1)), t)
    return t


def chips(lst):
    return "".join(f'<span class="chip">{esc(x)}</span>' for x in (lst or []))


def links(q):
    e = urllib.parse.quote_plus(q or "")
    return (f'<span class="links"><a href="https://scholar.google.com/scholar?q={e}" target="_blank">Google Scholar</a>'
            f'<a href="https://www.semanticscholar.org/search?q={e}" target="_blank">Semantic Scholar</a>'
            f'<a href="https://arxiv.org/search/?query={e}&searchtype=all" target="_blank">arXiv</a></span>')


def ul(items, cls=""):
    return "<ul>" + "".join(f"<li>{rich(i)}</li>" for i in items or []) + "</ul>"


def md(s):
    st.markdown(s, unsafe_allow_html=True)


# ------------------------------------------------------------------ AI access (Gemini by default, Claude optional)
def _secret(name):
    try:
        return st.secrets.get(name)
    except Exception:
        return None


def _env(name):
    return _secret(name) or os.getenv(name)


def provider():
    """The provider in use: the one picked in Settings, else whichever key is configured, else Gemini."""
    if ss.get("provider") in engine.PROVIDERS:
        return ss.provider
    chosen = _env("PAPER_BENCH_PROVIDER")
    if chosen in engine.PROVIDERS:
        return chosen
    if not _env("GEMINI_API_KEY") and _env("ANTHROPIC_API_KEY"):
        return "claude"
    return engine.DEFAULT_PROVIDER


def ai():
    """Returns (client, model), or (None, model) when no key is set."""
    prov = provider()
    info = engine.PROVIDERS[prov]
    key = ss.get(f"key_{prov}") or _env(info["key"])
    model = ss.get("model") or _env("PAPER_BENCH_MODEL") or info["model"]
    if not key:
        return None, model
    return engine.make_client(key, prov), model


def need_ai():
    client, model = ai()
    if not client:
        flash("warning", "Add a free Gemini API key in the sidebar under Settings to run new research. The 5 starter projects work without it.")
    return client, model


# ------------------------------------------------------------------ actions
def add_suggested(p, s):
    if not s or not s.get("title") or store.find_in_library(p, s["title"]):
        return None
    return store.new_paper(p, s["title"], "Model knowledge", "", origin="knowledge",
                           authors=s.get("authors", ""), year=str(s.get("year", "")))


def apply_card(paper, card, by=None):
    if by:
        paper["by"] = by
    if card.get("unknown"):
        paper["unknown"], paper["card"] = True, None
    else:
        paper["unknown"], paper["card"] = False, card
        if card.get("title") and len(str(card["title"])) > 3:
            paper["title"] = str(card["title"])
    paper["failed"] = False


def summarise_many(p, papers, client, model, on_progress=None):
    """Summarise papers. Papers from the model's knowledge go several per request (saves free-tier quota);
    uploaded papers go one per request. Returns the number that failed; raises on account-level errors."""
    papers = [x for x in papers if x]
    if not papers:
        return 0
    known = [x for x in papers if x.get("origin") == "knowledge"]
    texts = [x for x in papers if x.get("origin") != "knowledge"]
    tasks = [("batch", known[i:i + engine.BATCH_SIZE]) for i in range(0, len(known), engine.BATCH_SIZE)]
    tasks += [("one", [x]) for x in texts]
    failed, done, total = 0, 0, len(papers)

    def run(task):
        kind, group = task
        if kind == "batch":
            return engine.summarise_known(client, model, p, group)
        return {group[0]["num"]: engine.summarise_paper(client, model, p, group[0])}

    with ThreadPoolExecutor(max_workers=client.parallel) as pool:
        futs = {pool.submit(run, t): t for t in tasks}
        for f in as_completed(futs):
            _, group = futs[f]
            try:
                cards = f.result()
            except Exception as e:
                if engine.is_fatal(e):
                    for g in futs:
                        g.cancel()
                    raise
                cards = {}
            for x in group:
                done += 1
                if x["num"] in cards:
                    apply_card(x, cards[x["num"]], by=client.name)
                else:
                    x["failed"] = True
                    failed += 1
                if on_progress:
                    on_progress(done, total, x)
    return failed


def run_step(label, fn):
    client, model = need_ai()
    if not client:
        return
    try:
        with st.spinner(label):
            fn(client, model)
    except Exception as e:
        flash("error", engine.friendly(e))
    persist()
    st.rerun()


def research_all(p):
    client, model = need_ai()
    if not client:
        st.rerun()
        return
    with st.status("Researching this for you…", expanded=True) as status:
        try:
            if not p.get("map"):
                status.write("Mapping the research landscape…")
                p["map"] = engine.build_map(client, model, p)
                persist()
            sugg = [s for s in (p["map"].get("landmark_papers") or []) if s.get("title")]
            picks = [s for s in sugg if s.get("confidence") != "Guessing"]
            if len(picks) < 3:
                picks = sugg
            for s in picks[:8]:
                add_suggested(p, s)
            todo = [x for x in p["papers"] if not x.get("card") and not x.get("unknown") and (x.get("text") or x.get("origin") == "knowledge")]
            bar = status.progress(0.0, text=f"Summarising {len(todo)} papers…")
            failed = summarise_many(p, todo, client, model,
                                    lambda d, n, x: bar.progress(d / n, text=f"Summarised {d} of {n}: {x['title'][:60]}"))
            persist()
            done = [x for x in p["papers"] if x.get("card")]
            if not done:
                raise engine.AIError("The AI couldn't summarise any of the suggested papers. Try Find more papers, or upload a PDF.")
            if len(done) >= 2:
                status.write("Comparing the papers and finding gaps…")
                p["synthesis"] = engine.synthesise(client, model, p)
                persist()
            status.write("Designing solutions from the evidence…")
            p["solutions"] = engine.design_solutions(client, model, p)
            persist()
            status.update(label="Research complete", state="complete")
            ss.view = "Solutions"
            flash("success", "Research complete. Your solutions are ready." + (f" {failed} paper(s) couldn't be summarised." if failed else ""))
        except Exception as e:
            status.update(label="Stopped", state="error")
            flash("error", engine.friendly(e))
            persist()
    st.rerun()


def read_upload(f):
    data = f.getvalue()
    if f.name.lower().endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        text = []
        for page in reader.pages[:40]:
            text.append(page.extract_text() or "")
            if sum(len(t) for t in text) > 80000:
                break
        return "\n".join(text)
    return data.decode("utf-8", errors="ignore")


def guess_title(text, fallback):
    for line in (text or "").splitlines():
        s = line.strip()
        if 15 < len(s) < 200 and not re.match(r"^(arxiv|\d|http|doi)", s, re.I):
            return s
    return fallback


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    md('<div class="pb-logo">Paper Bench</div><div class="pb-tag">Problem → papers → build</div>')
    ids = [p["id"] for p in ss.projects]
    names = {p["id"]: p["name"] for p in ss.projects}
    if ss.cur not in ids:
        ss.cur = ids[0]
    ss.cur = st.radio("Projects", ids, index=ids.index(ss.cur), format_func=lambda i: names[i])

    with st.expander("New project", expanded=False):
        with st.form("newproj", clear_on_submit=True):
            n_name = st.text_input("Name", placeholder="e.g. Reduce delivery complaints")
            n_problem = st.text_area("The business problem", height=120,
                                     placeholder="Describe the real problem, not the solution you have in mind. What's hard about it? What outcome matters?")
            n_ctx = st.text_input("Context (optional)", placeholder="Industry, data you have, scale")
            n_auto = st.checkbox("Research it for me right away", value=True)
            if st.form_submit_button("Create project", type="primary"):
                if n_name.strip() and n_problem.strip():
                    p = store.new_project(n_name, n_problem, n_ctx)
                    ss.projects.insert(0, p)
                    ss.cur, ss.view = p["id"], "Map"
                    ss.autorun = p["id"] if n_auto else None
                    persist()
                    st.rerun()
                else:
                    st.warning("Add a name and a problem.")

    with st.expander("Settings", expanded=False):
        provs = list(engine.PROVIDERS)
        cur_prov = provider()
        picked_prov = st.radio("AI provider", provs, index=provs.index(cur_prov),
                               format_func=lambda k: engine.PROVIDERS[k]["label"])
        if picked_prov != cur_prov:
            ss.provider = picked_prov
            ss.model = ""
            st.rerun()
        info = engine.PROVIDERS[picked_prov]
        if _env(info["key"]):
            st.caption(f"{info['name']} is connected through your Streamlit secrets.")
        else:
            if picked_prov == "gemini":
                st.caption("Get a free key at aistudio.google.com/apikey (Google account, no card needed).")
            st.text_input(f"{info['name']} API key", type="password", key=f"key_{picked_prov}",
                          help=f"Kept only for this browser session. For a deployed app, add {info['key']} to Streamlit secrets.")
        st.text_input("Model", key="model", placeholder=info["model"],
                      help=f"Leave blank for {info['model']}.")

    with st.expander("Your data", expanded=False):
        st.download_button("Download all projects", json.dumps(ss.projects, ensure_ascii=False, indent=1),
                           file_name="paper-bench-projects.json", mime="application/json", use_container_width=True)
        up = st.file_uploader("Restore from a download", type=["json"], key="restore")
        if up is not None and st.button("Restore these projects", use_container_width=True):
            try:
                data = json.loads(up.getvalue())
                assert isinstance(data, list) and all("id" in x for x in data)
                ss.projects = data
                ss.cur = data[0]["id"]
                persist()
                flash("success", f"Restored {len(data)} projects.")
                st.rerun()
            except Exception:
                st.error("That file isn't a Paper Bench download.")
        if st.button("Restore the 5 starter projects", use_container_width=True):
            ss.projects = store.reset_demos(ss.projects)
            ss.cur = ss.projects[0]["id"]
            persist()
            st.rerun()
        st.caption("Projects are saved to data/projects.json. On Streamlit Community Cloud that file resets when the app restarts, so download a copy of anything you want to keep.")

# ------------------------------------------------------------------ main
p = current()
for kind, msg in ss.flash:
    getattr(st, kind)(msg)
ss.flash = []

md(f"""<div class="pb-hero"><div class="pb-eyebrow">Research project</div>
<h1>{esc(p['name'])}</h1><p class="problem">{esc(p['problem'])}</p>
{f'<div class="ctx">{esc(p["context"])}</div>' if p.get('context') else ''}</div>""")

a1, a2, a3 = st.columns([1.4, 1.2, 1])
with a1:
    go = st.button("Research again" if p.get("solutions") else "Research this for me", type="primary", use_container_width=True,
                   help="Maps the topic, picks the key papers, summarises them, compares them and designs solutions.")
with a2:
    st.download_button("Download brief (.md)", store.to_markdown(p), file_name=re.sub(r"\W+", "-", p["name"].lower()) + ".md",
                       use_container_width=True)
with a3:
    if not p.get("demo"):
        if ss.confirm == "project":
            if st.button("Confirm delete", use_container_width=True):
                ss.projects = [x for x in ss.projects if x["id"] != p["id"]]
                ss.cur, ss.confirm = ss.projects[0]["id"], None
                persist()
                st.rerun()
        elif st.button("Delete project", use_container_width=True):
            ss.confirm = "project"
            st.rerun()

if go or ss.get("autorun") == p["id"]:
    ss.autorun = None
    research_all(p)

counts = {"Library": len(p.get("papers", []))}
labels = {v: (f"{v} ({counts[v]})" if v in counts else v) for v in VIEWS}
if hasattr(st, "segmented_control"):
    picked = st.segmented_control("View", VIEWS, default=ss.view, format_func=lambda v: labels[v],
                                  key=f"view-{p['id']}-{ss.view}", label_visibility="collapsed")
else:
    picked = st.radio("View", VIEWS, index=VIEWS.index(ss.view), format_func=lambda v: labels[v],
                      horizontal=True, key=f"view-{p['id']}-{ss.view}", label_visibility="collapsed")
if picked and picked != ss.view:
    ss.view = picked
    st.rerun()
view = ss.view


# ------------------------------------------------------------------ views
def view_map():
    m = p.get("map")
    if not m:
        md('<div class="pb-panel"><p class="pb-lead">No research map yet. The AI will reframe your problem, explain the terms '
           'researchers use, and suggest papers you can add with one click.</p></div>')
        if st.button("Build research map", type="primary"):
            def f(c, mo):
                p["map"] = engine.build_map(c, mo, p)
            run_step("Mapping the research landscape…", f)
        return
    md(f"""<div class="pb-panel"><div class="pb-label">The problem, as researchers would frame it</div>
<p class="pb-lead">{rich(m.get('reframed_problem'))}</p>
{f'<p class="pb-muted"><b>Why it is hard:</b> {rich(m.get("why_hard"))}</p>' if m.get('why_hard') else ''}</div>""")

    sugg = [s for s in (m.get("landmark_papers") or []) if s.get("title")]
    left = [s for s in sugg if not store.find_in_library(p, s["title"])]
    h1, h2, h3 = st.columns([3, 1.1, 1.3])
    h1.markdown("### Suggested papers")
    if left and h2.button(f"Add all {len(left)}", type="primary", use_container_width=True):
        def f(c, mo):
            new = [add_suggested(p, s) for s in left]
            summarise_many(p, [x for x in new if x], c, mo)
        run_step(f"Adding and summarising {len(left)} papers…", f)
    if h3.button("Find more papers", use_container_width=True):
        def f(c, mo):
            known = [s["title"] for s in sugg] + [x["title"] for x in p.get("papers", [])]
            more = engine.find_more(c, mo, p, known)
            fresh = [s for s in more if isinstance(s, dict) and s.get("title") and not any(store.norm(s["title"]) == store.norm(k) for k in known)]
            m["landmark_papers"] = (m.get("landmark_papers") or []) + fresh
            flash("success" if fresh else "info", f"Added {len(fresh)} new suggestions." if fresh else "No new papers found.")
        run_step("Finding more papers…", f)
    st.caption("Press Add and the AI summarises the paper for you from what it knows. No PDF, no reading. "
               "The label shows how sure the AI is that the paper exists; the links let you check.")
    for i, s in enumerate(sugg):
        c1, c2 = st.columns([5, 1.3], vertical_alignment="center")
        with c1:
            md(f"""<div style="margin:.2rem 0 .5rem"><span class="pb-sug-title">{esc(s['title'])}</span> {conf(s.get('confidence'))}<br>
<span class="pb-muted">{esc(s.get('authors'))}{' · ' + esc(s.get('year')) if s.get('year') else ''}</span><br>
<span>{rich(s.get('why'))}</span><br>{links(s['title'])}</div>""")
        with c2:
            x = store.find_in_library(p, s["title"])
            if x and x.get("card"):
                if st.button("✓ In library", key=f"in-{p['id']}-{i}", use_container_width=True):
                    ss.view, ss.open = "Library", x["id"]
                    st.rerun()
            elif x and x.get("unknown"):
                st.caption("The AI doesn't know this one well")
            elif x:
                if st.button("Summarise", key=f"sum-{p['id']}-{i}", use_container_width=True):
                    def f(c, mo, x=x):
                        summarise_many(p, [x], c, mo)
                    run_step("Summarising…", f)
            elif st.button("+ Add to library", key=f"add-{p['id']}-{i}", use_container_width=True):
                def f(c, mo, s=s):
                    new = add_suggested(p, s)
                    if summarise_many(p, [new], c, mo):
                        flash("warning", "Added, but the AI couldn't summarise it. Try again from the Library.")
                run_step(f"Adding and summarising: {s['title'][:60]}…", f)

    c1, c2 = st.columns(2)
    with c1:
        md(f'<div class="pb-panel"><div class="pb-label">Questions research can answer</div>{ul(m.get("sub_questions"))}</div>')
    with c2:
        terms = "".join(f'<li class="pb-term"><b>{esc(t.get("term"))}</b>: {rich(t.get("meaning"))}</li>' for t in m.get("concepts") or [])
        md(f'<div class="pb-panel"><div class="pb-label">Vocabulary to search with</div><ul>{terms}</ul></div>')
    qs = "".join(f'<li><b>{esc(q.get("query"))}</b>: {rich(q.get("purpose"))}<br>{links(q.get("query"))}</li>' for q in m.get("search_queries") or [])
    md(f'<div class="pb-panel"><div class="pb-label">Search queries</div><ul>{qs}</ul></div>')
    if m.get("adjacent_fields"):
        af = "".join(f'<li><b>{esc(a.get("field"))}</b>: {rich(a.get("why"))}</li>' for a in m["adjacent_fields"])
        md(f'<div class="pb-panel"><div class="pb-label">Adjacent fields worth raiding</div><ul>{af}</ul></div>')


def card_html(x):
    c = x.get("card") or {}
    score = max(0, min(5, int(float((c.get("relevance") or {}).get("score") or 0))))
    fit = '<span class="fit">' + "".join(f'<i class="{"on" if i <= score else ""}"></i>' for i in range(1, 6)) + "</span>"
    meta = " · ".join(esc(v) for v in [c.get("authors") or x.get("authors"), c.get("year") or x.get("year"), c.get("venue")] if v)
    if x.get("origin") == "knowledge":
        badge = f'<span class="src k">From {esc(x.get("by") or "Claude")}\'s knowledge</span> ' + conf(c.get("knowledge"))
    else:
        badge = '<span class="src">Read from full text</span>'
    out = f'<p class="pb-muted">{meta} &nbsp;{badge}</p>'
    if not c:
        return out
    out += f"""<p class="pb-lead"><b>{rich(c.get('one_liner'))}</b></p>
<div class="pb-label">In plain words</div><p>{rich(c.get('plain_summary'))}</p>
<div class="pb-label">Method</div><p>{rich(c.get('method'))}</p>
<div class="pb-label">Findings</div><ul>{''.join(f"<li>{rich(f.get('claim'))} {conf(f.get('confidence'))}</li>" for f in c.get('key_findings') or [])}</ul>
<div class="pb-label">Limits</div>{ul(c.get('limitations'))}
<div class="pb-borrow"><div class="pb-label">What you can borrow</div>{ul(c.get('builder_takeaways'))}
{f"<p><b>Weekend test:</b> {rich(c.get('weekend_test'))}</p>" if c.get('weekend_test') else ''}</div>
<p class="pb-muted"><b>Fit {score}/5</b> {fit} {rich((c.get('relevance') or {}).get('why'))}</p>"""
    if c.get("key_terms"):
        out += '<div class="pb-label">Terms</div><ul>' + "".join(
            f'<li><b>{esc(t.get("term"))}</b>: {rich(t.get("meaning"))}</li>' for t in c["key_terms"]) + "</ul>"
    return out


def view_library():
    papers = sorted(p.get("papers", []), key=lambda x: x["num"])
    unread = [x for x in papers if not x.get("card") and not x.get("unknown") and (x.get("text") or x.get("origin") == "knowledge")]
    h1, h2 = st.columns([3, 1.4])
    h1.markdown("### Paper library")
    if unread and h2.button(f"Summarise {len(unread)} unread", type="primary", use_container_width=True):
        run_step(f"Summarising {len(unread)} papers…", lambda c, mo: summarise_many(p, unread, c, mo))
    if not papers:
        md('<div class="pb-panel"><p class="pb-lead">No papers yet. Add them with one click from the Map, '
           'or press Research this for me at the top and the AI does every step.</p></div>')
    for x in papers:
        c = x.get("card")
        status = "" if c else (" · couldn't summarise" if x.get("unknown") else " · failed, try again" if x.get("failed") else " · not summarised")
        with st.expander(f"P{x['num']} · {(c or {}).get('title') or x['title']}{status}", expanded=ss.get("open") == x["id"]):
            md(card_html(x))
            if x.get("unknown"):
                st.info("The AI doesn't know this paper well enough to summarise it. Upload its PDF below for a proper read.")
            if x.get("origin") == "knowledge":
                md(f'<div class="pb-label">Check the source</div>{links((c or {}).get("title") or x["title"])}')
            b1, b2, _ = st.columns([1.2, 1, 3])
            if (x.get("text") or x.get("origin") == "knowledge") and b1.button(
                    "Summarise again" if c else "Try again", key=f"re-{x['id']}", use_container_width=True):
                ss.open = x["id"]
                run_step("Summarising…", lambda cl, mo, x=x: summarise_many(p, [x], cl, mo))
            if ss.confirm == x["id"]:
                if b2.button("Confirm remove", key=f"rmy-{x['id']}", use_container_width=True):
                    p["papers"] = [y for y in p["papers"] if y["id"] != x["id"]]
                    ss.confirm = None
                    persist()
                    st.rerun()
            elif b2.button("Remove", key=f"rm-{x['id']}", use_container_width=True):
                ss.confirm = x["id"]
                ss.open = x["id"]
                st.rerun()

    st.markdown("#### Have the full text?")
    st.caption("Upload PDFs or text for a deeper card than one written from memory. Text is read on the server, up to 40 pages each.")
    files = st.file_uploader("Upload papers", type=["pdf", "txt", "md"], accept_multiple_files=True, key=f"up-{p['id']}",
                             label_visibility="collapsed")
    if files and st.button(f"Add and summarise {len(files)} file(s)", type="primary"):
        def f(c, mo):
            new, bad = [], []
            for fl in files:
                try:
                    text = read_upload(fl)
                except Exception:
                    text = ""
                if len(text.strip()) < 200:
                    bad.append(fl.name)
                    continue
                new.append(store.new_paper(p, guess_title(text, fl.name.rsplit(".", 1)[0]), fl.name, text))
            if bad:
                flash("warning", "Couldn't read enough text from: " + ", ".join(bad) + ". If they're scanned PDFs, paste the text instead.")
            summarise_many(p, new, c, mo)
        run_step("Reading and summarising…", f)
    with st.expander("Paste text instead"):
        with st.form(f"paste-{p['id']}", clear_on_submit=True):
            t = st.text_input("Title")
            body = st.text_area("Text", height=160, placeholder="Paste at least the abstract, method and conclusion.")
            if st.form_submit_button("Add and summarise", type="primary"):
                if t.strip() and len(body.strip()) >= 100:
                    new = store.new_paper(p, t.strip(), "Pasted text", body)
                    run_step("Summarising…", lambda c, mo: summarise_many(p, [new], c, mo))
                else:
                    st.warning("Add a title and at least a full abstract.")


def view_synthesis():
    s = p.get("synthesis")
    done = [x for x in p.get("papers", []) if x.get("card")]
    h1, h2 = st.columns([3, 1.4])
    h1.markdown("### Synthesis")
    if h2.button("Re-synthesise" if s else "Synthesise library", type="primary", use_container_width=True, disabled=len(done) < 2):
        run_step("Comparing papers and finding gaps…", lambda c, mo: p.__setitem__("synthesis", engine.synthesise(c, mo, p)))
    if not s:
        md(f'<div class="pb-panel"><p class="pb-lead">{"Add and summarise at least 2 papers first." if len(done) < 2 else "Ready when you are."}</p></div>')
        return
    md(f'<div class="pb-panel"><div class="pb-label">State of the field</div><p class="pb-lead">{rich(s.get("state_of_field"))}</p></div>')
    if s.get("approaches"):
        rows = "".join(f"<tr><td><b>{esc(a.get('name'))}</b><br>{chips(a.get('papers'))}</td><td>{rich(a.get('how'))}</td><td>{rich(a.get('strengths'))}</td>"
                       f"<td>{rich(a.get('weaknesses'))}</td><td>{rich(a.get('data_needs'))}</td></tr>" for a in s["approaches"])
        md(f'<div class="pb-label">Approaches compared</div><div class="pb-tablewrap"><table class="pb-table"><thead><tr><th>Approach</th><th>How</th>'
           f'<th>Strengths</th><th>Weaknesses</th><th>Data needed</th></tr></thead><tbody>{rows}</tbody></table></div>')
    c1, c2 = st.columns(2)
    with c1:
        items = "".join(f"<li>{rich(c.get('claim'))} {chips(c.get('papers'))} {conf(c.get('confidence'))}</li>" for c in s.get("consensus") or [])
        md(f'<div class="pb-panel"><div class="pb-label">Where papers agree</div><ul>{items or "<li>None found.</li>"}</ul></div>')
    with c2:
        items = "".join(f"<li><b>{esc(d.get('topic'))}</b>: {rich(d.get('sides'))}</li>" for d in s.get("disagreements") or [])
        md(f'<div class="pb-panel"><div class="pb-label">Where they clash</div><ul>{items or "<li>No direct disagreements.</li>"}</ul></div>')
    gaps = "".join(f'<div class="pb-borrow">{rich(g.get("gap"))}<br><b>Opportunity:</b> {rich(g.get("opportunity"))}</div>' for g in s.get("gaps") or [])
    md(f'<div class="pb-panel"><div class="pb-label">Gaps you could build into</div>{gaps}</div>')
    if s.get("reading_order"):
        ro = "".join(f'<li><span class="chip">{esc(r.get("paper"))}</span> {rich(r.get("why"))}</li>' for r in s["reading_order"])
        md(f'<div class="pb-panel"><div class="pb-label">Read them in this order</div><ol>{ro}</ol></div>')


def view_solutions():
    s = p.get("solutions")
    done = [x for x in p.get("papers", []) if x.get("card")]
    h1, h2 = st.columns([3, 1.4])
    h1.markdown("### Solutions")
    cons = st.text_input("Your constraints", value=p.get("constraints", ""), key=f"cons-{p['id']}",
                         placeholder="Team, budget, timeline, stack, data you can't use")
    if cons != p.get("constraints", ""):
        p["constraints"] = cons
        persist()
    if h2.button("Generate again" if s else "Generate solutions", type="primary", use_container_width=True, disabled=not done):
        run_step("Designing solutions from the evidence…", lambda c, mo: p.__setitem__("solutions", engine.design_solutions(c, mo, p)))
    if not s:
        md(f'<div class="pb-panel"><p class="pb-lead">{"Summarise at least one paper first." if not done else "Running the synthesis first gives sharper solutions, but you can generate now."}</p></div>')
        return
    r = s.get("recommendation") or {}
    if r:
        md(f'<div class="pb-reco"><div class="pb-label">Start here</div><div class="pick">{esc(r.get("pick"))}</div><p>{rich(r.get("why"))}</p></div>')
    pick = str(r.get("pick", "")).lower()
    for x in s.get("solutions") or []:
        e = x.get("experiment") or {}
        is_pick = pick and str(x.get("name", "")).lower() == pick
        steps = "".join(f"<li>{rich(h)}</li>" for h in x.get("how_it_works") or [])
        md(f"""<div class="pb-sol {'pick' if is_pick else ''}">
<h3>{esc(x.get('name'))}</h3>
<p><span class="effort">effort {esc(x.get('effort'))}</span> {conf(x.get('confidence'))} &nbsp;<span class="pb-muted">Grounded in</span> {chips(x.get('grounded_in'))}</p>
<p class="pb-lead">{rich(x.get('pitch'))}</p>
<div class="pb-label">How it works</div><ol>{steps}</ol>
{f"<p><b>Why it could win:</b> {rich(x.get('why_it_could_win'))}</p>" if x.get('why_it_could_win') else ''}
{('<div class="pb-label">Risks</div>' + ul(x.get('risks'))) if x.get('risks') else ''}
<div class="pb-borrow"><b>MVP:</b> {rich(x.get('mvp'))}</div>
<div class="pb-exp"><b>Hypothesis</b><span>{rich(e.get('hypothesis'))}</span><b>Metric</b><span>{rich(e.get('metric'))}</span>
<b>Success if</b><span>{rich(e.get('success_threshold'))}</span><b>Drop it if</b><span>{rich(e.get('change_our_mind'))}</span></div>
</div>""")


def view_ask():
    st.markdown("### Ask the library")
    st.caption("Question your papers. Answers cite the library so you can check them.")
    chat = p.setdefault("chat", [])
    if chat and st.button("Clear chat"):
        p["chat"] = []
        persist()
        st.rerun()
    for m in chat:
        with st.chat_message(m["role"]):
            md(rich(m["content"]).replace("\n", "<br>") if m["role"] == "user" else m["content"])
    if not chat:
        st.info("Try: “Which idea can we test fastest this week?” or “What would a sceptic say about these findings?”")
    q = st.chat_input("Ask about your papers…")
    if q:
        client, model = need_ai()
        if not client:
            st.rerun()
            return
        chat.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.write(q)
        with st.chat_message("assistant"):
            try:
                answer = st.write_stream(engine.chat_stream(client, model, p, chat))
                chat.append({"role": "assistant", "content": answer if isinstance(answer, str) else str(answer)})
            except Exception as e:
                chat.pop()
                st.error(engine.friendly(e))
        p["chat"] = chat[-40:]
        persist()


{"Map": view_map, "Library": view_library, "Synthesis": view_synthesis, "Solutions": view_solutions, "Ask": view_ask}[view]()

md('<p class="pb-foot">Papers added with one click are summarised from the AI model\'s knowledge, not the full text. Each card says so and '
   'carries confidence labels and links to check the source. Upload a PDF for a read of the full text.</p>')
