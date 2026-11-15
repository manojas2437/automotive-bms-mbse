# 01 Item and Assets — BMS Cybersecurity Asset Identification

## 1. Purpose & Standard Reference
This document establishes the **Cybersecurity Asset Identification** for the **400 V High-Voltage Battery Management System (HV-BMS)** in accordance with **ISO/SAE 21434 (Clause 9 – Threat Analysis and Risk Assessment)**. Because the BMS controls high-voltage galvanic isolation and electrochemical operating boundaries, cybersecurity compromises can directly violate safety goals (`SG-001` through `SG-005`), disable vehicle mobility, or expose proprietary battery control intellectual property.

---

## 2. Asset Summary Matrix

| Asset ID | Asset Name | Primary Security Objectives (CIA+) | Asset Location | Primary Interfaces |
| :--- | :--- | :--- | :--- | :--- |
| **ASSET-001** | BMS Firmware | Integrity, Authenticity | Master MCU Non-Volatile Flash Memory | Bootloader, UDS/OTA Flashing Interface, JTAG/SWD Debug Port |
| **ASSET-002** | Battery Calibration Data | Integrity | Master MCU Data Flash / EEPROM (NVM) | UDS Diagnostic Service (`WriteDataByIdentifier`), EOL Calibration Tool |
| **ASSET-003** | Battery State Information | Integrity, Availability | Master MCU SRAM & NVM (`SoC`, `SoH`, `SoP`, `CellVoltage`) | Internal `isoSPI` Bus, External `CAN / CAN-FD` Bus (VCU/OBC) |
| **ASSET-004** | Diagnostic Interface | Access Control, Integrity, Authenticity | Master MCU UDS Stack & Physical Debug/OBD-II Gateway | External `CAN` (ISO 14229 UDS), Hardware JTAG/SWD Pins |
| **ASSET-005** | CAN Communication | Integrity, Availability, Authenticity | Master BMS CAN Controller & Transceiver | Vehicle Powertrain `CAN / CAN-FD` Bus (`VCU`, `OBC`, `TMS`) |
| **ASSET-006** | Cryptographic Keys | Confidentiality, Integrity | Master MCU Hardware Security Module (HSM) / Secure Key Storage | HSM Internal Bus, Secure Bootloader, SecOC / UDS Security Access |
| **ASSET-007** | Software Update Package | Authenticity, Integrity | External OTA/Service Payload → Master MCU Staging Memory | Over-The-Air (OTA) Gateway / Service Tester via UDS (`RequestDownload` / `TransferData`) |

---

## 3. Detailed Asset Profiles

### ASSET-001: BMS Firmware
* **Description:** Embedded application software, real-time operating system (RTOS), state-machine logic, fault diagnostic handlers, and low-level drivers running on the `Master MCU`.
* **Security Objectives:** **Integrity** and **Authenticity**.
* **Asset Owner:** BMS Embedded Software & Systems Engineering Team.
* **Asset Location:** Internal program Flash memory of the `Master MCU` (protected by Secure Boot and Memory Protection Unit).
* **External Interfaces:**
  * UDS diagnostic bootloader interface over `CAN / CAN-FD` (for service reflashing and OTA updates).
  * Hardware debug interface (`JTAG / SWD`) during development and manufacturing.
* **Security Properties:**
  * Code must originate from a trusted, cryptographically signed build (`Authenticity`).
  * Binary instructions must remain unmodified in Flash and during runtime execution (`Integrity`).
* **Dependencies:** Relies on **ASSET-006** (Cryptographic Keys) for Secure Boot signature verification and **ASSET-007** (Software Update Package) during firmware updates.
* **Potential Consequences of Compromise:**
  * **Safety Impact:** Attacker modifies overvoltage, overtemperature, or contactor control logic, bypassing `SG-001`–`SG-005` and causing battery thermal runaway, fire, or unintended 400 V bus energization.
  * **Operational Impact:** Permanent bricking of the BMS ECU or arbitrary disabling of propulsion (`Denial of Service`).

---

### ASSET-002: Battery Calibration Data
* **Description:** Configurable parameters defining cell chemistry limits (overvoltage/undervoltage thresholds, temperature derating curves, maximum current lookup tables, debounce timers, and 96S pack topology parameters).
* **Security Objectives:** **Integrity** (and **Confidentiality** for proprietary cell characterization models).
* **Asset Owner:** Battery Systems & Calibration Engineering Team.
* **Asset Location:** Dedicated calibration sector in `Master MCU` Non-Volatile Memory (Data Flash / emulated EEPROM).
* **External Interfaces:**
  * UDS diagnostic write services (`0x2E WriteDataByIdentifier`, `0x31 RoutineControl`) over `CAN / CAN-FD`.
  * End-of-Line (EOL) manufacturing programming interface.
