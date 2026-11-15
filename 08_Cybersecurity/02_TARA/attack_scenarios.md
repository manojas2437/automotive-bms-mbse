# 02 TARA — Threat and Attack Scenarios

## 1. Purpose & Methodology
This document defines the **Threat Scenarios (`TS-001` through `TS-007`)** and plausible **Attack Paths** for the **400 V High-Voltage Battery Management System (HV-BMS)** in accordance with **ISO/SAE 21434 (Clause 9)**. Using the **STRIDE** threat modeling framework (*Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege*), each scenario maps compromised cybersecurity assets (`ASSET-001` to `ASSET-007`) to potential vehicle-level safety, operational, financial, and privacy impacts.

---

## 2. Threat Scenario Definitions

### Threat Scenario 1 – Unauthorized Firmware Modification (`TS-001`)
* **Asset:** `ASSET-001` (BMS Firmware)
* **STRIDE Category:** Tampering / Elevation of Privilege
* **Threat:** An attacker attempts to modify the BMS application or bootloader firmware stored in the `Master MCU` Flash memory.
* **Plausible Attack Path:**
  * Physical access to exposed `JTAG / SWD` debug pins on the BMS PCB, or exploitation of an unauthenticated UDS flashing routine (`0x34 RequestDownload` / `0x36 TransferData`) over the vehicle OBD-II / CAN gateway.
* **Potential Impact:**
  * **Safety (`S`):** Compromised firmware disables overvoltage/overtemperature fault checks or alters contactor control logic, leading to cell overcharging (`HAZ-001`), thermal runaway (`HAZ-002`), or unintended HV energization (`HAZ-004`).
  * **Operational (`O`):** Permanent ECU bricking or arbitrary loss of vehicle propulsion.
* **Security Objective:** Firmware authenticity and integrity (enforced via hardware-anchored Secure Boot and digitally signed firmware images).

---

### Threat Scenario 2 – Unauthorized Diagnostic Access (`TS-002`)
* **Asset:** `ASSET-004` (Diagnostic Interface)
* **STRIDE Category:** Elevation of Privilege / Spoofing
* **Threat:** An attacker sends unauthorized privileged UDS diagnostic commands to the BMS over the vehicle network.
* **Plausible Attack Path:**
  * Connecting an aftermarket diagnostic dongle to the OBD-II port or pivoting from a compromised Telematics/Infotainment ECU onto the diagnostic CAN bus, then brute-forcing weak `0x27 SecurityAccess` seed-key algorithms or exploiting unlocked diagnostic sessions (`0x10 DiagnosticSessionControl`).
* **Potential Impact:**
  * **Safety (`S`):** Unauthorized execution of `0x2F InputOutputControlByIdentifier` forces HV contactors open while driving (`HAZ-003`) or closes contactors during workshop maintenance (`HAZ-004`).
  * **Financial / Forensic (`F`):** Unauthorized execution of `0x14 ClearDiagnosticInformation` erases critical latched DTCs (e.g., welded contactor or thermal abuse records) prior to warranty claims or vehicle resale.
* **Security Objective:** Strong authentication, role-based authorization, and session timeout enforcement (`ISO 14229 UDS 0x29 Authentication`).

---

### Threat Scenario 3 – CAN Message Manipulation & Replay (`TS-003`)
* **Asset:** `ASSET-005` (CAN Communication) & `ASSET-003` (Battery State Information)
* **STRIDE Category:** Spoofing / Tampering
* **Threat:** An attacker injects forged, modified, or replayed `CAN / CAN-FD` messages onto the powertrain bus (`VCU ↔ MBMS ↔ OBC`).
* **Plausible Attack Path:**
  * Physical tap into the powertrain CAN harness or compromise of another ECU sharing the powertrain CAN bus to transmit spoofed `HV_Enable_Request`, false `MaxChargeCurrent` limits, or replayed healthy `BatterySoC` / `CellVoltage` frames.
* **Potential Impact:**
  * **Safety (`S`):** Forged high charging current limits override thermal/SoC derating (`HAZ-005`), causing lithium plating or overvoltage; spoofed `HV_Enable_Request` energizes the HV bus unexpectedly.
  * **Operational (`O`):** Replaying stale `BatterySoC` values causes unexpected battery depletion and sudden vehicle immobilization (`HAZ-003`).
* **Security Objective:** Message authenticity, integrity, and freshness (enforced via `SecOC` Message Authentication Codes and monotonic freshness counters).

---

### Threat Scenario 4 – Cryptographic Key Compromise (`TS-004`)
* **Asset:** `ASSET-006` (Cryptographic Keys)
* **STRIDE Category:** Information Disclosure / Tampering
* **Threat:** An attacker extracts symmetric `SecOC` keys, diagnostic authentication keys, or replaces root Secure Boot public keys stored in the BMS.
* **Plausible Attack Path:**
  * Reading plaintext keys from unprotected Flash/EEPROM dumps, side-channel power analysis on software cryptographic routines, or exploiting debug interfaces left active after manufacturing.
