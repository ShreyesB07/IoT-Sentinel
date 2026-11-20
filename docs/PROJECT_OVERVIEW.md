# Project Overview — IoT Sentinel

## 1. Project title

**IoT Sentinel: IoT Network Traffic Monitoring and Unauthorized Actuator Access Detection System**

## 2. Abstract

The Internet of Things (IoT) connects sensors, actuators, gateways and user applications so that physical environments can be monitored and controlled remotely. This connectivity also creates security risks: an unauthorised client may attempt to operate an actuator, impersonate a registered device, repeat an earlier command, or overwhelm a gateway with excessive requests.

IoT Sentinel is a software-based prototype that models a small smart-home IoT installation. It generates synthetic device-control traffic and inspects each request at a virtual gateway before changing an actuator state. The gateway applies identity validation, credential checks, role-based actuator permissions, replay detection, rate limiting and command-value validation. Accepted and rejected requests are stored in a local SQLite audit log and displayed through a Streamlit dashboard. An optional local MQTT broker can be used to demonstrate message transport.

The project is designed to demonstrate IoT security concepts without physical hardware. All devices and attack scenarios are simulated in a controlled local environment.

## 3. Problem statement

IoT actuators can affect the physical environment, for example by unlocking a door, switching a motor or changing lighting. A gateway that accepts commands without verifying the source and its permissions can allow unauthorised control. A simple and observable software prototype is useful for demonstrating how command-level checks and traffic monitoring can reduce these risks.

## 4. Objectives

1. Build a virtual IoT environment containing sensors, actuators and a gateway.
2. Generate normal commands from authorised client profiles.
3. Inspect command identity, credentials, target device, action, request ID and request rate.
4. Identify and block selected unauthorised or suspicious command patterns.
5. Record security decisions with timestamps and plain-language explanations.
6. Present device state, traffic activity, alerts and summary metrics in a dashboard.
7. Demonstrate MQTT message transport through an optional local broker.

## 5. Scope

### Included

- Virtual temperature and humidity sensors.
- Virtual smart light, door lock and fan actuators.
- Owner, administrator and guest client profiles.
- Rule-based checks for unknown identities, invalid credentials, unauthorised actuator access, replayed request IDs, request flooding, sensor-control attempts and invalid command values.
- Local event persistence using SQLite.
- Streamlit dashboard and CSV export.
- Optional local Mosquitto MQTT broker integration.

### Not included

- Physical sensor/actuator construction or firmware.
- Wireless packet capture from a real deployment.
- Production authentication, cryptographic signing, TLS provisioning or key rotation.
- Detection of every possible IoT attack.
- Claims of production-level security or real-world detection accuracy.

## 6. System architecture

```text
User / Attack Scenario Generator
              |
              v
     Virtual IoT Clients
              |
              v
      Virtual IoT Gateway
              |
       Security Rule Engine
       /      |       \\
      v       v        v
 Identity  Replay   Rate Limit
 Check     Check     Check
       \\      |       /
              v
      Role and Command Check
              |
        +-----+-----+
        |           |
        v           v
    Accepted     Rejected
        |           |
        v           v
 Virtual Actuator   Audit Event
        |           |
        +-----+-----+
              v
       SQLite Audit Log
              |
              v
     Streamlit Dashboard
              |
              +---- Optional MQTT event publisher
```

## 7. Implementation methodology

### 7.1 Virtual device model

Each virtual device has a unique identifier, a device type, a zone, supported actions and a state dictionary. Sensors expose simulated readings and are not controllable. Actuators expose a limited set of control actions.

### 7.2 Client identity and permissions

The lab defines owner, administrator and guest profiles. A client must be registered and present its matching demo token. A client must also be authorised for the selected actuator and action. For example, the guest profile may switch the smart light but cannot unlock the door.

### 7.3 Traffic inspection

Each command includes a request ID, source client, target device, action, value and scenario label. The gateway checks the request before applying it. Every request produces an audit event with its result, severity, event type and a plain-language reason.

### 7.4 Threat scenarios

- Unauthorised actuator access: a guest tries to unlock the door.
- Device impersonation: an unregistered client attempts to issue a command.
- Replay: an already processed request ID is submitted again.
- Traffic flooding: more than five requests are sent by one client in ten seconds.
- Invalid credentials: a registered client ID is paired with the wrong demo token.

### 7.5 Visualisation and reporting

The dashboard presents device state, accepted and blocked requests, security findings, session metrics and CSV export. The optional MQTT bridge mirrors generated events to a local broker topic.

## 8. Expected outcome

The completed prototype demonstrates that an authorised command can update a virtual actuator, while selected suspicious or unauthorised requests are rejected and logged. The student can reproduce each scenario, inspect the corresponding rule and collect evidence from the dashboard and exported audit log.

## 9. Evaluation measures

- Total commands inspected.
- Number and percentage of commands allowed or blocked.
- Number of synthetic attack-labelled requests.
- Number of attack-labelled requests that triggered a detection rule.
- Blocked requests grouped by finding type.
- Correctness of actuator state changes after accepted and rejected commands.

All metrics describe the controlled simulator session. They are not a substitute for testing against real IoT traffic or a labelled external dataset.

## 10. Conclusion

IoT Sentinel provides a reproducible software-only environment for studying gateway-level IoT security. It demonstrates why identity, permissions, replay checks, rate limiting and audit logging are important when protecting actuator controls. Its modular design can be extended with physical hardware, secure MQTT authentication, TLS, packet capture or a machine-learning anomaly detector in future work.