* **Security Properties:**
  * Calibration tables must be protected against unauthorized modification (`Integrity`) and validated via checksum/signature at startup.
* **Dependencies:** Depends on **ASSET-004** (Diagnostic Interface access control) and **ASSET-006** (Cryptographic Keys) to authenticate calibration write sessions.
* **Potential Consequences of Compromise:**
  * **Safety Impact:** Raising overvoltage (`> 4.25 V`) or overtemperature thresholds allows cells to operate outside their Safe Operating Area (SOA), leading to lithium plating, venting, or thermal runaway (`HAZ-001`, `HAZ-002`).
  * **Financial / Warranty Impact:** Premature battery degradation or voided OEM battery warranty compliance.

---

### ASSET-003: Battery State Information
* **Description:** Real-time physical measurements and estimated states including individual `CellVoltage` (96x), `CellTemperature`, `PackCurrent`, `BatterySoC`, `BatterySoH`, `MaxChargeCurrent`, `MaxDischargeCurrent`, and `BatteryFaultStatus`.
* **Security Objectives:** **Integrity** and **Availability**.
* **Asset Owner:** BMS Estimation & Diagnostics Function Owner.
* **Asset Location:** `Master MCU` runtime SRAM (live variables) and NVM (persisted `SoC`, `SoH`, and DTC freeze-frames).
* **External Interfaces:**
  * Internal isolated daisy-chain (`isoSPI`) receiving raw measurements from `Slave BMS` (CMUs).
  * External `CAN / CAN-FD` bus broadcasting state estimates and power limits to `VCU`, `OBC`, and `TMS`.
* **Security Properties:**
  * Telemetry must accurately reflect actual physical battery conditions without spoofing or replay (`Integrity`).
  * State updates must be delivered within defined cycle and latency budgets (`Availability`).
* **Dependencies:** Depends on **ASSET-001** (BMS Firmware) for calculation accuracy and **ASSET-005** (CAN Communication) for reliable external delivery.
* **Potential Consequences of Compromise:**
  * **Safety Impact:** Spoofing lower `CellVoltage` or `CellTemperature` values masks fault detection; spoofing higher `MaxChargeCurrent` causes overcharging (`HAZ-005`).
  * **Operational Impact:** False `SoC = 0%` or false critical fault injection strands the vehicle or causes sudden loss of propulsion (`HAZ-003`).

---

### ASSET-004: Diagnostic Interface
* **Description:** ISO 14229 (UDS) diagnostic protocol stack, diagnostic session state machine, security access (`0x27 SecurityAccess`), routine controls (e.g., manual contactor actuation, DTC clearing), and physical hardware debug ports (`JTAG/SWD`).
* **Security Objectives:** **Access Control**, **Integrity**, and **Authenticity**.
* **Asset Owner:** Vehicle Diagnostics & Cybersecurity Engineering Team.
* **Asset Location:** `Master MCU` communication stack and physical PCB debug/test pads.
* **External Interfaces:**
  * Vehicle OBD-II / Central Gateway `CAN / CAN-FD` diagnostic bus connected to external `Diagnostic Tool` (Technician).
  * Physical `JTAG / SWD` pins on the Master BMS PCB.
* **Security Properties:**
  * Privileged diagnostic routines (contactor override, NVM write, firmware flash, DTC clear) must be restricted to authenticated roles (`Access Control` & `Authenticity`).
  * Hardware debug interfaces must be permanently locked or authenticated in production (`Access Control`).
* **Dependencies:** Relies on **ASSET-006** (Cryptographic Keys) for challenge-response authentication (`UDS 0x27` / `0x29 Authentication`).
* **Potential Consequences of Compromise:**
  * **Safety Impact:** Unauthorized execution of I/O control routines (`0x2F InputOutputControlByIdentifier`) can force main HV contactors open during high-speed driving (`HAZ-003`) or close contactors during maintenance (`HAZ-004`).
  * **Forensic Impact:** Unauthorized clearing of latched critical DTCs (e.g., welded contactor or thermal event records) hides safety-critical fault evidence.

---

