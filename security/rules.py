"""Human-readable security policy and threat labels."""
THREAT_RULES = {
    "unauthorized_actuator_access": {
        "label": "Unauthorised actuator access",
        "severity": "HIGH",
        "explanation": "The signed-in client is known, but its role is not permitted to control this actuator or perform this action.",
        "recommended_action": "Review the user's role and the actuator permissions. Keep door and safety controls restricted.",
    },
    "device_impersonation": {
        "label": "Unknown device / possible impersonation",
        "severity": "CRITICAL",
        "explanation": "The command came from a client identity that is not registered in this IoT installation.",
        "recommended_action": "Reject the source, verify device identity out-of-band, and register devices only through an administrator.",
    },
    "replay_attack": {
        "label": "Replay attack",
        "severity": "HIGH",
        "explanation": "A request identifier already seen by the gateway was submitted again.",
        "recommended_action": "Use unique nonces or sequence numbers and short-lived message timestamps in a production design.",
    },
    "traffic_flooding": {
        "label": "Traffic flooding / rate limit exceeded",
        "severity": "MEDIUM",
        "explanation": "The source sent more than the allowed number of commands inside the configured time window.",
        "recommended_action": "Apply per-client rate limits and investigate the source if the burst is unexpected.",
    },
    "invalid_credentials": {
        "label": "Invalid credentials",
        "severity": "HIGH",
        "explanation": "The client identifier exists, but the presented demo token does not match its registered token.",
        "recommended_action": "Reject the request and rotate credentials if misuse is suspected.",
    },
    "invalid_command": {
        "label": "Invalid actuator command",
        "severity": "LOW",
        "explanation": "The target does not support the requested action or the command value is outside the accepted range.",
        "recommended_action": "Check the device capability list and validate command values before publishing.",
    },
    "sensor_control_attempt": {
        "label": "Attempt to control a sensor",
        "severity": "MEDIUM",
        "explanation": "A control command was sent to a sensor or gateway that does not expose actuator controls.",
        "recommended_action": "Check the target identifier and keep sensor telemetry topics separate from actuator command topics.",
    },
}
