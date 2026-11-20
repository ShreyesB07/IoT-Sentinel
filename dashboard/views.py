"""Streamlit pages for the IoT Sentinel learning lab."""
from __future__ import annotations

from datetime import datetime
import html
import json

import pandas as pd
import plotly.express as px
import streamlit as st

from config import CLIENTS, MQTT_HOST, MQTT_PORT
from security.rules import THREAT_RULES
from simulator.traffic import command, generate_normal_traffic, run_attack
from dashboard.styles import page_header


DISPLAY_ACTIONS = {
    "Set power": "set_power",
    "Set brightness": "set_brightness",
    "Lock door": "lock",
    "Unlock door": "unlock",
    "Set fan speed": "set_speed",
}


def _events(engine, limit=5000):
    return engine.store.list_events(limit=limit)


def _event_frame(events):
    if not events:
        return pd.DataFrame(columns=["Time", "Source", "Target", "Action", "Result", "Severity", "Event", "Reason"])
    df = pd.DataFrame(events)
    df["Time"] = pd.to_datetime(df["timestamp"], errors="coerce").dt.strftime("%H:%M:%S")
    df["Source"] = df["source_id"]
    df["Target"] = df["target_id"]
    df["Action"] = df["action"].str.replace("_", " ")
    df["Result"] = df["status"]
    df["Severity"] = df["severity"]
    df["Event"] = df["event_type"].str.replace("_", " ")
    df["Reason"] = df["reason"]
    return df[["Time", "Source", "Target", "Action", "Result", "Severity", "Event", "Reason"]]


def _mirror_events(events, mqtt_bridge):
    if mqtt_bridge and mqtt_bridge.status():
        for event in events:
            mqtt_bridge.publish_event(event)


def _metric_row(engine):
    stats = engine.summary()
    total = stats["total"]
    blocked = stats["blocked"]
    attempts = stats["attack_attempts"]
    detected = stats["detected_attacks"]
    block_rate = (blocked / total * 100) if total else 0
    detection_rate = (detected / attempts * 100) if attempts else 0
    cols = st.columns(4)
    cols[0].metric("Requests inspected", f"{total:,}", help="All commands recorded by the local gateway simulator.")
    cols[1].metric("Commands blocked", f"{blocked:,}", help="Commands rejected by at least one security rule.")
    cols[2].metric("Attack events detected", f"{detected:,}", help="Synthetic attack-labelled requests that triggered a detection rule.")
    cols[3].metric("Attack detection rate", f"{detection_rate:.0f}%" if attempts else "—", help="Detected attack-labelled requests divided by all attack-labelled requests in this demo session.")
    st.caption(f"Overall block rate: {block_rate:.1f}% of all inspected requests. Detection figures are based on the simulator's known scenario labels, not a real-world benchmark.")


