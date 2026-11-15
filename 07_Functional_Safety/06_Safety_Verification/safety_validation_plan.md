# BMS Safety Validation Plan

## 1. Objective
Validate the safety-related functions and safety mechanisms of the **400 V High-Voltage Battery Management System (HV-BMS)** in accordance with **ISO 26262-4** and **ISO 26262-6**. This plan defines the validation scope, test environments, execution approach, and pass/fail acceptance criteria required to verify that all Safety Goals (`SG-001` through `SG-005`), Functional Safety Requirements (`FSR-001` through `FSR-013`), and Technical Safety Requirements (`TSR-001` through `TSR-015`) operate effectively under normal and fault conditions.

---

## 2. Scope
This validation plan covers the following safety-relevant BMS functions and hardware/software interfaces:
* **Cell voltage monitoring:** 96-series cell voltage acquisition accuracy, open-wire detection, internal communication integrity (`isoSPI` CRC/counters), and overvoltage/undervoltage protection (`SG-001`).
* **Temperature monitoring:** NTC thermistor out-of-range/open/short diagnostics, spatial plausibility checks, thermal power derating, and critical overtemperature HV isolation (`SG-002`).
* **Current monitoring:** Bidirectional pack current acquisition, dual-channel plausibility cross-checks, overcurrent protection, and dynamic charge/discharge current limiting (`SG-005`).
* **Contactor management:** DC-link pre-charge sequencing, dual-switch (high-side/low-side) driver control, hardware HVIL interlock gating, contactor state feedback supervision, and welded-contactor detection (`SG-003`, `SG-004`).
* **Fault detection:** Fault debouncing, Diagnostic Trouble Code (DTC) persistence, external window watchdog hardware safe-state actuation (`SAFE_STATE_N`), and MCU memory/program-flow diagnostics (`TSR-014`, `TSR-015`).
* **Communication diagnostics:** End-to-End (E2E) CRC/alive-counter validation and timeout fallback handling on external `CAN` (VCU/OBC) and internal daisy-chain interfaces (`TSR-002`, `TSR-005`).

---

## 3. Test Environment
Validation activities are distributed across four progressive test environments to verify both isolated algorithmic behavior and full physical ECU hardware integration:

* **MATLAB/Simulink (MIL – Model-in-the-Loop):**
  * Executes control models, Master BMS state machines, and electro-thermal 96S battery pack plant models to validate state transitions, thermal derating curves, and fault-reaction logic prior to target code deployment.
* **Software-in-the-Loop (SIL):**
  * Runs compiled production C application software in a virtualized ECU environment to verify integrated safety software partitions, RTOS task scheduling, E2E communication libraries, and diagnostic debounce timers.
* **Hardware-in-the-Loop (HIL):**
  * Connects the physical Master BMS and Cell Monitoring Unit (CMU) hardware to a real-time 96-channel battery cell simulator, programmable HV/LV power supplies, simulated contactor loads, and CANoe bus simulation to test hardware/software interfaces, electrical fault injection, and external watchdog hardware cut-off paths.
* **Vehicle test environment:**
  * Integrates the complete HV-BMS into a prototype 400 V BEV test vehicle with a physical 96S lithium-ion pack, VCU, OBC, and thermal management system to validate end-to-end safety reactions during real-world driving, fast charging, and climatic testing.

---

## 4. Validation Approach
* **Normal operating conditions:**
  * Execute complete nominal operational cycles (`Initialization` → `SelfTest` → `Standby` → `Precharge` → `Operating` → `Charging` / `Discharging` → `Shutdown`) to verify deterministic state transitions and confirm zero false-positive fault triggers.
* **Boundary conditions:**
  * Evaluate system stability and threshold accuracy at upper and lower cell voltage boundaries, warning/critical temperature thresholds, minimum/maximum SoC limits, and 12 V supply voltage extremes (6 V to 16 V).
* **Fault injection:**
  * Inject deterministic hardware, sensor, communication, and MCU execution faults (`FI-001` through `FI-007` in `fault_injection_scenarios.md`, including stuck cell voltage, NTC open circuit, current sensor offset, CAN timeout, MCU watchdog timeout, contactor feedback mismatch, and invalid charging requests) across SIL and HIL environments.
* **Diagnostic coverage:**
  * Verify that primary and independent redundant safety mechanisms (such as MCU software checks paired with AFE hardware comparators and external watchdog `SAFE_STATE_N` hardware disable lines) detect single-point and latent faults without common-cause interference (`DFA-001` through `DFA-005`).
* **Fault reaction timing:**
  * Measure end-to-end fault reaction time from physical fault injection trigger to safe-state attainment (main HV contactor coil de-energization and `MaxChargeCurrent = 0 A`) using hardware oscilloscopes and time-synchronized CAN logs to confirm compliance within allocated **Fault Tolerant Time Intervals (FTTIs)**.

---

## 5. Acceptance Criteria
A safety test case (`BMS-SFT-001` through `BMS-SFT-012`) or validation campaign shall be accepted as **PASSED** only when all of the following criteria are satisfied:
* **Requirement-specific thresholds satisfied:** All detection thresholds, debounce intervals, and measurement tolerances comply with the approved Technical Safety Requirements (`TSR-001` through `TSR-015`).
* **Expected diagnostic detected:** The target fault condition is accurately identified, debounced, and logged as the expected Diagnostic Trouble Code (DTC) in non-volatile memory.
* **Defined safety reaction executed:** The BMS transitions deterministically to its required safe state (main HV contactors physically **OPEN** and dynamic current limits clamped to `0 A`).
* **No unintended side effects:** Fault detection and recovery actions do not cause unintended contactor chatter, loss of diagnostic communication, or violation of any other Safety Goal.
* **Verification evidence recorded:** Raw test execution logs, oscilloscope timing captures, CAN bus traces, firmware build hashes, and signed test reports are archived and traced in `safety_test_cases.csv` and `02_Requirements/traceability_matrix.csv`.
