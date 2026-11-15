# 05 Behavioural Architecture — Operational Scenarios

## 1. Overview & Purpose
This document defines the behavioral execution flows of the Battery Management System (BMS) across normal operating modes and critical fault conditions. Each scenario specifies the interaction sequence between the logical subsystems (`Master_Controller`, `Monitoring`, `Estimation`, `Energy_Management`, `HV_Management`, and `Diagnostics`) and traces back to system-level requirements.

---

## 2. Normal Operational Scenarios

### Scenario 1: Normal Battery Startup
* **Preconditions:**
  * BMS low-voltage (LV) supply is off; main HV contactors (`ContactorState`) are open.
  * No latched critical Diagnostic Trouble Codes (DTCs) exist in non-volatile memory.
  * High-Voltage Interlock Loop (`HVILStatus`) is physically closed.
* **Trigger:**
  * Ignition / Wake-up signal is asserted by the Vehicle Control Unit (VCU).
* **Main Sequence:**
  1. `Master_Controller` initializes internal state machines and transitions from `OFF` to `INIT`.
  2. `Monitoring` performs self-checks and begins publishing `CellVoltage`, `CellTemperature`, and `PackCurrent`.
  3. `Diagnostics` verifies sensor plausibility (`SensorPlausibilityStatus`) and confirms zero active critical faults (`BatteryFaultStatus`).
  4. `HV_Management` verifies `HVILStatus` continuity, confirms `InsulationResistance` is within safe bounds, and verifies contactors are not welded open/closed.
  5. `Estimation` loads stored `BatterySoH`, computes initial `BatterySoC`, and publishes valid state estimates.
  6. Upon receiving an HV-enable request from the VCU, `Master_Controller` sends `ContactorControlRequest = PRECHARGE` to `HV_Management`.
  7. `HV_Management` closes the negative main contactor and pre-charge contactor, monitoring DC-link voltage rise until it matches `PackVoltage` within tolerance.
  8. `HV_Management` closes the positive main contactor, opens the pre-charge contactor, and reports `ContactorState = CLOSED`.
  9. `Master_Controller` transitions to `READY / RUN` and enables `Energy_Management` to publish `MaxChargeCurrent` and `MaxDischargeCurrent`.
* **Expected Result:**
  * HV bus is safely energized without inrush current spikes, and the BMS reports `READY` status to the VCU.
* **Fault Handling:**
  * If pre-charge fails to reach target voltage within the timeout window, `HV_Management` aborts the sequence, opens all contactors, and `Diagnostics` logs a pre-charge timeout DTC.
  * If `HVILStatus` is open or `InsulationResistance` is below threshold, startup halts in `STANDBY` and inhibits contactor closure.
* **Related Requirements:**
  * `SYS-REQ-001` (Controlled Startup & Self-Test), `SYS-REQ-002` (Pre-Charge Sequencing), `SYS-REQ-003` (HVIL & Isolation Verification).

---

### Scenario 2: Normal Battery Charging
* **Preconditions:**
  * BMS is in `READY` or `STANDBY` state with all cell voltages, temperatures, and isolation values within normal operating limits.
  * Charger / EVSE is physically connected and handshake is established via VCU or charge controller.
* **Trigger:**
  * VCU requests `OperatingMode = CHARGING` while `BatterySoC` is below the target charge threshold.
* **Main Sequence:**
  1. `Master_Controller` validates charging preconditions with `Diagnostics` and transitions `OperatingMode` to `CHARGING`.
  2. `HV_Management` ensures main contactors are closed (`ContactorState = CLOSED`).
  3. `Energy_Management` continuously computes `MaxChargeCurrent` based on `BatterySoC`, `BatterySoH`, `CellVoltage`, and `CellTemperature`.
  4. `Master_Controller` transmits `MaxChargeCurrent` and `BatterySoC` over CAN to the VCU / On-Board Charger (OBC).
  5. As charging progresses, `Monitoring` tracks individual `CellVoltage` values and `PackCurrent`.
  6. Once cell voltages enter the balancing threshold window, `Energy_Management` issues `CellBalancingCommand` to `Monitoring` to equalize cell charge.
  7. As `BatterySoC` approaches 100% (or top cell reaches upper voltage limit), `Energy_Management` tapers `MaxChargeCurrent` down to 0 A.
  8. Upon charge completion, `Master_Controller` transitions `OperatingMode` to `STANDBY` and commands contactor opening if requested by VCU.
* **Expected Result:**
  * Battery charges safely within cell voltage and thermal limits with balanced cell voltages and accurate SoC reporting.
* **Fault Handling:**
  * If `CellTemperature` approaches upper limits, `Energy_Management` dynamically reduces `MaxChargeCurrent` (thermal derating).
  * If charger current exceeds `MaxChargeCurrent` beyond tolerance, `Diagnostics` triggers an over-current fault and `HV_Management` opens contactors.
* **Related Requirements:**
  * `SYS-REQ-010` (Dynamic Charge Current Limiting), `SYS-REQ-011` (Cell Balancing Control), `SYS-REQ-012` (Charge Termination).

---

### Scenario 3: Normal Battery Discharging
* **Preconditions:**
  * BMS is in `READY / DRIVE` state with `ContactorState = CLOSED`.
  * `BatterySoC` is above the minimum reserve threshold and no critical faults are active.