def overview_page(engine, mqtt_bridge):
    page_header("MONITORING / OVERVIEW", "Security overview", "A quick view of the virtual IoT installation, command activity and security decisions.")
    stats = engine.summary()
    _metric_row(engine)

    if stats["high_alerts"]:
        st.markdown('<div class="callout danger"><strong>Attention required.</strong> High or critical security events are present in the audit log. Review the Security events page for the source and reason.</div>', unsafe_allow_html=True)
    elif stats["total"]:
        st.markdown('<div class="callout"><strong>Lab is running.</strong> Recent commands are being checked by the gateway rules. Blocked commands do not change actuator state.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="callout"><strong>Ready for your first test.</strong> Generate normal traffic or open the Attack lab to see how the gateway handles suspicious commands.</div>', unsafe_allow_html=True)

    left, right = st.columns([1.55, 1])
    with left:
        st.subheader("Recent command activity")
        events = _events(engine, 80)
        if events:
            chart_df = pd.DataFrame(events)
            chart_df["Time"] = pd.to_datetime(chart_df["timestamp"], errors="coerce")
            chart_df = chart_df.dropna(subset=["Time"]).sort_values("Time")
            if not chart_df.empty:
                chart_df["Result"] = chart_df["status"].map({"ALLOWED": "Accepted", "BLOCKED": "Blocked"})
                fig = px.scatter(chart_df, x="Time", y="source_id", color="Result",
                                 hover_data={"target_id": True, "action": True, "reason": True, "Time": True},
                                 color_discrete_map={"Accepted": "#47765C", "Blocked": "#B25C4F"})
                fig.update_traces(marker=dict(size=10, opacity=.8))
                fig.update_layout(height=290, margin=dict(l=8, r=8, t=15, b=8),
                                  paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF",
                                  font_color="#566158", legend_title_text="Decision",
                                  xaxis_title="Time", yaxis_title="Request source")
                fig.update_xaxes(showgrid=True, gridcolor="#EEF0EA")
                fig.update_yaxes(showgrid=False)
                st.plotly_chart(fig, use_container_width=True)
            st.dataframe(_event_frame(events).head(7), use_container_width=True, hide_index=True)
        else:
            st.info("No commands yet. Use the buttons below to create a small sample of normal IoT traffic.")
            if st.button("Generate 8 normal requests", type="primary", key="overview_normal"):
                generated = generate_normal_traffic(engine, 8)
                _mirror_events(generated, mqtt_bridge)
                st.rerun()
    with right:
        st.subheader("Virtual installation")
        for device in engine.get_devices():
            badge = "pill-green" if device["state"].get("status") == "Online" else "pill-grey"
            state_text = _device_state(device)
            st.markdown(
                f'<div class="surface" style="padding:12px 14px;margin-bottom:9px;">'
                f'<div style="display:flex;justify-content:space-between;gap:8px;align-items:center;">'
                f'<strong style="font-size:13px;color:#2b342e;">{html.escape(device["name"])}</strong>'
                f'<span class="status-pill {badge}">ONLINE</span></div>'
                f'<div class="surface-copy" style="margin-top:5px;">{html.escape(device["zone"])} · {html.escape(device["kind"])}</div>'
                f'<div style="font-size:12px;color:#566158;margin-top:7px;">{html.escape(state_text)}</div></div>',
                unsafe_allow_html=True,
            )
        st.caption("All devices shown here are virtual. Their state changes only when a command passes the security checks.")

    st.divider()
    st.subheader("Suggested first run")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**01 · Normal traffic**")
        st.caption("Send a few authorised commands and inspect the accepted messages.")
        if st.button("Create normal traffic", key="overview_traffic"):
            generated = generate_normal_traffic(engine, 8)
            _mirror_events(generated, mqtt_bridge)
            st.rerun()
    with col2:
        st.markdown("**02 · Try an attack**")
        st.caption("Run a controlled scenario against the virtual front-door lock.")
        if st.button("Try unauthorised access", key="overview_attack"):
            generated = run_attack(engine, "unauthorized_access")
            _mirror_events(generated, mqtt_bridge)
            st.session_state["last_attack"] = generated
            st.rerun()
    with col3:
        st.markdown("**03 · Review the decision**")
        st.caption("Open **Security events** from the left navigation to read why each command was accepted or blocked.")


def _device_state(device):
    state = device["state"]
    if "power" in state:
        state_part = "On" if state["power"] else "Off"
        if "brightness" in state:
            return f"Power: {state_part} · Brightness: {state['brightness']}%"
        if "speed" in state:
            return f"Power: {state_part} · Fan speed: {state['speed']}/5"
        return f"Power: {state_part}"
    if "locked" in state:
        return "Locked" if state["locked"] else "Unlocked"
    if "temperature_c" in state:
        return f"Temperature: {state['temperature_c']} °C"
    if "humidity_pct" in state:
        return f"Humidity: {state['humidity_pct']}%"
    return "Gateway operational"


