# 05 Safety Analysis — Dependent Failure Analysis (DFA)

## 1. Purpose & Scope
In accordance with **ISO 26262-9**, this Dependent Failure Analysis (DFA) evaluates potential **Common-Cause Failures (CCFs)** and **Cascading Failures** that could violate independence between redundant safety mechanisms or architectural elements in the master/slave 400 V BMS architecture.

---

## 2. Architectural Independence Assessment

### 2.1 Do voltage and temperature measurements share a power supply?
* **Vulnerability:** In distributed Cell Monitoring Units (CMUs), individual cell voltages and module NTC thermistors are typically acquired by the same Analog Front-End (AFE) IC. If the AFE internal voltage regulator ($V_{REG}$ / ADC reference) drifts or fails, both cell voltage readings and ratiometric NTC temperature measurements on that slave module can be corrupted simultaneously.
* **Impact:** A single AFE power-supply fault could mask both an overvoltage condition (`SG-001`) and an overtemperature condition (`SG-002`) for an entire cell group.
* **Architectural Mitigation:**
  * Implement an **independent secondary reference voltage** inside the Cell Monitoring IC checked on every conversion cycle.
  * Power the AFE overvoltage hardware comparator from a separate internal supply domain from the main ADC multiplexer.
  * Perform cross-module plausibility checks in the Master MCU (comparing pack sum voltage against individual cell sum, and comparing adjacent thermal zones across separate CMUs).

### 2.2 Can one MCU failure affect both monitoring and contactor control?
* **Vulnerability:** The `Master MCU` processes incoming sensor telemetry (`Monitoring` / `Diagnostics`) and generates the control signals (`ContactorControlRequest`) for the HV contactors. A single MCU clock failure, power rail brownout, or CPU lock-up could freeze fault detection while leaving contactor driver outputs latched in the `CLOSED` state.
* **Impact:** Violation of `SG-001`, `SG-002`, and `SG-005` because the system can neither detect a fault nor open the HV contactors.
* **Architectural Mitigation:**
  * **External Window Watchdog (`TSR-014`):** An independent System Basis Chip (SBC) / external watchdog monitors Master MCU execution via challenge-response pulses and directly drives a hardware `SAFE_STATE_N` pin that disables the `Contactor Driver` stage independently of MCU software.
  * **Hardware Bypass Path:** Critical overvoltage/overcurrent hardware fault lines from the sensing layer directly gate the contactor driver enable hardware without requiring MCU software intervention.

### 2.3 Can communication failures disable multiple safety functions?
* **Vulnerability:**
  1. **Internal Communication (`isoSPI` Daisy-Chain):** A broken wire, connector unmating, or common-mode EMI burst on the daisy-chain bus between the `Master MCU` and `CMUs` cuts off all 96 cell voltage readings and all module temperature readings simultaneously.
  2. **External Communication (`CAN` Bus):** A CAN transceiver failure or bus-off event prevents sending `MaxChargeCurrent = 0 A` to the `OBC` and fault notifications to the `VCU`.
* **Impact:** Loss of observability across the entire battery pack or inability to command external chargers to stop current flow.
* **Architectural Mitigation:**
  * **Bidirectional / Ring Daisy-Chain:** Route `isoSPI` in a reversible ring topology so a single wire break does not isolate any CMU slave node.
  * **Deterministic Timeout Safe State:** If `isoSPI` or `CAN` E2E checks fail beyond the timeout threshold, the BMS does not rely on external charger compliance; instead, `HV_Management` autonomously opens the main HV contactors to physically break the circuit.

### 2.4 Can software defects affect multiple redundant channels?
* **Vulnerability:** Even when hardware sensors are redundant (e.g., dual current channels or primary + secondary voltage thresholds), shared software libraries, common compiler bugs, shared RTOS scheduling queues, or unpartitioned RAM access can cause a single systematic software defect to corrupt both channels simultaneously.
* **Impact:** Common-cause software failure defeating logical redundancy.
* **Architectural Mitigation:**
  * **Freedom from Interference (FFI) per ISO 26262-6:** Use hardware Memory Protection Unit (MPU) spatial partitioning to isolate ASIL-rated safety partitions (`Monitoring`, `Diagnostics`, `HV_Management`) from QM partitions (`Estimation`, `Energy_Management`).
  * **Diverse Software Implementation:** Implement primary and secondary threshold checks using diverse data representations (e.g., physical floating-point/scaled integers vs. raw inverted ADC counts) and separate execution tasks.
  * **Static Analysis & Coding Standards:** Enforce MISRA C compliance, static code analysis, and 100% MC/DC structural coverage on ASIL C/D software components.

### 2.5 Are the safety mechanisms sufficiently independent?
* **Assessment Summary:** In a master/slave BMS architecture, achieving high-ASIL integrity (e.g., ASIL C/D for overvoltage, overtemperature, and unintended HV energization) requires strict separation between the **Intended Function Path** and the **Safety Mechanism Path**:

| Safety Function | Primary Path (Intended Function) | Independent Safety Mechanism Path | Independence Assessment |
| :--- | :--- | :--- | :--- |
| **Overvoltage Protection (`SG-001`)** | CMU Main ADC → `isoSPI` → Master MCU SW check → CAN `MaxChargeCurrent = 0` | CMU internal HW comparator (separate reference) → Hardware fault line → Contactor Driver disable | **Sufficient** if AFE silicon implements internal galvanic/supply isolation between ADC and comparator blocks. |
| **MCU Execution (`SG-001..005`)** | Master MCU main control loop & RTOS scheduler | External SBC Window Watchdog → Hardware `SAFE_STATE_N` pin → Contactor Driver power stage | **Sufficient** (diverse clock source, separate silicon die, independent power supply monitoring). |
| **Contactor Control (`SG-003` / `SG-004`)** | Master MCU GPIO command → High-Side Driver | Secondary safety enable → Low-Side Driver + Hardware HVIL interlock series gate | **Sufficient** (requires two independent failures to cause unintended closure; HVIL physically breaks coil supply). |
| **Current Plausibility (`SG-005`)** | Primary Shunt / Hall ADC channel | Secondary redundant sensor channel + pack $dV/dt$ model check | **Conditional** — requires separate power supply rails and physically separated signal routing for primary and secondary channels. |

---

## 3. Summary of Required DFA Follow-Up Actions
1. **Silicon Safety Manual Review:** Verify internal AFE block independence (reference voltage, clock, and comparator isolation) against the selected Cell Monitoring IC Safety Manual.
2. **PCB Layout & Pin-FMEA:** Perform pin-level FMEA on the Master MCU, AFE, and Contactor Driver connectors to confirm adjacent-pin shorts cannot defeat dual-channel isolation.
3. **Quantitative CCF Beta-Factor Estimation:** Apply ISO 26262-9 / IEC 61508 $\beta$-factor checklists during hardware architectural metric calculation (SPFM/LFM/PMHF).
