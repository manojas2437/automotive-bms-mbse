# 05 Behavioural Architecture — State Machine Definitions

## 1. Overview & Modeling Scope
This document defines the conceptual state machine of the **Master BMS Controller** (`Master_Controller`). It specifies each operational state, its entry/do/exit behaviors, and the exact boolean transition guards and actions governing state changes.

> **Architectural Note:** This state machine represents a simplified conceptual model. A production BMS implementation typically introduces hierarchical substates (e.g., `Precharge_CloseNeg`, `Precharge_Ramp`, `Precharge_ClosePos`), explicit `Shutdown / Sleep` states, limp-home degraded modes, and non-volatile fault-latching rules per ISO 26262.

---

## 2. State Definitions

| State | Description | Entry / Do / Exit Behavior |
| :--- | :--- | :--- |
| **Initialization** | Initialize hardware and software | **Entry:** Boot MCU peripherals, initialize RTOS tasks, load NVM calibration & stored SoH.<br>**Do:** Establish internal communication with cell monitoring AFEs.<br>**Exit:** Set `Init_Complete = TRUE`. |
| **SelfTest** | Perform diagnostic checks | **Entry:** Start startup diagnostic sequence.<br>**Do:** Verify sensor plausibility, ADC CRC, HVIL continuity, insulation resistance, and contactor weld status.<br>**Exit:** Latch `SelfTest_Passed` status. |
| **Standby** | Battery ready but not actively delivering power | **Entry:** Ensure all main contactors are open; set `MaxChargeCurrent = 0 A` and `MaxDischargeCurrent = 0 A`.<br>**Do:** Publish live `BatterySoC`, `BatterySoH`, and readiness status to VCU.<br>**Exit:** Prepare HV management for pre-charge or shutdown. |
| **Precharge** | Pre-charge DC link | **Entry:** Close negative main contactor and pre-charge contactor; start pre-charge timer.<br>**Do:** Monitor DC-link voltage rise relative to `PackVoltage`.<br>**Exit:** Close positive main contactor and open pre-charge contactor upon completion (or open all on abort). |
| **Operating** | Battery system enabled | **Entry:** Confirm `ContactorState = CLOSED`; enable `Energy_Management` power limit calculation.<br>**Do:** Broadcast dynamic `MaxChargeCurrent` and `MaxDischargeCurrent`; await VCU mode direction.<br>**Exit:** Hold contactor state or prepare power ramp-down. |
| **Charging** | Battery accepts charging current | **Entry:** Enable active/passive cell balancing logic.<br>**Do:** Regulate `MaxChargeCurrent` per cell voltage/temperature limits; monitor charger compliance.<br>**Exit:** Disable cell balancing switches; taper `MaxChargeCurrent` to `0 A`. |
| **Discharging** | Battery delivers electrical power | **Entry:** Set discharge power limits active.<br>**Do:** Continuously update `MaxDischargeCurrent` and track `BatterySoC` under load.<br>**Exit:** Taper `MaxDischargeCurrent` to `0 A`. |
| **Fault** | Fault handling and defined safety reaction | **Entry:** Assert `EmergencyOpenRequest` (if critical), force current limits to `0 A`, log DTC, broadcast `BatteryFaultStatus`.<br>**Do:** Maintain safe isolated state and evaluate fault-healing/reset conditions.<br>**Exit:** Clear active fault flags upon valid reset/recovery. |

---

## 3. State Transition Table (Guards & Actions)

### 3.1 Startup & Self-Test Transitions

#### `Initialization → SelfTest`
* **Guard:**
  ```text
  Init_Complete == TRUE
  AND Internal_Comm_Established == TRUE
  AND Critical_HW_Fault == FALSE
  ```
* **Action:**
  ```text
  Start_Startup_Diagnostics()
  Enable_Monitoring_Acquisition()
  ```

#### `SelfTest → Standby`
* **Guard:**
  ```text
  SelfTest_Passed == TRUE
  AND HVIL_Status == VALID
  AND Insulation_Status == VALID
  AND Contactor_Weld_Check == PASSED
  ```
* **Action:**
  ```text
  Set_OperatingMode(STANDBY)
  Enable_Estimation_Algorithms()
  Broadcast_BMS_Ready(TRUE)
  ```

---

### 3.2 High-Voltage Activation Transitions

#### `Standby → Precharge`
* **Guard:**
  ```text
  HV_Enable_Request == TRUE
  AND HVIL_Status == VALID
  AND Safety_Conditions == SATISFIED
  ```
* **Action:**
  ```text
  Activate_Precharge_Control()
  Start_Precharge_Timer()
  ```

