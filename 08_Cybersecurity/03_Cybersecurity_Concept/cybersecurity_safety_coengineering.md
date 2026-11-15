# 03 Cybersecurity Concept — Cybersecurity & Functional Safety Co-Engineering

## 1. Purpose & Architectural Perspective
In a **400 V High-Voltage Battery Management System (HV-BMS)**, functional safety (**ISO 26262**) and automotive cybersecurity (**ISO/SAE 21434**) are deeply interdependent. Functional safety protects against **unintended random hardware failures and systematic faults**, whereas cybersecurity protects against **intentional malicious manipulation** that could cause those exact same physical hazards (`HAZ-001` through `HAZ-005`).

> **Engineering Governance Note:** Cybersecurity controls reduce the likelihood of maliciously induced safety violations, but **cybersecurity mechanisms do not replace or automatically establish ISO 26262 functional safety compliance**. Safety impact and cybersecurity risk must be analyzed jointly so that security reactions (such as halting execution on a failed cryptographic check) do not inadvertently violate availability-related safety goals (such as `SG-003: Prevent unintended HV disconnection during vehicle operation`).

---

## 2. Threat-to-Safety Consequence Mapping

| Cybersecurity Threat (`ISO/SAE 21434`) | Target Asset | Possible Safety Consequence (`ISO 26262`) | Violated Safety Goal(s) |
| :--- | :--- | :--- | :--- |
| **Firmware manipulation** (`TS-001`, `TS-007`) | `ASSET-001` (BMS Firmware)<br>`ASSET-007` (Update Package) | Malicious alteration of overvoltage, overtemperature, or contactor state-machine logic leading to thermal runaway or unintended 400 V bus energization. | `SG-001`, `SG-002`, `SG-004` |
| **Sensor & calibration data manipulation** (`TS-003`, `TS-005`) | `ASSET-002` (Calibration Data)<br>`ASSET-003` (Battery State Info) | Corrupted cell voltage/temperature thresholds or spoofed `SoC` values causing incorrect battery state estimation and operation outside the Safe Operating Area (SOA). | `SG-001`, `SG-002`, `SG-005` |
| **CAN message manipulation** (`TS-003`) | `ASSET-005` (CAN Communication) | Forged or replayed `MaxChargeCurrent` or `HV_Enable_Request` frames causing overcharging, lithium plating, or unexpected HV activation. | `SG-001`, `SG-004`, `SG-005` |
| **Diagnostic access abuse** (`TS-002`) | `ASSET-004` (Diagnostic Interface) | Unauthorized execution of UDS I/O control routines (`0x2F`) opening contactors during highway driving or closing contactors during workshop maintenance. | `SG-003`, `SG-004` |
| **Denial of service (DoS)** (`TS-006`) | `ASSET-005` (CAN Communication) | CAN bus flooding causes loss of battery communication with VCU/OBC, triggering emergency power derating and sudden loss of propulsion. | `SG-003` |

---

## 3. Defense-in-Depth Flow: How Security Controls Reduce Safety Risks

### 3.1 Firmware Manipulation (`TS-001` → `SG-001` / `SG-002`)
```text
Threat:
Unauthorized firmware modification (TS-001)
        |
        v
Cybersecurity Requirement:
Verify firmware authenticity & integrity before execution (CS-REQ-001, CS-REQ-002)
        |
        v
Security Mechanism:
Hardware-anchored Secure Boot + Asymmetric Signature Verification (HSM)
        |
        v
Safety Contribution:
Reduces risk of executing unauthorized battery control software that could
disable overvoltage/overtemperature protection or contactor interlocks.
```

### 3.2 CAN Message Manipulation (`TS-003` → `SG-001` / `SG-004` / `SG-005`)
```text
Threat:
Forged or replayed CAN control/limit messages (TS-003)
        |
        v
Cybersecurity Requirement:
Detect invalid or replayed protected messages (CS-REQ-005)
        |
        v
Security Mechanism:
Secure Onboard Communication (SecOC) with HSM-backed MAC + Freshness Counter
        |
        v
Safety Contribution:
Prevents spoofed charging limits or unauthorized HV_Enable commands from
driving the battery pack beyond safe voltage, current, or isolation limits.
```

### 3.3 Diagnostic Access Abuse (`TS-002` → `SG-003` / `SG-004`)
```text
Threat:
Unauthorized privileged UDS diagnostic commands (TS-002)
        |
        v
Cybersecurity Requirement:
Authenticate authorized diagnostic access & restrict calibration writes (CS-REQ-003, CS-REQ-007)
        |
        v
Security Mechanism:
UDS 0x29 Certificate Authentication + Role-Based Access Control + Precondition Gating
        |
        v
Safety Contribution:
Blocks unauthorized contactor overrides during driving or maintenance and
protects safety threshold calibrations from tampering.
```

### 3.4 Denial of Service (`TS-006` → `SG-003`)
```text
Threat:
CAN bus flooding / communication loss (TS-006)
        |
        v
Cybersecurity Requirement:
Isolate safety-critical CAN reception & enforce safe fallback (CS-REQ-009)
        |
        v
Security Mechanism:
Hardware CAN Message Filtering + Gateway Rate Limiting + E2E Timeout Monitor
        |
        v
Safety Contribution:
Ensures deterministic, controlled power ramp-down and safe HV isolation rather
than erratic contactor chatter or unmonitored battery operation.
```

---

## 4. Safety–Security Conflict Analysis & Joint Resolution
When integrating security controls into a safety-critical BMS, potential conflicts between **security enforcement** and **safety availability** must be explicitly resolved:

| Potential Conflict | Security Objective | Safety Objective (`SG-003`) | Joint Architectural Resolution |
| :--- | :--- | :--- | :--- |
| **Secure Boot Failure on Startup** | Block execution of unverified firmware (`CS-REQ-001`). | Prevent unexpected HV disconnection while driving. | Secure Boot runs **only at cold boot** when HV contactors are already physically `OPEN` (`Initialization` state), never interrupting an active drive cycle. |
| **SecOC MAC Verification Failure During Driving** | Reject any CAN frame with an invalid MAC or stale freshness counter (`CS-REQ-005`). | Avoid immediate, abrupt loss of propulsion on a single transient bit flip (`SG-003`). | Pair `SecOC` rejection with a **debounced E2E timeout window**; transient single-frame errors increment an error counter, while sustained failures trigger controlled power derating (`0 A`) before opening contactors. |
| **Privileged Diagnostic Contactor Override** | Allow authorized service technicians to test contactors (`CS-REQ-003`). | Prevent HV energization when HVIL is open or vehicle is moving (`SG-003`, `SG-004`). | Enforce **dual gating**: UDS `0x29` cryptographic authentication **AND** physical safety preconditions (`Vehicle_Speed == 0`, `HVIL_Status == VALID`, `Standby` mode) must both be satisfied. |
