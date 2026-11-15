# 01 System Definition — Automotive BMS System Overview

## 1. Purpose & Scope
This document defines the top-level **System Overview** for the **400 V Automotive Battery Management System (BMS)**. It establishes the system purpose, primary actors, external system interfaces, internal decomposition (`Master BMS` and `Slave BMS`), and key operational capabilities as the entry point for downstream requirements engineering, logical/behavioral architecture, and ISO 26262 functional safety activities.

---

## 2. System Purpose & Core Objectives
The Automotive BMS acts as the central intelligence and protection layer for a **96-series-cell (96S, ~400 V nominal) Lithium-Ion High-Voltage (HV) Battery Pack** in a Battery Electric Vehicle (BEV). Its primary objectives are:
* **Safety & Protection:** Maintain all cells within their electrical and thermal Safe Operating Area (SOA) and enforce galvanic HV isolation via main contactors during faults or shutdown.
* **State Estimation:** Compute accurate real-time estimates of State of Charge (SoC), State of Health (SoH), and State of Power (SoP).
* **Energy & Thermal Optimization:** Coordinate dynamic charging/discharging current limits with vehicle controllers, balance cell voltages, and request active cooling or heating.
* **Diagnostics & Serviceability:** Continuously monitor sensor plausibility and hardware health, log Diagnostic Trouble Codes (DTCs), and expose diagnostic data to service technicians.

---

## 3. System Context & Boundaries
As illustrated in `system_context.puml`, the BMS interacts with human actors, vehicle-level controllers, and the physical High-Voltage Battery Pack:

### 3.1 Human Actors
* **Driver:** Interacts indirectly with the BMS via the **Vehicle Control Unit (VCU)** (e.g., ignition wake-up, driving propulsion requests, charging initiation, and dashboard state/warning indicators).
* **Technician:** Interacts directly with the **Master BMS** via an external diagnostic interface (UDS / ISO 14229) during manufacturing end-of-line testing, maintenance, and fault troubleshooting.

### 3.2 Interacting External Systems
* **Vehicle Control Unit (VCU):** Coordinates vehicle operating modes (`Standby`, `Driving`, `Charging`, `Shutdown`), receives `SoC`, `SoH`, `SoP`, and fault status over `CAN / CAN-FD`, and issues HV enable/disable requests.
* **On-Board Charger (OBC):** Receives dynamic maximum charging current and voltage limits from the Master BMS to safely charge the battery pack from AC grid power.
* **Thermal Management Controller (TMS):** Receives battery cooling and heating requests based on cell temperature measurements to maintain optimal thermal operating conditions.
* **High-Voltage Battery Pack:** Comprises the **Battery Cells** (96S energy storage), **Sensors** (pack current sensor and module temperature sensors), and **Contactors** (main positive/negative contactors and pre-charge circuit).

### 3.3 BMS Internal Decomposition
* **Master BMS (`MBMS`):** Central controller executing pack-level state machines, SoC/SoH/SoP estimation, power-limit arbitration, contactor control, fault diagnostics, and external CAN communication.
* **Slave BMS (`SBMS`):** Distributed Cell Monitoring Units (CMUs / AFEs) mounted on battery modules to measure individual cell voltages and local temperatures, perform cell balancing, and forward telemetry to the Master BMS.

---

## 4. High-Level System Capabilities

| Capability ID | Capability Name | Description | Primary Actors / Interfaces |
| :--- | :--- | :--- | :--- |
| **CAP-01** | **Battery State Monitoring** | Continuously acquire individual cell voltages (via `SBMS`), module temperatures, and pack current (via `Sensors`). | `SBMS`, `Sensors`, `MBMS` |
| **CAP-02** | **State Estimation (SoC / SoH / SoP)** | Calculate remaining usable energy, long-term battery health, and dynamic power capability. | `MBMS`, `VCU` |
| **CAP-03** | **HV Bus Control & Pre-Charge** | Execute controlled DC-link pre-charge, close/open main HV contactors, and verify galvanic isolation. | `MBMS`, `Contactors`, `VCU` |
| **CAP-04** | **Charging & Balancing Control** | Enforce dynamic charging limits with the `OBC` and equalize cell voltages across the 96S string. | `MBMS`, `SBMS`, `OBC`, `VCU` |
| **CAP-05** | **Discharging & Power Limiting** | Enforce dynamic discharge current limits during vehicle propulsion based on SoC, voltage, and temperature. | `MBMS`, `VCU`, `Driver` |
| **CAP-06** | **Thermal Management Coordination** | Request active cooling or heating from the `TMS` when cell temperatures deviate from optimal bands. | `MBMS`, `TMS` |
| **CAP-07** | **Fault Detection & Safe-State Reaction** | Detect overvoltage, overtemperature, overcurrent, contactor faults, and communication timeouts, transitioning the pack to a safe isolated state. | `MBMS`, `Contactors`, `VCU`, `OBC` |
| **CAP-08** | **Diagnostic & Service Access** | Store DTCs and freeze-frame data in non-volatile memory and serve diagnostic read/clear/routine requests. | `MBMS`, `Technician` |

---

## 5. Related Repository Artifacts
* **Context Diagram:** `01_System_Definition/system_context.puml`
* **Use Case Diagram:** `01_System_Definition/use_case.puml`
* **Requirements Baseline:** `02_Requirements/stakeholder_requirements.md`, `02_Requirements/system_requirements.csv`
* **Logical & Behavioural Architecture:** `04_Logical_Architecture/`, `05_Behavioural_Architecture/`
* **Functional Safety Lifecycle (ISO 26262):** `07_Functional_Safety/`
