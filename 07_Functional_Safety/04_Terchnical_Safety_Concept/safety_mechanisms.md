# 04 Technical Safety Concept — Safety Mechanisms Specification

## 1. Purpose & Architectural Context
This document defines the hardware and software **Safety Mechanisms** implementing the Technical Safety Requirements (`TSR-001` through `TSR-015`) in accordance with **ISO 26262-4**. It describes *how* the BMS technical architecture detects random hardware failures and systematic faults, achieves required diagnostic coverage, and transitions the system to its safe state (main HV contactors physically **OPEN**).

> **Architectural Independence & ASIL Justification Note:** In accordance with ISO 26262-4, a single MCU, watchdog, or sensor cannot be assumed sufficient for high-ASIL safety goals (such as ASIL C/D overvoltage, thermal runaway, or unintended HV energization). Required **Diagnostic Coverage (DC)**, **hardware architectural metrics** (SPFM, LFM, PMHF), **Freedom from Interference (FFI)**, and **redundant/diverse hardware paths** (e.g., independent AFE hardware comparators alongside MCU software checks, and external watchdog hardware disable paths) must be formally justified against the finalized HARA ASIL ratings during Hardware Architectural Metric evaluation.

---

## 2. Safety Mechanisms Breakdown

### 2.1 Voltage Monitoring Mechanisms (`TSR-001` to `TSR-005`)
* **Cell Voltage Acquisition:**
  * Dedicated Cell Monitoring ICs (AFEs) sample all 96 series cell voltages synchronously using internal precision voltage references.
* **Measurement Range & Validity Validation:**
  * **Open-Wire Detection:** Periodic weak pull-down/pull-up current injection checks verify sense-wire continuity to every cell tap.
  * **ADC & Reference Diagnostics:** Redundant internal reference checks and MUX self-tests detect stuck ADC channels or reference drift.
  * **Communication Integrity:** Isolated daisy-chain communication (`isoSPI`) between CMUs and Master MCU uses CRC-16, message counters, and timeout supervision.
* **Overvoltage & Undervoltage Detection:**
  * Primary software threshold evaluation in the Master MCU is paired with an independent hardware comparator path inside the Cell Monitoring IC to avoid common-cause failure.
* **Fault Reactions:**
  * Debounced overvoltage warning commands `MaxChargeCurrent = 0 A` via CAN (`OBC`/`VCU`).
  * Critical overvoltage asserts the hardware safe-state disable line to the `Contactor Driver` and opens the main HV contactors.

### 2.2 Temperature Monitoring Mechanisms (`TSR-006`, `TSR-007`)
* **Cell & Module Temperature Measurement:**
  * Distributed NTC thermistors are read through conditioned ADC channels with ratiometric excitation to eliminate supply-voltage drift errors.
* **Sensor Fault Detection:**
  * Hardware pull-up/pull-down bias networks pull disconnected or shorted sensor lines outside the valid physical voltage window, immediately flagging **short-to-GND**, **short-to-supply**, or **open-circuit** faults.
  * Spatial plausibility checks compare adjacent thermal zone sensors to detect stuck-in-range thermistors.
* **Overtemperature Detection:**
  * Multi-stage threshold evaluation detects both absolute overtemperature limits and rapid temperature rise rates ($dT/dt$).
* **Protective Actions:**
  * Warning stage issues maximum cooling requests to the `Thermal Management` interface and applies progressive power derating (`MaxChargeCurrent` / `MaxDischargeCurrent`).
  * Critical stage triggers `Diagnostic Manager` safe-state transition, opening HV contactors to eliminate Joule ($I^2R$) heating.

### 2.3 Current Monitoring Mechanisms (`TSR-012`, `TSR-013`)
* **Charge & Discharge Current Acquisition:**
  * Bidirectional pack current is measured continuously via a precision shunt or dual-range Hall-effect sensor.
* **Current Sensor Plausibility Validation:**
  * **Dual-Channel / Cross-Check Plausibility:** Primary current measurement is cross-checked against a secondary redundant sensing channel (or Coulomb-balance / pack-voltage $dV/dt$ model) to detect gain drift or frozen outputs.
  * **Zero-Current Offset Calibration:** Offset drift is verified whenever `ContactorState == OPEN`.
* **Overcurrent Detection:**
  * Fast hardware overcurrent comparator and software $I^2t$ thermal integration detect instantaneous short-circuit surges and sustained overcurrent conditions.
* **Protective Actions:**
  * Overcurrent or plausibility loss forces dynamic power limits to `0 A` and commands controlled or immediate HV contactor opening depending on fault severity.

### 2.4 Contactor Monitoring Mechanisms (`TSR-008` to `TSR-011`)
* **Commanded vs. Actual State Supervision:**
  * High-voltage differential measurement across each contactor pole (pack-side vs. load-side voltage) and/or mechanically linked mirror auxiliary contacts verify physical switch position against `ContactorControlRequest`.
* **Welded Contactor Detection:**
  * During startup (`SelfTest`) and shutdown sequences, contactors are actuated one pole at a time while measuring bus voltage transfer to identify a single welded main contactor.
* **Unexpected Contactor Opening Detection:**
  * Continuous feedback polling during `Operating`, `Charging`, and `Discharging` detects unintended coil drop-out or auxiliary contact opening and immediately notifies the `VCU`.
* **Prevention of Unsafe HV Activation:**
  * **Dual-Switch Architecture:** Both high-side and low-side contactor coil drivers must be independently enabled to energize a contactor coil, preventing single-point transistor shorts from closing a contactor.
  * **Hardware Interlock Gating:** Hardware HVIL loop continuity directly gates the contactor driver enable supply, physically inhibiting closure if an HV connector is unmated.

### 2.5 MCU Monitoring Mechanisms (`TSR-005`, `TSR-014`, `TSR-015`)
* **External Window Watchdog Supervision:**
  * An independent external safety watchdog (e.g., SBC / System Basis Chip) monitors periodic challenge-response / window trigger pulses from the `Master MCU`.
  * Upon missed, early, or late watchdog servicing, the watchdog asserts an independent hardware `SAFE_STATE_N` pin that directly disables the `Contactor Driver` stage without relying on MCU software.
* **Memory & Program-Flow Diagnostics:**
  * Hardware Error-Correcting Code (ECC) protects Flash and SRAM against single-bit upsets and detects double-bit errors.
  * Runtime program-flow monitoring (logical and temporal checkpoints) verifies execution order of safety-critical tasks (`Monitoring`, `Diagnostics`, `HV_Management`).
  * Startup Logic BIST (LBIST) and Memory BIST (MBIST) detect latent hardware faults prior to enabling HV operation.
* **Communication Monitoring:**
  * All safety-related CAN messages (`VCU`, `OBC`) and internal `isoSPI` frames implement **End-to-End (E2E) protection** (CRC checksum, rolling sequence counter, and timeout monitoring) per ISO 26262-6.
* **Centralized Error Handling:**
  * `Diagnostic Manager` aggregates fault flags, applies deterministic debouncing, latches critical DTCs in non-volatile memory, and coordinates safe-state transitions.
