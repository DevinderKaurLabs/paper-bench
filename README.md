# Paper Bench

Turn a business problem into research-backed solutions. Describe the problem, and the AI:

1. **Maps** it the way researchers would: sub-questions, vocabulary, search queries and the key papers.
2. **Adds papers in one click** and summarises each one: plain summary, method, findings with confidence labels, limits, what you can borrow, a weekend test.
3. **Synthesises** the library: approaches compared, where papers agree and clash, and gaps you can build into.
4. **Designs 3 solutions** grounded in the papers, each with an MVP and an experiment that says when to drop it.
5. **Answers questions** about your library, with citations.

Press **Research this for me** and it does all five steps. Five complete starter projects are preloaded:

| Project | Papers |
|---|---|
| Loyalty lapse: who to save, and with what | Schmittlein 1987, Fader 2005, Ascarza 2018, Verbeke 2012 |
| Is our paid media actually driving sales? | Lewis & Rao 2015, Gordon et al. 2019, Johnson et al. 2017, Jin et al. 2017, Brodersen et al. 2015 |
| Next-best offer across app, email and WhatsApp | Li et al. 2010, Chapelle & Li 2011, Hu et al. 2008, Covington et al. 2016 |
| Turn customer reviews into product decisions | Hu & Liu 2004, Chevalier & Mayzlin 2006, Devlin et al. 2019, Grootendorst 2022 |
| A support assistant that answers from our policies | Lewis et al. 2020, Karpukhin et al. 2020, Liu et al. 2024, Es et al. 2024 |

The starter projects work without any API key. New research uses **Google Gemini's free tier** by default: a free key from Google AI Studio, no credit card. Anthropic Claude is supported as an option.

**About the paper cards:** papers added with one click are summarised from the AI model's knowledge, not the full text. Each card says so, carries confidence labels, and links to Google Scholar, Semantic Scholar and arXiv so you can check. Upload the PDF when you want a read of the full text.

## Get a free Gemini key

1. Go to https://aistudio.google.com/apikey and sign in with a Google account.
2. Click **Create API key**. Copy it (it starts with `AIza`).

Free-tier notes: Google sets low, unpublished request limits per project (see them in AI Studio). Paper Bench uses about 4 requests per full research run and waits once if it hits a per-minute limit. Daily limits reset at midnight Pacific time (11am Dubai). On the free tier, Google may use prompts to improve its products, so don't paste confidential data.

## Run it on your computer (Windows PowerShell)

```powershell
cd "C:\better than busy\paper-bench"        # wherever you unzipped it
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
notepad .streamlit\secrets.toml               # paste your key: GEMINI_API_KEY = "AIza..."
streamlit run app.py
```

It opens at http://localhost:8501. You can also paste the key in the sidebar under **Settings** instead of using secrets.toml.

## Put it online (GitHub + Streamlit Community Cloud)

1. Create an empty repo on GitHub (for example `DevinderKaurLabs/paper-bench`, no README) and push this folder. `.gitignore` keeps your key and local data out of git.
   ```powershell
   git init
   git add .
   git commit -m "Paper Bench"
   git branch -M main
   git remote add origin https://github.com/DevinderKaurLabs/paper-bench.git
   git push -u origin main
   ```
2. Go to share.streamlit.io → **Create app** → pick the repo, branch `main`, main file `app.py`.
3. Under **Advanced settings → Secrets**, paste:
   ```toml
   GEMINI_API_KEY = "AIza..."
   ```
4. Deploy.

**Want no key at all?** Deploy without the secret. The five starter projects work for everyone, and visitors who want new research paste their own free Gemini key in Settings.

**Saving on Streamlit Cloud:** projects are saved to `data/projects.json`, and Streamlit Cloud resets that file when the app restarts or redeploys. Use **Your data → Download all projects** to keep a copy and **Restore** to load it back. Running locally, projects persist.

## Brand

Colours and fonts come from devinder-kaur.vercel.app: navy `#2F4156`, teal `#567C8D`, sky `#C8D9E6`, beige `#F5EFEB`, white; Playfair Display for headings, PT Serif for body text, Pinyon Script for the logo. Edit `styles.py` to change them; `.streamlit/config.toml` sets the matching base theme.

## Files

| File | What it does |
|---|---|
| `app.py` | The Streamlit interface |
| `engine.py` | Prompts and AI calls for Gemini or Claude (no Streamlit; easy to test) |
| `store.py` | Saving, loading, and the Markdown brief export |
| `demo_data.py` | The five demo projects |
| `styles.py` | Brand CSS |

Default model is `gemini-3.8-flash`. Change it in Settings or with `PAPER_BENCH_MODEL`. To use Claude instead, add `ANTHROPIC_API_KEY` and `PAPER_BENCH_PROVIDER = "claude"` to secrets, or pick it in Settings.
