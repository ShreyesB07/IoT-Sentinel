# Test Plan — IoT Sentinel

## Test environment

- macOS on Apple Silicon or another system with Python 3.11+.
- Python virtual environment with dependencies from `requirements.txt`.
- No physical IoT devices required.
- Optional: Docker Desktop and local Mosquitto broker for MQTT verification.

## Functional test cases

| ID | Test | Input / action | Expected outcome |
|---|---|---|---|
| TC-01 | Authorised actuator command | Owner app switches on the smart light | Gateway accepts the command and light state changes to On |
| TC-02 | Guest permission boundary | Guest tablet tries to unlock the front door | Gateway blocks the command; door remains locked |
| TC-03 | Unknown identity | Unregistered controller sends an unlock command | Gateway blocks the request as possible device impersonation |
| TC-04 | Invalid credential | Owner client ID supplies an incorrect token | Gateway blocks the request |
| TC-05 | Replay | Submit the same request ID twice | First request is accepted; duplicate is blocked as replay |
| TC-06 | Rate limiting | Send six requests within the configured window | First five may pass; request above the limit is blocked |
| TC-07 | Sensor control attempt | Send an actuator action to the temperature sensor | Gateway blocks the request because the target is not an actuator |
| TC-08 | Value validation | Set brightness to 140 | Gateway blocks the out-of-range value |
| TC-09 | Audit logging | Run any of the above tests | An event record is stored with timestamp, source, target, decision and reason |
| TC-10 | CSV export | Download the audit log from Reports & analytics | CSV file contains the session event records |
| TC-11 | MQTT bridge (optional) | Start Mosquitto and connect the dashboard | Dashboard reports connected and mirrors generated events to the configured topic |

## Automated unit tests

Run:

```bash
python -m unittest discover -s tests -v
```

The tests cover the core command acceptance, access control, identity, credential, replay, rate-limit, sensor-target and value-validation rules.

## Suggested classroom demonstration order

1. Show the virtual installation and explain that the sensors and actuators are software models.
2. Send one authorised light command and show the changed state.
3. Use the guest profile to attempt to unlock the door and show that the state remains locked.
4. Run the impersonation, replay, flooding and invalid-credential scenarios.
5. Open Security events and explain the rule that triggered each block.
6. Open Reports & analytics and export the CSV log.
7. Optionally demonstrate that events are also published to the local MQTT broker.

## Acceptance criteria

The project is considered functionally complete when all automated tests pass, the dashboard launches, each attack scenario produces the expected security event, accepted commands update the appropriate virtual actuator, blocked commands do not change actuator state, and the audit log can be exported.