* **Potential Impact:**
  * **System-Wide Impact (`S`, `O`, `F`):** Complete loss of trust anchor—enabling the attacker to sign malicious firmware (`TS-001`), forge valid `SecOC` CAN messages (`TS-003`), and authenticate as a privileged diagnostic tester (`TS-002`) across identical BMS units.
* **Security Objective:** Hardware-isolated secure key storage (`HSM` / `SHE`) and strict key lifecycle management (zero plaintext key exposure).

---

### Threat Scenario 5 – Battery Calibration Data Tampering (`TS-005`)
* **Asset:** `ASSET-002` (Battery Calibration Data)
* **STRIDE Category:** Tampering
* **Threat:** An attacker alters cell voltage thresholds, temperature derating curves, or current limit lookup tables stored in non-volatile memory.
* **Plausible Attack Path:**
  * Unauthorized `0x2E WriteDataByIdentifier` UDS requests or direct EEPROM/Data Flash manipulation to raise upper cell voltage limits (`> 4.25 V`) or disable temperature derating for aftermarket performance tuning.
* **Potential Impact:**
  * **Safety (`S`):** Battery operates outside its electrochemical Safe Operating Area (SOA), accelerating dendrite growth and triggering thermal runaway (`HAZ-001`, `HAZ-002`).
  * **Financial (`F`):** Accelerated pack capacity fade leading to fraudulent warranty replacement claims.
* **Security Objective:** Calibration data integrity and write-access authorization (digital signature verification of calibration blocks at startup and runtime).

---

### Threat Scenario 6 – CAN Bus Denial of Service / Flooding (`TS-006`)
* **Asset:** `ASSET-005` (CAN Communication) & `ASSET-003` (Battery State Information)
* **STRIDE Category:** Denial of Service
* **Threat:** An attacker floods the powertrain `CAN / CAN-FD` bus with high-priority dominant frames (`ID 0x000`), blocking legitimate communication between `Master BMS`, `VCU`, and `OBC`.
* **Plausible Attack Path:**
  * Compromised ECU on the same CAN segment or rogue hardware device attached to the vehicle bus continuously transmitting high-priority frames.
* **Potential Impact:**
  * **Safety (`S`) & Operational (`O`):** `Master BMS` and `VCU` experience communication timeout (`FMEA-006`), forcing emergency power derating (`0 A`) and HV contactor opening during highway driving (`HAZ-003`).
* **Security Objective:** Network segmentation, CAN gateway filtering, and deterministic safety fallback behavior upon communication loss.

---

### Threat Scenario 7 – Malicious or Downgraded Software Update Package (`TS-007`)
* **Asset:** `ASSET-007` (Software Update Package)
* **STRIDE Category:** Spoofing / Tampering / Information Disclosure
* **Threat:** An attacker injects a tampered OTA/service update package, intercepts proprietary firmware binaries during transfer, or forces a downgrade (rollback) to an older vulnerable firmware version.
* **Plausible Attack Path:**
  * Man-in-the-Middle (MitM) interception between the OTA gateway/service tool and BMS bootloader, or replaying a previously signed legitimate firmware image containing a known security flaw.
* **Potential Impact:**
  * **Safety (`S`) & Fleet Operational (`O`):** Fleet-wide compromise of BMS safety controls via malicious update, or re-introduction of exploitable vulnerabilities via version rollback.
  * **Intellectual Property (`F`):** Reverse engineering of proprietary SoC/SoH estimation algorithms from unencrypted update payloads.
* **Security Objective:** End-to-end update authenticity, integrity, confidentiality, and hardware-enforced anti-rollback version protection.

---

## 3. Threat-to-Asset & Safety Cross-Reference Matrix

| Threat ID | Threat Scenario | Target Asset(s) | STRIDE | Related Safety Hazard / Goal |
| :--- | :--- | :--- | :--- | :--- |
| **TS-001** | Unauthorized firmware modification | `ASSET-001` | Tampering / EoP | `HAZ-001`..`005` / `SG-001`..`005` |
| **TS-002** | Unauthorized diagnostic access | `ASSET-004` | EoP / Spoofing | `HAZ-003`, `HAZ-004` / `SG-003`, `SG-004` |
| **TS-003** | CAN message manipulation & replay | `ASSET-005`, `ASSET-003` | Spoofing / Tampering | `HAZ-001`, `HAZ-003`, `HAZ-005` / `SG-001`, `SG-003`, `SG-005` |
| **TS-004** | Cryptographic key compromise | `ASSET-006` | Info Disclosure / Tampering | All Safety Goals (`SG-001`..`005`) |
| **TS-005** | Battery calibration data tampering | `ASSET-002` | Tampering | `HAZ-001`, `HAZ-002`, `HAZ-005` / `SG-001`, `SG-002`, `SG-005` |
| **TS-006** | CAN bus Denial of Service / flooding | `ASSET-005`, `ASSET-003` | Denial of Service | `HAZ-003` / `SG-003` |
| **TS-007** | Malicious or downgraded update package | `ASSET-007` | Spoofing / Tampering / Info Disc. | All Safety Goals (`SG-001`..`005`) |
