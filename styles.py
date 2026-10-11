"""Brand styling taken from devinder-kaur.vercel.app: navy, teal, sky, beige; Playfair Display, PT Serif, Pinyon Script."""

CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Pinyon+Script&family=Playfair+Display:wght@400;500;600&family=PT+Serif:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>
:root{
  --navy:#2F4156; --teal:#567C8D; --teal-ink:#44697A; --sky:#C8D9E6; --beige:#F5EFEB; --white:#FFFFFF; --rule:#DCD3CC;
  --good:#2E6B4F; --warn:#9A5B00;
  --serif:"Playfair Display", Georgia, "Times New Roman", serif;
  --sans:"PT Serif", Georgia, "Times New Roman", serif;
  --script:"Pinyon Script", "Brush Script MT", cursive;
}
html, body, .stApp, [data-testid="stAppViewContainer"], .stMarkdown, p, li, label, input, textarea, button, select,
[data-testid="stWidgetLabel"], [data-baseweb="tab"], .stAlert { font-family: var(--sans) !important; }
.stApp { background: var(--beige); color: var(--navy); }
h1, h2, h3, h4, .pb-h { font-family: var(--serif) !important; font-weight: 500 !important; color: var(--navy); letter-spacing: -0.01em; }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.6rem; max-width: 1120px; }
a { color: var(--teal-ink); text-decoration-color: var(--teal); text-underline-offset: 3px; }

/* sidebar */
section[data-testid="stSidebar"] { background: var(--navy); }
section[data-testid="stSidebar"] * { color: var(--white); }
section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] textarea { color: var(--navy) !important; background: var(--white) !important; }
section[data-testid="stSidebar"] [data-testid="stExpander"] details { background: rgba(255,255,255,.06); border-color: rgba(200,217,230,.35); }
section[data-testid="stSidebar"] .stButton button, section[data-testid="stSidebar"] .stDownloadButton button, section[data-testid="stSidebar"] .stFormSubmitButton button {
  background: var(--sky) !important; color: var(--navy) !important; border-color: var(--sky) !important; }
section[data-testid="stSidebar"] .stButton button *, section[data-testid="stSidebar"] .stDownloadButton button *, section[data-testid="stSidebar"] .stFormSubmitButton button * { color: var(--navy) !important; }
.pb-logo { font-family: var(--script); font-size: 3.1rem; line-height: .9; color: var(--white); margin: .2rem 0 .1rem; }
.pb-tag { color: var(--sky) !important; font-size: .92rem; margin-bottom: .6rem; }

/* buttons: pill, navy, teal on hover (as on the site) */
.stButton button, .stDownloadButton button, .stFormSubmitButton button {
  border-radius: 999px !important; border: 1.5px solid var(--navy) !important; font-weight: 700 !important;
  background: transparent; color: var(--navy); padding: .45rem 1.1rem; }
.stButton button:hover, .stDownloadButton button:hover { background: var(--navy) !important; color: var(--white) !important; }
.stButton button[kind="primary"], [data-testid="stBaseButton-primary"], .stFormSubmitButton button[kind="primaryFormSubmit"], [data-testid="stBaseButton-primaryFormSubmit"] {
  background: var(--navy) !important; color: var(--white) !important; }
.stButton button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover { background: var(--teal) !important; border-color: var(--teal) !important; }
.stButton button:disabled { opacity: .45; }

/* hero */
.pb-hero { background: var(--navy); color: var(--white); border-radius: 22px; padding: 1.7rem 1.9rem 1.6rem; margin-bottom: 1rem; position: relative; overflow: hidden; }
.pb-hero::after { content:""; position:absolute; inset:0; pointer-events:none;
  background: repeating-linear-gradient(90deg, rgba(200,217,230,.07) 0 2px, transparent 2px 14px); }
.pb-eyebrow { font-size: .78rem; letter-spacing: .12em; text-transform: uppercase; color: var(--sky); font-weight: 700; }
.pb-hero h1 { color: var(--white) !important; font-size: clamp(1.7rem, 3vw, 2.4rem) !important; margin: .35rem 0 .6rem !important; padding: 0 !important; }
.pb-hero .problem { color: var(--sky); max-width: 70ch; font-size: 1.04rem; margin: 0; }
.pb-hero .ctx { color: rgba(255,255,255,.75); font-size: .9rem; margin-top: .5rem; }

