"""Quiet, editorial visual system: warm paper, charcoal and restrained green."""
import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>
        :root {
          --paper: #F3F2ED;
          --panel: #FFFFFF;
          --ink: #242B27;
          --muted: #707A73;
          --line: #E2E3DC;
          --forest: #315B46;
          --forest-soft: #E8F0EA;
          --amber: #A77736;
          --amber-soft: #F5EFE4;
          --red: #A64E43;
          --red-soft: #F7ECE9;
        }
        html, body, [class*="css"] { font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
        .stApp { background: var(--paper); color: var(--ink); }
        [data-testid="stHeader"] { background: rgba(243,242,237,0.92); }
        [data-testid="stSidebar"] { background: #EAE9E2; border-right: 1px solid #D9DCD5; }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1.1rem; }
        .block-container { max-width: 1440px; padding-top: 2.75rem !important; padding-bottom: 3rem; }
        [data-testid="stAppViewContainer"] > .main { overflow: visible; }
        [data-testid="stHeader"] { height: 2.75rem; }
        h1, h2, h3 { color: var(--ink) !important; letter-spacing: -0.035em; }
        h1 { font-size: 2.05rem !important; font-weight: 690 !important; }
        h2 { font-size: 1.38rem !important; font-weight: 650 !important; }
        h3 { font-size: 1.08rem !important; font-weight: 650 !important; }
        p, li, label { color: var(--ink); }
        [data-testid="stMetric"] { background: var(--panel); border: 1px solid var(--line); padding: 16px 18px; border-radius: 11px; box-shadow: 0 1px 2px rgba(30,40,32,0.025); }
        [data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.79rem; }
        [data-testid="stMetricValue"] { color: var(--ink) !important; font-weight: 680; }
        [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] { gap: 1rem; }
        /* Explicitly set button text colour; Streamlit theme styles can otherwise
           override it and produce dark text on the forest-green button. */
        div[data-testid="stButton"] > button,
        div[data-testid="stDownloadButton"] > button,
        div.stButton > button,
        div.stDownloadButton > button {
          border-radius: 8px; border: 1px solid #315B46;
          background: #315B46 !important; color: #FFFFFF !important;
          -webkit-text-fill-color: #FFFFFF !important;
          font-weight: 650; min-height: 2.45rem;
        }
        div[data-testid="stButton"] > button *,
        div[data-testid="stDownloadButton"] > button *,
        div.stButton > button *, div.stDownloadButton > button * {
          color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important;
        }
        div[data-testid="stButton"] > button:hover,
        div[data-testid="stDownloadButton"] > button:hover,
        div.stButton > button:hover, div.stDownloadButton > button:hover {
          background: #274B39 !important; border-color: #274B39 !important;
          color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important;
        }
        div[data-testid="stButton"] > button:focus,
        div[data-testid="stDownloadButton"] > button:focus {
          box-shadow: 0 0 0 3px rgba(49,91,70,.22); outline: none;
        }
        div[data-testid="stButton"] > button:disabled {
          background: #DCE4DE !important; border-color: #DCE4DE !important;
          color: #68766C !important; -webkit-text-fill-color: #68766C !important;
          opacity: 1;
        }
        [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stSelectbox"] div[data-baseweb="select"] { border-radius: 7px; }
        [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
        [data-testid="stTabs"] button { font-weight: 600; }
        hr { border-color: var(--line); }
        .brand-lockup { display:flex; gap:10px; align-items:center; padding: 4px 2px 20px 2px; }
        .brand-mark { width:34px; height:34px; border-radius:9px; background:#315B46; color:#fff; display:flex; align-items:center; justify-content:center; font-size:17px; font-weight:750; }
        .brand-name { color:#242B27; font-size:17px; line-height:1.1; font-weight:750; letter-spacing:-.03em; }
        .brand-sub { color:#748077; font-size:10px; letter-spacing:.11em; text-transform:uppercase; margin-top:4px; }
        .eyebrow { color:#728078; font-size:11px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; margin-bottom:8px; }
        .page-subtitle { color:#6E786F; font-size:14px; margin-top:-10px; margin-bottom:22px; }
        .surface { background:#fff; border:1px solid #E2E3DC; border-radius:11px; padding:17px 18px; box-shadow:0 1px 2px rgba(31,42,34,.025); }
        .surface-title { font-size:14px; font-weight:700; color:#29322C; margin-bottom:4px; }
        .surface-copy { font-size:12px; color:#778078; line-height:1.55; }
        .metric-kicker { color:#768078; font-size:11px; letter-spacing:.08em; text-transform:uppercase; font-weight:700; }
        .metric-number { font-size:28px; font-weight:720; color:#263029; margin-top:5px; letter-spacing:-.04em; }
        .metric-note { font-size:11px; color:#7A827B; margin-top:2px; }
        .status-pill { display:inline-block; border-radius:99px; padding:4px 9px; font-size:10px; font-weight:750; letter-spacing:.05em; }
        .pill-green { background:#E8F0EA; color:#315B46; }
        .pill-red { background:#F7ECE9; color:#A64E43; }
        .pill-amber { background:#F5EFE4; color:#93672E; }
        .pill-grey { background:#EFF0EC; color:#667169; }
        .callout { border-left:3px solid #315B46; background:#EDF2ED; padding:12px 15px; border-radius:0 8px 8px 0; color:#3C5043; font-size:13px; line-height:1.5; }
        .callout.warning { border-left-color:#A77736; background:#F6F0E6; color:#6D5738; }
        .callout.danger { border-left-color:#A64E43; background:#F7ECE9; color:#75463F; }
        .step-number { color:#315B46; font-weight:750; font-size:12px; letter-spacing:.08em; }
        .small-muted { color:#7A827B; font-size:11px; }
        .sidebar-note { font-size:11px; color:#6E796F; line-height:1.5; padding:9px 10px; background:rgba(255,255,255,.52); border:1px solid #DDDFD7; border-radius:8px; }
        [data-testid="stSidebar"] [data-testid="stRadio"] label { font-size:13px; font-weight:550; }
        [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] { gap:2px; }
        code { color:#315B46; background:#EEF1EC; }
        a { color:#315B46 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(section: str, title: str, subtitle: str):
    st.markdown(f'<div class="eyebrow">{section}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def surface(title: str, copy: str = ""):
    st.markdown(
        f'<div class="surface"><div class="surface-title">{title}</div><div class="surface-copy">{copy}</div></div>',
        unsafe_allow_html=True,
    )