### ASSET-005: CAN Communication
* **Description:** External automotive `CAN / CAN-FD` communication channels exchanging control requests, power limits, and fault notifications between the `Master BMS`, `VCU`, `OBC`, and `Thermal Management Controller`.
* **Security Objectives:** **Integrity**, **Availability**, and **Authenticity**.
* **Asset Owner:** Vehicle E/E Network & Communication Architecture Team.
* **Asset Location:** `Master BMS` CAN controller peripheral, CAN transceiver hardware, and vehicle powertrain CAN wiring harness.
* **External Interfaces:**
  * Vehicle powertrain `CAN / CAN-FD` bus (`VCU`, `OBC`, `TMS`).
* **Security Properties:**
  * Safety- and security-critical CAN frames must be protected against message spoofing, tampering, and replay attacks via Secure Onboard Communication (`SecOC` MACs + freshness values) (`Integrity` & `Authenticity`).
  * Bus bandwidth and message reception must remain resilient against flooding/DoS (`Availability`).
* **Dependencies:** Relies on **ASSET-006** (Cryptographic Keys) for `SecOC` Message Authentication Code (MAC) generation/verification.
* **Potential Consequences of Compromise:**
  * **Safety Impact:** Spoofed `HV_Enable_Request` or corrupted `MaxChargeCurrent` messages cause unintended HV energization or overcharging; CAN bus flooding causes communication timeout (`HAZ-003` / `FMEA-006`), triggering emergency HV disconnection.
  * **Operational Impact:** Loss of propulsion or inability to charge the vehicle.

---

### ASSET-006: Cryptographic Keys
* **Description:** Symmetric and asymmetric cryptographic key material stored in the BMS, including Secure Boot public verification keys, firmware signature verification keys, `SecOC` symmetric MAC keys, and UDS diagnostic authentication keys/certificates.
* **Security Objectives:** **Confidentiality** and **Integrity**.
* **Asset Owner:** Automotive Cybersecurity & PKI Governance Team.
* **Asset Location:** Isolated **Hardware Security Module (HSM)** / Secure Key Storage inside the `Master MCU` (never stored in plaintext application Flash).
* **External Interfaces:**
  * Internal hardware-isolated mailbox interface between `Master MCU` application core and HSM core.
  * Secure key injection interface during Tier-1 ECU manufacturing.
* **Security Properties:**
  * Private and symmetric keys must never be readable outside the HSM boundary (`Confidentiality`).
  * Root public keys and key attributes must be immutable or protected against unauthorized replacement (`Integrity`).
* **Dependencies:** Root-of-Trust hardware protections in the `Master MCU` silicon.
* **Potential Consequences of Compromise:**
  * **System-Wide Impact:** Extraction or replacement of cryptographic keys compromises the entire BMS trust anchor—allowing an attacker to sign malicious firmware (**ASSET-001**), forge `SecOC` CAN commands (**ASSET-005**), and bypass diagnostic authentication (**ASSET-004**).

---

### ASSET-007: Software Update Package
* **Description:** Encrypted and digitally signed binary firmware/calibration update image transferred to the BMS during Over-The-Air (OTA) vehicle updates or workshop service reflashing.
* **Security Objectives:** **Authenticity**, **Integrity**, and **Confidentiality**.
* **Asset Owner:** Vehicle OTA & Software Release Engineering Team.
* **Asset Location:** Transmitted over vehicle network from Telematics/Central Gateway into `Master MCU` Flash staging bank.
* **External Interfaces:**
  * `CAN / CAN-FD` UDS flashing interface (`0x34 RequestDownload`, `0x36 TransferData`, `0x37 RequestTransferExit`).
* **Security Properties:**
  * Package origin and integrity must be verified via digital signature before installation (`Authenticity` & `Integrity`).
  * Anti-rollback version counters must prevent downgrading to older firmware with known vulnerabilities (`Integrity`).
  * Payload encryption protects proprietary control algorithms during transit (`Confidentiality`).
* **Dependencies:** Relies on **ASSET-006** (Cryptographic Keys) for signature verification and decryption, and directly updates **ASSET-001** (BMS Firmware) and **ASSET-002** (Battery Calibration Data).
* **Potential Consequences of Compromise:**
  * **Safety & Fleet Impact:** Injection of unauthorized or tampered firmware compromises BMS safety functions across a single vehicle or remotely across an entire vehicle fleet; rollback attacks re-enable patched security vulnerabilities.