* **Trigger:**
  * VCU requests `OperatingMode = DISCHARGING` (vehicle propulsion or load demand draws negative `PackCurrent`).
* **Main Sequence:**
  1. `Master_Controller` sets `OperatingMode = DISCHARGING`.
  2. `Energy_Management` continuously calculates `MaxDischargeCurrent` using `BatterySoC`, `BatterySoH`, minimum `CellVoltage`, and `CellTemperature`.
  3. `Master_Controller` broadcasts `MaxDischargeCurrent` and `BatterySoC` via CAN to the VCU at 50–100 ms intervals.
  4. `Monitoring` acquires `PackCurrent` and `CellVoltage` at 10 ms intervals to detect transient voltage sags under peak load.
  5. `Estimation` integrates `PackCurrent` and updates `BatterySoC` and internal resistance models.
  6. As `BatterySoC` depletes toward minimum operational limits, `Energy_Management` progressively tapers `MaxDischargeCurrent` to prevent deep discharge.
* **Expected Result:**
  * Pack delivers requested power while maintaining all cells inside the Safe Operating Area (SOA).
* **Fault Handling:**
  * If any cell approaches minimum voltage under heavy load, `Energy_Management` sharply reduces `MaxDischargeCurrent` to clamp voltage drop.
  * If `BatterySoC` reaches critical empty threshold, `Master_Controller` signals depleted status and prepares for controlled HV disconnect.
* **Related Requirements:**
  * `SYS-REQ-020` (Dynamic Discharge Power Limiting), `SYS-REQ-021` (Under-Voltage Protection), `SYS-REQ-022` (SoC Tracking Under Load).

---

## 3. Fault & Edge-Case Scenarios

### Scenario 4: Cell Overvoltage Detection
* **Preconditions:**
  * BMS is active (`CHARGING` or regenerative braking during `DISCHARGING`) with `ContactorState = CLOSED`.
* **Trigger:**
  * `Monitoring` measures one or more `CellVoltage` values exceeding the defined Overvoltage (OV) threshold.
* **Main Sequence:**
  1. `Monitoring` detects `CellVoltage > OV_Threshold` within its 10 ms acquisition cycle and sets a raw OV flag in `SensorPlausibilityStatus`.
  2. `Diagnostics` evaluates the raw OV flag against the configured debounce timer to filter measurement noise.
  3. Upon debounce expiration, `Diagnostics` confirms the Cell Overvoltage fault, logs the corresponding DTC, and updates `BatteryFaultStatus`.
  4. For a Warning-level OV, `Diagnostics` sends `DeratingFactor` to `Energy_Management`, which sets `MaxChargeCurrent = 0 A`.
  5. For a Critical-level OV, `Diagnostics` asserts `EmergencyOpenRequest = TRUE` to `HV_Management` and notifies `Master_Controller`.
  6. `Master_Controller` transitions to `FAULT_SAFE_STATE` and broadcasts the critical fault status on CAN.
  7. `HV_Management` opens the main HV contactors to physically isolate the battery pack.
* **Expected Result:**
  * Charging or regenerative current is halted immediately, preventing electrolyte decomposition, venting, or thermal runaway.
* **Fault Handling:**
  * If primary contactor opening fails under load, `HV_Management` triggers redundant isolation mechanisms (e.g., pyro-fuse) if equipped.
  * Fault remains latched until `CellVoltage` drops below the recovery hysteresis and a valid diagnostic clear/reset cycle occurs.
* **Related Requirements:**
  * `SAF-REQ-001` (Overvoltage Detection Latency), `SAF-REQ-002` (Emergency HV Isolation), `SYS-REQ-030` (Fault Debouncing & Latching).

---

### Scenario 5: Battery Overtemperature Detection
* **Preconditions:**
  * BMS is active in any operational mode (`STANDBY`, `CHARGING`, or `DISCHARGING`).
* **Trigger:**
  * `Monitoring` reads one or more `CellTemperature` sensors exceeding Warning or Critical Overtemperature (OT) thresholds.
* **Main Sequence:**
  1. `Monitoring` publishes updated `CellTemperature` values at 100 ms intervals.
  2. `Diagnostics` compares maximum cell temperature against Warning and Critical thresholds and runs debounce filtering.
  3. **Stage 1 (Warning Threshold Exceeded):**
     * `Diagnostics` issues `DeratingFactor` to `Energy_Management` and raises a thermal warning flag in `BatteryFaultStatus`.
     * `Energy_Management` scales down `MaxChargeCurrent` and `MaxDischargeCurrent` proportionally to temperature rise and requests maximum cooling via VCU.
  4. **Stage 2 (Critical Threshold Exceeded):**
     * `Diagnostics` confirms Critical Overtemperature, logs a critical DTC, and asserts `EmergencyOpenRequest = TRUE`.
     * `Master_Controller` enters `FAULT_SAFE_STATE` and notifies the VCU of imminent HV disconnect.
     * `HV_Management` opens all main contactors to remove Joule heating ($I^2R$) losses.
* **Expected Result:**
  * Thermal generation is reduced via progressive power derating and completely stopped via HV isolation if temperatures reach critical limits.
* **Fault Handling:**
  * If rapid temperature rise ($dT/dt$) indicates potential thermal runaway, `Diagnostics` bypasses standard derating and immediately triggers `EmergencyOpenRequest` plus VCU thermal event warning.
* **Related Requirements:**
