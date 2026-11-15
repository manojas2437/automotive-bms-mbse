# 04 Logical Architecture — Battery Management System (BMS)

## 1. Overview & Purpose
This document defines the logical architecture of the Battery Management System (BMS) and documents the underlying **Architecture Decisions (ADs)**. Rather than describing only what logical blocks exist, this specification explains the engineering rationale, trade-offs, system consequences, and verification methods behind each structural boundary.

---

## 2. Logical Subsystem Breakdown

### 2.1 Master BMS Controller
* **Role:** Acts as the central decision-making authority, state machine coordinator, and external communication gateway (e.g., to the Vehicle Control Unit or Energy Management System).
* **Why It Is Needed:**
  * **Single Source of Truth:** Consolidates data from distributed cell-monitoring units (CMUs) into a unified pack-level state.
  * **Deterministic Arbitration:** Resolves conflicting requests between charging, discharging, thermal management, and fault handling through a centralized operating mode state machine.
  * **Safety & Isolation Boundary:** Enforces pack-level safety goals (ISO 26262) and manages high-voltage (HV) contactor sequencing without relying on distributed slave nodes to make pack-wide decisions.
  * **External Interface Abstraction:** Presents a single, standardized communication interface (CAN/Ethernet) to the host vehicle or grid controller, hiding internal cell topology.

### 2.2 Separation of Monitoring and Estimation
* **Monitoring (Data Acquisition):** Handles hardware-close signal conditioning, analog-to-digital conversion (ADC) synchronization, plausibility checks, and raw physical measurements (cell voltages, pack current, temperatures).
* **Estimation (State Calculation):** Executes algorithmic models (e.g., Extended Kalman Filters, coulomb counting, impedance tracking) to compute non-measurable internal states such as State of Charge (SoC), State of Health (SoH), State of Power (SoP), and State of Energy (SoE).
* **Why They Are Separated:**
  * **Independent Update Rates:** Raw safety monitoring requires fast, deterministic execution loops (1–10 ms) for over-voltage/over-current protection, whereas complex state observers run on slower schedules (50–1000 ms).
  * **Algorithmic Independence:** Allows battery modeling algorithms to be upgraded or swapped for different cell chemistries (e.g., NMC vs. LFP) without altering low-level sensor acquisition drivers.
  * **Testability:** Enables Hardware-in-the-Loop (HiL) and Software-in-the-Loop (SiL) validation of estimation models using recorded or synthetic measurement datasets.

### 2.3 Separation of High-Voltage (HV) Management and Energy Management
* **HV Management (Safety & Switching):** Controls physical galvanic isolation, main contactors, pre-charge circuits, pyro-fuses, High-Voltage Interlock Loops (HVIL), and insulation resistance monitoring (IMD).
* **Energy Management (Power & Balancing):** Calculates dynamic charge/discharge power limits (SoP), manages passive or active cell balancing, and coordinates thermal conditioning requests.
* **Why They Are Separated:**
  * **Safety Integrity Level (ASIL) Decoupling:** HV switching directly prevents electrocution and thermal runaway, typically requiring higher functional safety integrity (e.g., ASIL C/D) than energy optimization functions (e.g., ASIL A/B or QM).
  * **Failure Containment:** A software fault or calibration error in power limit calculation or cell balancing cannot inadvertently open contactors under load or bypass pre-charge sequencing.
  * **Clear Responsibility:** Separates *whether* the battery is safe to connect (HV Management) from *how much* energy can be exchanged once connected (Energy Management).

### 2.4 Diagnostic Subsystem Interactions
The Diagnostic Manager operates as a cross-cutting logical function that continuously supervises all other subsystems without owning primary control loops.

* **Interaction with Monitoring:** Receives raw sensor out-of-range flags, open-wire detections, ADC CRC errors, and plausibility mismatches (e.g., current sensor redundancy checks).
* **Interaction with Estimation:** Monitors model convergence flags, covariance bounds, and parameter drift to detect degraded estimation confidence.
* **Interaction with HV Management:** Reads contactor weld-detection feedback, pre-charge timeout status, HVIL continuity, and insulation fault triggers. Issues immediate safe-state transition requests upon critical fault confirmation.
* **Interaction with Energy Management:** Sends derating requests (e.g., reducing allowable charge/discharge current limits) when non-critical faults occur (e.g., single temperature sensor loss or over-temperature warning).
* **Interaction with Master Controller & External Tester:** Logs Diagnostic Trouble Codes (DTCs), manages fault debouncing/healing counters, broadcasts fault status to the host system, and serves UDS (ISO 14229) diagnostic requests.

