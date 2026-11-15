# 06 Safety Verification — Fault Injection Test Scenarios

## 1. Purpose & Execution Governance
This document specifies the **Fault Injection Scenarios (`FI-001` through `FI-007`)** used to verify the robustness and diagnostic effectiveness of the BMS safety mechanisms in accordance with **ISO 26262-4** and **ISO 26262-6**.

> **Verification Evidence Policy:** All test cases below are currently defined in `Planned` status. **No verification pass/fail claim or measured reaction time shall be recorded as verified until the physical/simulated test is executed on the target environment and traceable test logs are archived.**

---

## 2. Fault Injection Specifications

### FI-001: Cell Voltage Sensor Stuck at a Fixed Value
* **Related Artifacts:** `SG-001`, `FSR-001`, `FSR-005`, `TSR-001`, `TSR-002`, `FMEA-001`, `BMS-SFT-001`
* **Fault Injection Method:** On the Hardware-in-the-Loop (HiL) battery cell simulator (or via SPI/isoSPI register fault-injection interface), freeze a single cell voltage channel (`Cell_14`) at a nominal value (`3.65 V`) while ramping the remaining 95 cells upward during a simulated charging cycle.
* **Initial Conditions:** BMS in `Charging` state, `ContactorState = CLOSED`, all 96 cells balanced at `3.65 V`, charging current active at `50 A`.
* **Expected Diagnostic Response:** Measurement plausibility check detects divergence between `Cell_14` and neighboring cells / pack sum voltage, flags `Cell_14` voltage measurement as invalid, and logs a cell voltage plausibility DTC.
* **Expected Safety Reaction:** `Energy_Management` sets `MaxChargeCurrent = 0 A`, `Master_Controller` transitions to `Fault` mode, and `HV_Management` opens main contactors before adjacent cells exceed upper safety voltage limits.
* **Measured Reaction Time:** `TBD (To be recorded from HiL oscilloscope / CAN trace upon test execution)`
* **Pass/Fail Criteria:**
  * **Pass:** Plausibility fault is confirmed, charging current is inhibited (`0 A`), and contactors open within the allocated Fault Tolerant Time Interval (FTTI) without any cell exceeding the critical overvoltage limit.
  * **Fail:** Fault remains undetected, or charging continues unchecked past safe cell voltage boundaries.

---

### FI-002: Temperature Sensor Open Circuit
* **Related Artifacts:** `SG-002`, `FSR-006`, `FSR-007`, `TSR-006`, `TSR-007`, `FMEA-002`, `BMS-SFT-004`
* **Fault Injection Method:** Open a hardware breakout relay on NTC thermistor channel `Temp_03` on the HiL harness to simulate a broken sensor wire.
* **Initial Conditions:** BMS in `Discharging` state at `25 °C` ambient, `ContactorState = CLOSED`, normal discharge current (`100 A`).
* **Expected Diagnostic Response:** Hardware pull-up bias pulls ADC voltage above the upper valid threshold; `Monitoring` flags `Temp_03` out-of-range within acquisition cycle and `Diagnostics` confirms an open-circuit sensor DTC after debounce.
* **Expected Safety Reaction:** System substitutes a conservative worst-case temperature value for thermal calculations, requests cooling via `Thermal Management`, and applies defined power derating (`MaxChargeCurrent` / `MaxDischargeCurrent` reduced).
* **Measured Reaction Time:** `TBD (To be recorded from HiL test log)`
* **Pass/Fail Criteria:**
  * **Pass:** Open-circuit fault is detected within debounce limits, valid DTC is stored in NVM, and conservative thermal derating is applied immediately.
  * **Fail:** System interprets the open circuit as a valid cold temperature (e.g., `-40 °C`) and fails to log a sensor fault or apply derating.

---

### FI-003: Current Sensor Offset
* **Related Artifacts:** `SG-005`, `FSR-012`, `FSR-013`, `TSR-012`, `FMEA-003`, `BMS-SFT-009`
* **Fault Injection Method:** Inject a DC voltage offset (`+25 A` equivalent) onto the primary current sensor analog/digital signal on the HiL bench while keeping the redundant sensing channel at `0 A` (or actual load current).
* **Initial Conditions:** BMS in `Standby` (`ContactorState = OPEN`, true pack current = `0 A`) followed by transition to `Operating` (`ContactorState = CLOSED`).
* **Expected Diagnostic Response:** Zero-current offset check in `Standby` and dual-channel cross-check plausibility in `Operating` detect mismatch exceeding the defined plausibility band; `Diagnostics` confirms a current sensor plausibility DTC.
* **Expected Safety Reaction:** Coulomb counting integration is frozen, `MaxChargeCurrent` and `MaxDischargeCurrent` are clamped to `0 A`, and `HV_Management` transitions the pack to a safe isolated state (`ContactorState = OPEN`).
* **Measured Reaction Time:** `TBD (To be recorded from HiL test log)`
* **Pass/Fail Criteria:**
  * **Pass:** Offset fault is detected prior to or immediately upon HV activation, SoC corruption is prevented, and HV contactors are isolated.
  * **Fail:** BMS accepts the offset current as valid, allowing unmonitored overcurrent or corrupted SoC estimation.

---