def devices_page(engine, mqtt_bridge):
    page_header("VIRTUAL INSTALLATION", "Devices & actuator controls", "Explore the simulated smart-home devices and send commands through the same security checks used by the gateway.")
    devices = engine.get_devices()
    cols = st.columns(3)
    for index, device in enumerate(devices):
        with cols[index % 3]:
            with st.container(border=True):
                st.markdown(f"**{device['name']}**")
                st.caption(f"{device['device_id']} · {device['zone']}")
                st.markdown(f'<span class="status-pill pill-green">ONLINE</span> <span class="status-pill pill-grey">{html.escape(device["kind"].upper())}</span>', unsafe_allow_html=True)
                st.write(_device_state(device))
                st.caption(device["description"])
                if device["actuator"]:
                    st.caption("Supported actions: " + ", ".join(a.replace("_", " ") for a in device["actions"]))
                else:
                    st.caption("Read-only endpoint — actuator commands are not supported.")

    st.divider()
    st.subheader("Send a test command")
    st.markdown("Use the demo profiles below. The token is supplied by the simulator, so you can focus on the access-control decision.")
    c1, c2 = st.columns(2)
    with c1:
        source = st.selectbox("Client profile", list(CLIENTS.keys()), format_func=lambda k: f"{CLIENTS[k]['name']} ({CLIENTS[k]['role']})", key="manual_source")
        target = st.selectbox("Target actuator", ["smart-light-01", "smart-lock-01", "smart-fan-01"], format_func=lambda k: next(d["name"] for d in devices if d["device_id"] == k), key="manual_target")
        action_labels = [label for label, action in DISPLAY_ACTIONS.items() if action in next(d["actions"] for d in devices if d["device_id"] == target)]
        action_label = st.selectbox("Action", action_labels, key="manual_action")
    with c2:
        action = DISPLAY_ACTIONS[action_label]
        if action == "set_power":
            value = st.selectbox("Power state", [True, False], format_func=lambda v: "On" if v else "Off", key="manual_power")
        elif action == "set_brightness":
            value = st.slider("Brightness", 0, 100, 70, 5, key="manual_brightness")
        elif action == "set_speed":
            value = st.slider("Fan speed", 0, 5, 3, key="manual_speed")
        else:
            value = None
            st.info("This command changes the door-lock state.")
    submitted = st.button("Send command to gateway", type="primary", key="manual_send")
    if submitted:
        result = engine.process_command(command(source, target, action, value, scenario="manual_control"))
        _mirror_events([result], mqtt_bridge)
        if result["status"] == "ALLOWED":
            st.success("Command accepted. The virtual actuator state has been updated.")
        else:
            st.error("Command blocked by the security engine.")
        st.write(f"**Decision reason:** {result['reason']}")
        st.rerun()


def traffic_page(engine, mqtt_bridge):
    page_header("NETWORK OBSERVABILITY", "Traffic monitor", "Inspect the command records that reach the virtual gateway. Each row is one request, including accepted and rejected traffic.")
    top1, top2, top3 = st.columns([1, 1, 2])
    with top1:
        if st.button("Generate 8 normal requests", type="primary"):
            generated = generate_normal_traffic(engine, 8)
            _mirror_events(generated, mqtt_bridge)
            st.rerun()
    with top2:
        if st.button("Refresh view"):
            st.rerun()
    with top3:
        st.caption("Traffic is synthetic and generated inside this local application. No external network is scanned.")

    events = _events(engine, 1000)
    if not events:
        st.info("The traffic log is empty. Generate normal requests or run an attack simulation to populate it.")
        return
    f1, f2, f3 = st.columns(3)
    with f1:
        status_filter = st.selectbox("Decision", ["All", "ALLOWED", "BLOCKED"])
    with f2:
        severity_filter = st.selectbox("Severity", ["All", "INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"])
    with f3:
        source_filter = st.selectbox("Source client", ["All"] + sorted({e["source_id"] for e in events}))
    filtered = [e for e in events if (status_filter == "All" or e["status"] == status_filter)
                and (severity_filter == "All" or e["severity"] == severity_filter)
                and (source_filter == "All" or e["source_id"] == source_filter)]
    st.caption(f"Showing {len(filtered)} matching records from {len(events)} stored events.")
    st.dataframe(_event_frame(filtered), use_container_width=True, hide_index=True, height=430)
    with st.expander("What do these fields mean?"):
        st.markdown("- **Source:** the client that sent the command.\n- **Target:** the virtual device receiving the command.\n- **Action:** the operation requested.\n- **Result:** `ALLOWED` means the gateway accepted it; `BLOCKED` means a security rule rejected it.\n- **Severity:** the seriousness assigned to a security finding.\n- **Reason:** the plain-language explanation recorded by the gateway.")