### 2.5 Support for Future Hardware Reuse
The logical architecture decouples application logic from physical hardware topology to maximize reuse across vehicle platforms and battery pack variants:

* **Hardware Abstraction Layer (HAL) Boundary:** Monitoring interfaces normalize physical sensor inputs into standard engineering units (mV, mA, °C), isolating upper layers from specific Analog Front-End (AFE) ICs or shunt/Hall-effect current sensors.
* **Parameterized Topology:** Logical components reference configurable pack parameters (number of cells in series/parallel, thermal zone count, contactor count) rather than hardcoded array sizes.
* **Chemistry-Agnostic Interfaces:** Standardized data contracts between Monitoring, Estimation, and Energy Management allow switching cell chemistries or module layouts by updating calibration tables and estimation models while reusing the Master Controller, HV Management, and Diagnostic frameworks intact.

---

## 3. Architecture Decision Records (ADRs)

### Architecture Decision AD-001: Centralization of Master BMS Control
* **Decision:** Pack-level state arbitration, mode management, and external host communication are centralized in a single logical Master BMS Controller.
* **Reason:** Prevents split-brain fault handling across distributed slave modules and provides a single deterministic authority for safety-critical state transitions.
* **Consequence:** All distributed measurement nodes must maintain reliable internal communication links to the Master Controller; loss of communication triggers a defined fail-safe state.
* **Verification:** System-level state transition tests, communication loss fault-injection tests, and latency budget analysis.

### Architecture Decision AD-002: Separation of Monitoring and Estimation
* **Decision:** Battery measurements (acquisition/plausibility) and battery state estimation (SoC, SoH, SoP) are implemented as separate logical components.
* **Reason:** Improves modularity, testability, and maintainability while allowing fast safety monitoring loops to run independently of slower state-observer algorithms.
* **Consequence:** Measurement data and signal quality flags must be transferred through strictly defined, versioned interfaces.
* **Verification:** Interface contract tests, timing/scheduling analysis, and SiL/HiL model-validation tests using prerecorded drive cycles.

### Architecture Decision AD-003: Separation of HV Management and Energy Management
* **Decision:** Physical high-voltage switching/isolation control (HV Management) is separated from power-limit computation and cell balancing (Energy Management).
* **Reason:** Isolates high-ASIL safety functions (contactor control, pre-charge, HVIL) from lower-ASIL optimization functions, reducing safety certification scope and preventing unintended contactor actuation.
* **Consequence:** Energy Management cannot directly actuate contactors; it must request power states through the Master Controller and respect HV Management readiness flags.
* **Verification:** Freedom-from-interference (FFI) analysis, fault-tree verification, and HiL contactor-sequencing tests under fault conditions.

### Architecture Decision AD-004: Cross-Cutting Diagnostic Architecture
* **Decision:** Fault detection, debouncing, derating coordination, and DTC storage are consolidated into a dedicated Diagnostic subsystem interacting via standardized fault-reporting interfaces.
* **Reason:** Ensures consistent fault-handling behavior (debouncing, safe-state escalation, and UDS reporting) across all functional blocks rather than duplicating error logic inside each component.
* **Consequence:** Every logical component must expose standardized health status and fault-event signals to the Diagnostic subsystem and accept derating/safe-state commands.
* **Verification:** Fault-injection testing across all sensor and actuator interfaces, DTC validation against UDS specifications, and derating response-time measurements.

### Architecture Decision AD-005: Hardware-Independent Logical Interfaces
* **Decision:** All logical components above the Monitoring and HV actuator abstraction boundaries communicate exclusively using physical SI/engineering units and parameterized pack dimensions.
* **Reason:** Enables reuse of core BMS application software across different AFE chips, contactor configurations, pack voltages, and cell chemistries without rewriting control logic.
* **Consequence:** Requires an explicit adaptation/mapping layer for each new hardware platform and strict adherence to interface abstraction rules during code reviews.
* **Verification:** Static architecture compliance checks, multi-configuration builds (varying series/parallel counts), and portability testing across target ECU hardware variants.