#### `Precharge → Operating`
* **Guard:**
  ```text
  DC_Link_Voltage >= (0.95 * Pack_Voltage)
  AND Precharge_Timer < Precharge_Timeout
  AND Safety_Conditions == SATISFIED
  ```
* **Action:**
  ```text
  Close_Main_Positive_Contactor()
  Open_Precharge_Contactor()
  Stop_Precharge_Timer()
  Enable_Power_Limit_Calculation()
  ```

#### `Precharge → Standby`
* **Guard:**
  ```text
  HV_Enable_Request == FALSE
  AND Critical_Fault == FALSE
  ```
* **Action:**
  ```text
  Abort_Precharge_Sequence()
  Open_All_Contactors()
  Stop_Precharge_Timer()
  ```

---

### 3.3 Operational Mode Transitions

#### `Operating → Charging`
* **Guard:**
  ```text
  VCU_Mode_Request == CHARGE
  AND Charger_Connected == TRUE
  AND Battery_SoC < Target_Charge_SoC
  AND Safety_Conditions == SATISFIED
  ```
* **Action:**
  ```text
  Set_OperatingMode(CHARGING)
  Publish_MaxChargeCurrent()
  Enable_Cell_Balancing()
  ```

#### `Charging → Operating`
* **Guard:**
  ```text
  VCU_Mode_Request != CHARGE
  OR Battery_SoC >= Target_Charge_SoC
  OR Charge_Complete_Flag == TRUE
  ```
* **Action:**
  ```text
  Disable_Cell_Balancing()
  Set_MaxChargeCurrent(0)
  Set_OperatingMode(OPERATING)
  ```

#### `Operating → Discharging`
* **Guard:**
  ```text
  VCU_Mode_Request == DISCHARGE
  AND Battery_SoC > Min_Discharge_SoC
  AND Safety_Conditions == SATISFIED
  ```
* **Action:**
  ```text
  Set_OperatingMode(DISCHARGING)
  Publish_MaxDischargeCurrent()
  ```

#### `Discharging → Operating`
* **Guard:**
  ```text
  VCU_Mode_Request != DISCHARGE
  OR Battery_SoC <= Min_Discharge_SoC
  ```
* **Action:**
  ```text
  Set_MaxDischargeCurrent(0)
  Set_OperatingMode(OPERATING)
  ```

---

### 3.4 Controlled Shutdown Transitions

#### `Operating → Standby`
* **Guard:**
  ```text
  HV_Enable_Request == FALSE
  AND Abs(Pack_Current) <= Safe_Contactor_Open_Current
  ```
* **Action:**
  ```text
  Set_Power_Limits(0, 0)
  Open_All_Contactors()
  Verify_Contactor_State(OPEN)
  Persist_NVM_States()
  ```

#### `Charging → Standby`
* **Guard:**
  ```text
  HV_Enable_Request == FALSE
  AND Abs(Pack_Current) <= Safe_Contactor_Open_Current
  ```
* **Action:**
  ```text
  Disable_Cell_Balancing()
  Set_Power_Limits(0, 0)
  Open_All_Contactors()
  Persist_NVM_States()
  ```

#### `Discharging → Standby`
* **Guard:**
  ```text
  HV_Enable_Request == FALSE
  AND Abs(Pack_Current) <= Safe_Contactor_Open_Current
  ```
* **Action:**
  ```text
  Set_Power_Limits(0, 0)
  Open_All_Contactors()
  Persist_NVM_States()
  ```

---

### 3.5 Fault & Recovery Transitions

#### `Any State (Initialization..Discharging) → Fault`
* **Guard:**
  ```text
  Critical_Fault_Confirmed == TRUE
  OR Overvoltage_Fault == TRUE
  OR Overtemperature_Critical == TRUE
  OR HVIL_Status == OPEN (when HV active)
  OR Precharge_Timer >= Precharge_Timeout
  OR Contactor_Failure == TRUE
  OR VCU_Comm_Timeout == TRUE
  ```
* **Action:**
  ```text
  Trigger_Emergency_Contactor_Open()
  Set_Power_Limits(0, 0)
  Disable_Cell_Balancing()
  Log_DTC_To_NVM()
  Broadcast_BatteryFaultStatus(CRITICAL)
  ```

#### `Fault → Standby`
* **Guard:**
  ```text
  All_Critical_Faults == CLEARED
  AND Fault_Latched_Flag == FALSE
  AND Reset_Condition_Met == TRUE
  AND Safety_Conditions == SATISFIED
  ```
* **Action:**
  ```text
  Clear_Active_Fault_Flags()
  Verify_Contactor_State(OPEN)
  Set_OperatingMode(STANDBY)
  Broadcast_BMS_Ready(TRUE)
  ```