def attack_lab_page(engine, mqtt_bridge):
    page_header("CONTROLLED SECURITY TESTING", "Attack simulation lab", "Run safe, local scenarios against virtual devices. The simulator demonstrates common IoT security failure patterns without targeting a real network.")
    st.markdown('<div class="callout warning"><strong>Lab boundary.</strong> Every scenario runs only against the virtual devices in this project. No real device, public IP address or third-party network is contacted.</div>', unsafe_allow_html=True)
    scenarios = [
        ("unauthorized_access", "01", "Unauthorised actuator access", "A registered guest account tries to unlock the front door, although its role only permits basic light control.", "Role and actuator permission check", "HIGH"),
        ("device_impersonation", "02", "Unknown device identity", "An unregistered controller claims to be part of the installation and attempts to unlock the door.", "Device registry / identity check", "CRITICAL"),
        ("replay_attack", "03", "Replay an earlier command", "A valid light command is sent once, then the exact same request ID is submitted again.", "Unique request ID check", "HIGH"),
        ("traffic_flooding", "04", "Traffic flooding", "One authorised client sends 12 commands in quick succession. The configured limit is 5 commands per 10 seconds.", "Per-client rate limiter", "MEDIUM"),
        ("invalid_credentials", "05", "Invalid credentials", "A registered client ID is paired with an incorrect demo token.", "Credential validation", "HIGH"),
    ]
    for start in range(0, len(scenarios), 2):
        cols = st.columns(2)
        for offset, item in enumerate(scenarios[start:start + 2]):
            scenario, number, title, description, check, severity = item
            with cols[offset]:
                with st.container(border=True):
                    st.markdown(f'<div class="step-number">SCENARIO {number} · {severity} SEVERITY</div>', unsafe_allow_html=True)
                    st.subheader(title)
                    st.write(description)
                    st.caption(f"What the gateway checks: {check}.")
                    if st.button(f"Run {title.lower()}", key=f"attack_{scenario}", use_container_width=True):
                        generated = run_attack(engine, scenario)
                        _mirror_events(generated, mqtt_bridge)
                        st.session_state["last_attack"] = generated
                        st.session_state["last_attack_name"] = title
                        st.rerun()
    if len(scenarios) % 2:
        st.write("")

    recent = st.session_state.get("last_attack")
    if recent:
        st.divider()
        st.subheader(f"Latest result · {st.session_state.get('last_attack_name', 'Scenario')}")
        blocked = sum(1 for event in recent if event["status"] == "BLOCKED")
        allowed = len(recent) - blocked
        a, b, c = st.columns(3)
        a.metric("Requests generated", len(recent))
        b.metric("Blocked", blocked)
        c.metric("Accepted", allowed)
        st.dataframe(_event_frame(recent), use_container_width=True, hide_index=True)
        st.caption("A replay scenario includes one original valid request followed by the repeated request. Flooding can allow the first few requests before the rate limit is crossed.")


