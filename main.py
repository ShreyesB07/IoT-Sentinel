"""Launch the IoT Sentinel Streamlit application."""
import streamlit as st

from config import APP_NAME, APP_SUBTITLE, DB_PATH
from core.engine import IoTSentinelEngine
from core.mqtt_bridge import MQTTBridge
from dashboard.styles import apply_styles
from dashboard import views

st.set_page_config(page_title=APP_NAME, page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")
apply_styles()

if "engine" not in st.session_state:
    st.session_state.engine = IoTSentinelEngine(DB_PATH)
if "mqtt_bridge" not in st.session_state:
    st.session_state.mqtt_bridge = MQTTBridge()
if "page" not in st.session_state:
    st.session_state.page = "Overview"

engine = st.session_state.engine
mqtt_bridge = st.session_state.mqtt_bridge

with st.sidebar:
    st.markdown(
        '<div class="brand-lockup"><div class="brand-mark">IS</div><div><div class="brand-name">IoT Sentinel</div><div class="brand-sub">Network security lab</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="eyebrow">WORKSPACE</div>', unsafe_allow_html=True)
    pages = ["Overview", "Devices & controls", "Traffic monitor", "Attack simulation lab", "Security events", "Reports & analytics", "Local MQTT bridge", "How it works"]
    page = st.radio("Navigation", pages, label_visibility="collapsed", key="navigation", index=pages.index(st.session_state.page) if st.session_state.page in pages else 0)
    st.session_state.page = page
    st.divider()
    st.markdown('<div class="eyebrow">LAB STATUS</div>', unsafe_allow_html=True)
    stats = engine.summary()
    st.markdown(f'<div class="sidebar-note"><strong>{stats["total"]:,}</strong> requests in audit history<br><strong>{stats["blocked"]:,}</strong> blocked by security rules</div>', unsafe_allow_html=True)
    mqtt_text = "MQTT connected" if mqtt_bridge.status() else "Built-in simulator active"
    mqtt_class = "pill-green" if mqtt_bridge.status() else "pill-grey"
    st.markdown(f'<div style="margin-top:10px;"><span class="status-pill {mqtt_class}">{mqtt_text.upper()}</span></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="eyebrow">LAB CONTROLS</div>', unsafe_allow_html=True)
    if st.button("Reset lab and clear history", use_container_width=True, help="Restores virtual devices and permanently clears this local audit history."):
        engine.reset_lab()
        st.session_state.pop("last_attack", None)
        st.session_state.pop("last_attack_name", None)
        st.success("The lab has been reset.")
        st.rerun()
    st.markdown('<div class="sidebar-note">Local learning environment only. Demo credentials are public examples and must never be reused in real systems.</div>', unsafe_allow_html=True)
    st.caption("ITCN · Unit 3 · Software prototype")

if page == "Overview":
    views.overview_page(engine, mqtt_bridge)
elif page == "Devices & controls":
    views.devices_page(engine, mqtt_bridge)
elif page == "Traffic monitor":
    views.traffic_page(engine, mqtt_bridge)
elif page == "Attack simulation lab":
    views.attack_lab_page(engine, mqtt_bridge)
elif page == "Security events":
    views.security_events_page(engine)
elif page == "Reports & analytics":
    views.reports_page(engine)
elif page == "Local MQTT bridge":
    views.mqtt_page(engine, mqtt_bridge)
elif page == "How it works":
    views.about_page()