### FI-004: CAN Communication Timeout
* **Related Artifacts:** `SG-003`, `SG-005`, `FSR-004`, `FSR-013`, `TSR-005`, `FMEA-006`, `BMS-SFT-011`
* **Fault Injection Method:** Stop transmission of periodic VCU heartbeat / command CAN frames on the HiL CANoe/bus simulator during active operation.
* **Initial Conditions:** BMS in `Discharging` state (`ContactorState = CLOSED`), active CAN traffic between VCU and BMS at nominal cycle rates.
* **Expected Diagnostic Response:** CAN E2E / timeout monitor detects missing VCU frames beyond the configured timeout threshold; `Diagnostics` confirms a VCU Lost Communication DTC.
* **Expected Safety Reaction:** `Energy_Management` forces `MaxChargeCurrent = 0 A` and `MaxDischargeCurrent = 0 A`, `Master_Controller` enters `COMM_LOSS_DEGRADED` / `Fault` mode, and `HV_Management` opens main contactors once pack current drops below safe-open threshold (or upon grace-period expiration).
* **Measured Reaction Time:** `TBD (To be recorded from CAN trace and contactor current probe)`
* **Pass/Fail Criteria:**
  * **Pass:** Timeout is detected deterministically, power limits drop to `0 A`, and contactors open safely without uncontrolled arcing.
  * **Fail:** BMS remains in `Discharging` indefinitely without VCU supervision, or drops contactors instantaneously under peak load without executing the defined ramp-down/grace logic.

---

### FI-005: MCU Watchdog Timeout
* **Related Artifacts:** `SG-001..SG-005`, `FSR-002`, `FSR-007`, `TSR-014`, `FMEA-004`, `BMS-SFT-010`
* **Fault Injection Method:** Trigger a debugger breakpoint or inject an infinite-loop fault task in the `Master MCU` firmware to halt periodic servicing of the external window watchdog.
* **Initial Conditions:** BMS in `Operating` state (`ContactorState = CLOSED`), external window watchdog actively supervising MCU challenge-response pulses.
* **Expected Diagnostic Response:** External SBC / window watchdog detects missed trigger window and latches a watchdog fault status bit.
* **Expected Safety Reaction:** External watchdog asserts hardware `SAFE_STATE_N` low independently of the frozen MCU, physically cutting power/enable to the `Contactor Driver` stage and opening all HV contactors, followed by a controlled MCU reset.
* **Measured Reaction Time:** `TBD (To be recorded via oscilloscope measuring last WDG pulse to contactor coil de-energization)`
* **Pass/Fail Criteria:**
  * **Pass:** Hardware `SAFE_STATE_N` asserts and main HV contactors open strictly via hardware path without requiring MCU software execution.
  * **Fail:** Contactors remain closed while the Master MCU is hung.

---

### FI-006: Contactor Feedback Mismatch
* **Related Artifacts:** `SG-003`, `SG-004`, `FSR-008`, `FSR-011`, `TSR-008`, `TSR-011`, `FMEA-005`, `BMS-SFT-006`, `BMS-SFT-008`
* **Fault Injection Method:**
  * *Sub-case A (Unintended Opening):* Force the auxiliary mirror contact feedback and load-side HV sense to indicate `OPEN` while `ContactorControlRequest = CLOSED`.
  * *Sub-case B (Welded Contactor):* Force the positive contactor feedback/voltage sense to indicate `CLOSED` after commanding `ContactorControlRequest = OPEN`.
* **Initial Conditions:**
  * *Sub-case A:* BMS in `Operating` (`ContactorState = CLOSED`).
  * *Sub-case B:* BMS executing `Shutdown` (`Operating` → `Standby`).
* **Expected Diagnostic Response:** `HV_Management` detects command-vs-feedback discrepancy; `Diagnostics` confirms Contactor Open-Fault (`Sub-case A`) or Contactor Weld DTC (`Sub-case B`).
* **Expected Safety Reaction:**
  * *Sub-case A:* De-energize all contactor coils, set current limits to `0 A`, transition to `Fault`, and notify VCU immediately.
  * *Sub-case B:* Command negative contactor `OPEN` to ensure single-pole galvanic isolation, latch non-volatile weld DTC, broadcast critical weld warning to VCU, and inhibit future startup.
* **Measured Reaction Time:** `TBD (To be recorded from HiL test log)`
* **Pass/Fail Criteria:**
  * **Pass:** Both mismatch conditions are detected within diagnostic debounce limits, safe isolation is maximized, and restart is inhibited on welded contactor.
  * **Fail:** BMS reports `ContactorState = CLOSED` during an open fault or permits normal `Standby` readiness with a welded contactor.

---

### FI-007: Invalid Battery Charging Request
* **Related Artifacts:** `SG-001`, `SG-004`, `SG-005`, `FSR-010`, `FSR-013`, `BMS-SFT-007`
* **Fault Injection Method:** Transmit a CAN `VCU_Mode_Request = CHARGE` from the HiL bus simulator while `HVILStatus = OPEN`, or while `BatterySoC = 100%` (at upper cell voltage limit), or with corrupted E2E CRC/counter.
* **Initial Conditions:** BMS in `Standby` (`ContactorState = OPEN`) for invalid precondition test; and BMS in `Operating` at `100% SoC` for overcharge-request test.
* **Expected Diagnostic Response:** `Master_Controller` / `HV_Management` rejects the invalid state transition request; `Diagnostics` logs an invalid request / E2E error or HVIL open status flag.