def security_events_page(engine):
    page_header("AUDIT & RESPONSE", "Security events", "Review why a request was accepted or blocked. The explanation is intended to be readable without prior cybersecurity experience.")
    events = _events(engine, 2000)
    blocked = [e for e in events if e["status"] == "BLOCKED"]
    if not blocked:
        st.info("No blocked commands are recorded yet. Run one or more scenarios in the Attack simulation lab.")
    else:
        st.metric("Blocked commands in the current audit history", len(blocked))
    if not events:
        return
    threat_types = sorted({e["event_type"] for e in blocked})
    selected = st.selectbox("Filter by finding", ["All findings"] + [x.replace("_", " ") for x in threat_types])
    selected_norm = None if selected == "All findings" else selected.replace(" ", "_")
    filtered = [e for e in blocked if selected_norm is None or e["event_type"] == selected_norm]
    st.dataframe(_event_frame(filtered), use_container_width=True, hide_index=True, height=330)
    st.subheader("Detection guide")
    for key, info in THREAT_RULES.items():
        with st.expander(f"{info['label']} · {info['severity']}"):
            st.write(info["explanation"])
            st.markdown(f"**Recommended response:** {info['recommended_action']}")


def reports_page(engine):
    page_header("EVIDENCE & EVALUATION", "Reports & analytics", "Export the local audit trail and review the measurements produced by the controlled test scenarios.")
    stats = engine.summary()
    _metric_row(engine)
    events = _events(engine, 10000)
    if events:
        df = pd.DataFrame(events)
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download complete audit log (CSV)", data=csv_bytes,
                           file_name="iot_sentinel_audit_log.csv", mime="text/csv", type="primary")
        type_counts = df[df["status"] == "BLOCKED"]["event_type"].value_counts().rename_axis("Finding").reset_index(name="Blocked requests")
        if not type_counts.empty:
            fig = px.bar(type_counts, x="Blocked requests", y="Finding", orientation="h",
                         color_discrete_sequence=["#54765F"])
            fig.update_layout(height=300, margin=dict(l=6, r=8, t=12, b=8),
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF",
                              font_color="#566158", xaxis_title="Blocked requests", yaxis_title="")
            fig.update_xaxes(showgrid=True, gridcolor="#EEF0EA")
            fig.update_yaxes(showgrid=False)
            st.subheader("Blocked requests by finding")
            st.plotly_chart(fig, use_container_width=True)
        st.subheader("Session summary")
        st.dataframe(pd.DataFrame([
            {"Measure": "Total requests", "Value": stats["total"]},
            {"Measure": "Allowed requests", "Value": stats["allowed"]},
            {"Measure": "Blocked requests", "Value": stats["blocked"]},
            {"Measure": "Attack-labelled requests", "Value": stats["attack_attempts"]},
            {"Measure": "Attack-labelled requests detected", "Value": stats["detected_attacks"]},
            {"Measure": "High / critical events", "Value": stats["high_alerts"]},
        ]), use_container_width=True, hide_index=True)
    else:
        st.info("There is no audit data to export yet. Run the suggested test sequence first.")
    with st.expander("How should these results be interpreted?"):
        st.markdown("The figures describe this controlled simulation only. The attack detection rate uses the scenario labels embedded in generated test requests. It is not a claim about performance on a real deployment or an external benchmark dataset. The rate limiter intentionally allows requests up to the configured threshold before rejecting the excess traffic.")


