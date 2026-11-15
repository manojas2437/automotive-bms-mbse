# 02 Requirements — Stakeholder Requirements & Safety Goals

## 1. Purpose & Scope
This document defines the top-level **Stakeholder Requirements (`STK-REQ-*`)** and **Functional Safety Goals (`SAF-GOAL-*`)** for the Battery Management System (BMS). These items establish *what* external stakeholders need from the battery system and serve as the parent baseline for the system requirements in `system_requirements.csv`.

---

## 2. Key Stakeholders
* **Vehicle OEM / Powertrain Integration:** Requires reliable energy delivery, accurate range/state reporting, and standardized vehicle bus communication.
* **Functional Safety & Homologation:** Requires compliance with ISO 26262, UN ECE R100, and protection against electrical and thermal hazards.
* **End User / Driver:** Expects safe vehicle operation, predictable driving range, fast charging, and long battery lifespan.
* **Service & Diagnostics Engineering:** Requires clear fault reporting, Diagnostic Trouble Codes (DTCs), and service-tool access (UDS) for maintenance.

---

## 3. Stakeholder Requirements (`STK-REQ-*`)

| ID | Stakeholder | Requirement Statement | Rationale | Child System Requirements |
| :--- | :--- | :--- | :--- | :--- |
| **STK-REQ-001** | Vehicle OEM / Safety | The battery system shall continuously observe internal electrical and thermal operating conditions across all cells. | Ensures visibility into cell-level health and safe operating boundaries. | `BMS-REQ-001`, `BMS-REQ-002`, `BMS-REQ-009` |
| **STK-REQ-002** | End User / Vehicle OEM | The system shall provide accurate real-time estimates of remaining usable energy and long-term battery degradation. | Enables reliable vehicle range prediction and warranty/lifespan tracking. | `BMS-REQ-003`, `BMS-REQ-004` |
| **STK-REQ-003** | Vehicle OEM / End User | The system shall maximize charging speed, discharge power availability, and pack usable capacity without accelerating cell degradation. | Optimizes vehicle performance, fast-charging times, and battery longevity. | `BMS-REQ-007`, `BMS-REQ-012`, `BMS-REQ-013` |
| **STK-REQ-004** | Vehicle OEM (VCU/OBC) | The BMS shall exchange real-time operational status, power limits, and fault states with host vehicle controllers over standard automotive networks. | Enables coordinated vehicle propulsion, thermal management, and charging control. | `BMS-REQ-008` |
| **STK-REQ-005** | Vehicle OEM | The battery system shall support deterministic, safe power-up and power-down sequences coordinated with vehicle ignition states. | Prevents electrical arcing, inrush damage, and unintended high-voltage exposure. | `BMS-REQ-010`, `BMS-REQ-019` |
| **STK-REQ-006** | Service & Manufacturing | The BMS shall record, store, and report standardized diagnostic fault information for assembly testing and field maintenance. | Reduces vehicle downtime and enables rapid root-cause troubleshooting. | `BMS-REQ-016` |
| **STK-REQ-007** | Platform Engineering | The BMS architecture shall support reuse across multiple battery pack capacities and cell chemistries with minimal software rework. | Reduces development cost and time-to-market across vehicle variants. | *(Addressed in `AD-005`)* |

---

## 4. Top-Level Functional Safety Goals (`SAF-GOAL-*`)
Derived from the Hazard Analysis and Risk Assessment (HARA) per ISO 26262, these safety goals define the top-level hazard mitigations that flow down into safety-relevant system requirements:

| Goal ID | Safety Goal Description | Target ASIL | Safe State | Child System Requirements |
| :--- | :--- | :--- | :--- | :--- |
| **SAF-GOAL-001** | **Prevent High-Voltage Electric Shock:** Prevent unintended energization of the vehicle HV bus and ensure reliable galvanic isolation on demand or upon interlock/isolation breach. | **ASIL D** | Main HV contactors open (galvanic isolation). | `BMS-REQ-005`, `BMS-REQ-011`, `BMS-REQ-018` |
| **SAF-GOAL-002** | **Prevent Cell Overcharge / Over-Discharge Hazard:** Prevent cell voltages from exceeding safe upper or lower limits that could cause venting, electrolyte breakdown, or internal short circuits. | **ASIL C / D** | Charging/discharging halted; main contactors open. | `BMS-REQ-006`, `BMS-REQ-014`, `BMS-REQ-020` |
| **SAF-GOAL-003** | **Prevent Thermal Runaway Initiation:** Prevent battery cell temperatures from exceeding critical safety limits during operation or charging. | **ASIL C** | Power derated to zero; main contactors open; thermal warning issued. | `BMS-REQ-015` |
| **SAF-GOAL-004** | **Maintain Safe Control on Host Communication Loss:** Ensure the battery pack transitions to a predictable, isolated state if communication with the host vehicle controller is lost. | **ASIL B** | Power limits set to 0 A; contactors opened after safe current ramp-down. | `BMS-REQ-017` |

---

## 5. Non-Functional & Regulatory Constraints
* **Compliance:** Must comply with **ISO 26262** (Functional Safety), **UN ECE R100** (Electric Powertrain Safety), and **ISO 14229** (UDS Diagnostics).
* **Environmental & EMC:** Must operate reliably across automotive temperature grades (-40 °C to +85 °C) and electromagnetic interference limits (CISPR 25).
* **Lifecycle & Service:** Non-volatile state and fault records must remain intact across power cycles for a minimum 15-year / 300,000 km service life.