/* panels and cards */
.pb-panel { background: var(--white); border: 1px solid var(--rule); border-radius: 16px; padding: 1.1rem 1.25rem; margin-bottom: .9rem; }
.pb-label { font-size: .74rem; letter-spacing: .1em; text-transform: uppercase; color: var(--teal-ink); font-weight: 700; margin-bottom: .35rem; }
.pb-lead { font-size: 1.08rem; max-width: 70ch; }
.pb-muted { color: var(--teal-ink); font-size: .93rem; }
.pb-borrow { background: #EAF1F6; border-radius: 12px; padding: .8rem 1rem; margin: .6rem 0; }
.pb-reco { border-left: 5px solid var(--teal); background: var(--white); border-radius: 0 16px 16px 0; padding: 1rem 1.2rem; margin-bottom: 1rem; border-top:1px solid var(--rule); border-right:1px solid var(--rule); border-bottom:1px solid var(--rule); }
.pb-reco .pick { font-family: var(--serif); font-size: 1.35rem; }
.pb-sol { background: var(--white); border: 1px solid var(--rule); border-radius: 16px; padding: 1.1rem 1.25rem; margin-bottom: .9rem; }
.pb-sol.pick { border: 2px solid var(--teal); }
.pb-sol h3 { font-size: 1.35rem !important; margin: 0 0 .3rem !important; padding: 0 !important; }
.pb-exp { background: var(--beige); border-radius: 12px; padding: .8rem 1rem; display: grid; grid-template-columns: max-content 1fr; gap: .35rem 1rem; margin-top: .6rem; }
.pb-exp b { font-size: .74rem; letter-spacing: .08em; text-transform: uppercase; color: var(--teal-ink); }
@media (max-width: 640px){ .pb-exp { grid-template-columns: 1fr; } }
.pb-sug-title { font-family: var(--serif); font-size: 1.08rem; font-weight: 500; }
.pb-term b { font-weight: 700; }

/* chips */
.chip { display:inline-block; font-size:.78rem; font-weight:700; background: var(--sky); color: var(--navy); border-radius: 6px; padding: 0 .4rem; margin: 0 .1rem; }
.conf { display:inline-block; font-size:.72rem; font-weight:700; border:1.5px solid currentColor; border-radius:999px; padding:0 .5rem; white-space:nowrap; vertical-align: 1px; }
.conf-certain { color: var(--good); } .conf-likely { color: var(--teal-ink); } .conf-guessing { color: var(--warn); }
.src { display:inline-block; font-size:.7rem; letter-spacing:.06em; text-transform:uppercase; font-weight:700; border-radius:6px; padding:.05rem .45rem; background: #EDE4DE; color: var(--navy); }
.src.k { background: var(--sky); }
.effort { font-size:.75rem; font-weight:700; background: var(--beige); border-radius:6px; padding:.05rem .45rem; }
.links a { margin-right: .9rem; font-size: .9rem; }
.fit i { display:inline-block; width:7px; height:14px; border-radius:2px; background: var(--rule); margin-right:2px; vertical-align:-2px; }
.fit i.on { background: var(--teal); }

/* tables */
.pb-table { width:100%; border-collapse: collapse; font-size: .94rem; background: var(--white); }
.pb-table th { text-align:left; font-size:.72rem; letter-spacing:.08em; text-transform:uppercase; color: var(--teal-ink); background: var(--beige); padding:.6rem .7rem; border-bottom:1px solid var(--rule); }
.pb-table td { padding:.65rem .7rem; border-bottom:1px solid var(--rule); vertical-align: top; }
.pb-tablewrap { overflow-x:auto; border:1px solid var(--rule); border-radius:16px; margin-bottom: .9rem; }

/* expanders, inputs, view switcher */
[data-testid="stExpander"] details { background: var(--white); border: 1px solid var(--rule) !important; border-radius: 16px !important; }
[data-testid="stExpander"] summary p { font-family: var(--serif) !important; font-size: 1.05rem; }
.stTextInput input, .stTextArea textarea { border-radius: 10px !important; }
[data-testid="stButtonGroup"] button, [data-testid="stSegmentedControl"] button { border-radius: 999px !important; }
[data-testid="stBaseButton-segmented_controlActive"], [data-testid="stBaseButton-pillsActive"] { background: var(--navy) !important; color: var(--white) !important; border-color: var(--navy) !important; }
[data-testid="stBaseButton-segmented_controlActive"] * { color: var(--white) !important; }
div[role="radiogroup"] label p { font-weight: 700; }
[data-testid="stChatMessage"] { background: var(--white); border: 1px solid var(--rule); border-radius: 16px; }
.pb-foot { color: var(--teal-ink); font-size: .85rem; margin-top: 2rem; max-width: 75ch; }
</style>
"""