def mqtt_page(engine, mqtt_bridge):
    page_header("OPTIONAL MESSAGE TRANSPORT", "Local MQTT bridge", "MQTT adds a realistic message broker to the lab. It is optional: all simulator and security features work without it.")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("**Broker connection**")
        host = st.text_input("Broker host", value=MQTT_HOST, help="Keep this at 127.0.0.1 for a local-only demonstration.")
        port = st.number_input("Broker port", min_value=1, max_value=65535, value=MQTT_PORT)
        if mqtt_bridge.status():
            st.success("Connected to local MQTT broker.")
            if st.button("Disconnect MQTT"):
                mqtt_bridge.disconnect()
                st.rerun()
        else:
            st.warning("Not connected. The app is currently using its built-in local simulator.")
            if st.button("Connect to MQTT broker", type="primary"):
                if host not in ("127.0.0.1", "localhost", "::1"):
                    st.error("For safety, this starter project only permits a loopback MQTT host.")
                else:
                    ok, message = mqtt_bridge.connect(host, int(port))
                    st.success(message) if ok else st.error(message)
        if mqtt_bridge.last_error:
            st.caption(mqtt_bridge.last_error)
    with c2:
        st.markdown("**Start Mosquitto with Docker**")
        st.markdown("From the project folder, run:")
        st.code("docker compose up -d mosquitto", language="bash")
        st.markdown("Stop it with:")
        st.code("docker compose down", language="bash")
        st.caption("Docker Desktop must be installed and running. The compose file binds the broker to localhost only.")
    st.divider()
    st.subheader("Published topic")
    st.code("iot-sentinel/traffic/events", language="text")
    st.write("When connected, each command event generated by the dashboard is mirrored to this MQTT topic as a JSON message. The local SQLite audit log remains the source of truth even when MQTT is disconnected.")
    if st.button("Publish a test event", disabled=not mqtt_bridge.status()):
        demo = {"event": "mqtt_bridge_test", "message": "IoT Sentinel local broker test", "timestamp": datetime.now().astimezone().isoformat(timespec="seconds")}
        ok, message = mqtt_bridge.publish_event(demo)
        st.success(message) if ok else st.error(message)
    with st.expander("How to inspect MQTT messages"):
        st.write("With Mosquitto installed on your Mac, open another Terminal and run:")
        st.code("mosquitto_sub -h 127.0.0.1 -t 'iot-sentinel/#' -v", language="bash")
        st.caption("This command only subscribes to the local lab broker. It does not scan or connect to other networks.")


def about_page():
    page_header("PROJECT GUIDE", "How IoT Sentinel works", "A beginner-friendly explanation of the architecture, security checks and limits of this software-based implementation.")
    st.subheader("Project objective")
    st.write("IoT Sentinel models a small smart-home network and demonstrates how an IoT gateway can inspect actuator-control requests before allowing a command to change a device state. The emphasis is on identifying unauthorised access attempts and keeping an auditable record of decisions.")
    st.subheader("Processing flow")
    steps = [
        ("1. A client sends a command", "For example, the owner app asks the smart light to switch on."),
        ("2. The gateway checks identity", "The source must be a registered client and present its demo token."),
        ("3. The gateway checks request safety", "It checks for duplicate request IDs and excessive request rates."),
        ("4. The gateway checks permissions", "The client must be allowed to control the selected actuator and action."),
        ("5. The actuator state changes only on approval", "A rejected request is logged but does not change the virtual device."),
    ]
    for title, detail in steps:
        st.markdown(f"**{title}**  \n{detail}")
    st.subheader("Security checks in this version")
    st.dataframe(pd.DataFrame([
        {"Check": "Client registry", "Purpose": "Reject unregistered identities."},
        {"Check": "Demo credential", "Purpose": "Reject a known client ID paired with the wrong token."},
        {"Check": "Role / actuator permissions", "Purpose": "Prevent a guest profile from controlling restricted devices."},
        {"Check": "Request ID replay check", "Purpose": "Reject a request identifier that has already been processed."},
        {"Check": "Rate limiter", "Purpose": "Limit each client to 5 command requests in 10 seconds."},
        {"Check": "Command validation", "Purpose": "Reject unsupported actions and out-of-range values."},
    ]), use_container_width=True, hide_index=True)
    st.subheader("What is simulated, and what is real?")
    st.markdown("- **Simulated:** sensors, actuators, users, commands, attacks and device state.\n- **Real software components:** Python application, SQLite audit database, Streamlit dashboard and (when enabled) a local MQTT broker.\n- **Not included:** physical electronics, radio traffic capture, production-grade cryptography, cloud security or proof of protection against every IoT attack.")
    st.markdown('<div class="callout warning"><strong>Academic note.</strong> This is a software-based prototype of gateway security controls. In a real deployment, tokens would be replaced with secure device authentication, transport encryption, key rotation, secure provisioning, message timestamps and stronger replay protection.</div>', unsafe_allow_html=True)
