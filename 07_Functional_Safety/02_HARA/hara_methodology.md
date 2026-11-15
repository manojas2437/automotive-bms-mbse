# 02 HARA — Hazard Analysis and Risk Assessment Methodology

## 1. Purpose & Scope
This document defines the methodology used to perform the **Hazard Analysis and Risk Assessment (HARA)** for the **400 V High-Voltage Battery Management System (HV-BMS)** in accordance with **ISO 26262-3 (Concept Phase)**. The objective is to identify malfunctioning behaviors at the item boundary, evaluate them within specific vehicle operational situations, classify the associated risk using Severity ($S$), Exposure ($E$), and Controllability ($C$), and establish the foundation for Automotive Safety Integrity Level (ASIL) determination and Safety Goals.

---

## 2. HARA Workflow
1. **Malfunction Identification:** Apply guidewords (e.g., *loss of function, unintended activation, late activation, incorrect output*) to the functions defined in `01_Item_Definition/item_definition.md`.
2. **Operational Situation Definition:** Combine malfunctioning behaviors with realistic driving, charging, parked, and service scenarios (considering road type, traffic density, vehicle speed, and occupant/technician presence).
3. **Hazardous Event Formulation:** Define the vehicle-level hazardous event resulting from the combination of a BMS malfunction and a specific operational situation.
4. **Risk Classification ($S, E, C$):** Assess potential harm to vehicle occupants, bystanders, or service personnel using ISO 26262-3 classification criteria.
5. **ASIL Determination:** Map the $(S, E, C)$ tuple using the ISO 26262-3 ASIL determination matrix once scenario assumptions are peer-reviewed and finalized.
6. **Safety Goal & Safe State Allocation:** Formulate top-level Safety Goals (`SAF-GOAL-*`) and safe states for every hazardous event rated ASIL A–D.

---

## 3. Classification Scales (ISO 26262-3)

### 3.1 Severity ($S$) — Potential Harm to Persons

| Class | Meaning | BMS-Specific Assessment Criteria |
| :--- | :--- | :--- |
| **S0** | No injuries | Purely equipment or battery cell degradation without thermal runaway, fire, electric shock, or traffic collision risk. |
| **S1** | Light to moderate injuries | Minor smoke/fumes with ample egress time, or low-speed traffic disturbance. |
| **S2** | Severe to life-threatening injuries (survival probable) | Sudden loss of propulsion in dense highway traffic or localized thermal venting near cabin. |
| **S3** | Life-threatening or fatal injuries (survival uncertain) | Uncontrolled battery fire/thermal runaway with toxic gas release, high-voltage (400 V DC) electric shock, or loss of propulsion during high-speed overtaking/merging. |

### 3.2 Exposure ($E$) — Probability of Operational Situation

| Class | Meaning | BMS-Specific Assessment Criteria |
| :--- | :--- | :--- |
| **E0** | Incredible | Situations that are physically implausible under normal or foreseeable vehicle use. |
| **E1** | Very low probability | Rare maintenance or service operations (e.g., HV junction box open during workshop service). |
| **E2** | Low probability | Infrequent environmental extremes (e.g., ambient temperature > 45 °C during steep mountain climb). |
| **E3** | Medium probability | Regularly occurring situations (e.g., DC fast charging, wet-weather driving, highway merging/overtaking). |
| **E4** | High probability | Situations occurring during almost every drive cycle (e.g., urban/highway cruising, normal AC charging, parked/standby). |

### 3.3 Controllability ($C$) — Ability to Avoid Harm

| Class | Meaning | BMS-Specific Assessment Criteria |
| :--- | :--- | :--- |
| **C0** | Controllable in general | Driver or technician can easily prevent harm without special reaction. |
| **C1** | Simply controllable | > 99% of drivers/users can avoid harm (e.g., gradual power derating with dashboard warning). |
| **C2** | Normally controllable | > 90% of drivers can avoid harm (e.g., sudden loss of propulsion on a straight road with shoulder access, keeping steering and braking intact). |
| **C3** | Difficult or uncontrollable | < 90% of drivers/persons can avoid harm (e.g., rapid thermal runaway inside a parked garage, unexpected 400 V bus energization during service, or sudden power loss mid-overtake). |

---

## 4. ISO 26262-3 ASIL Determination Reference Matrix
*Note: Per project workflow, ASIL values remain `TBD` in `hara_analysis.csv` until scenario-specific vehicle assumptions are reviewed and signed off.*

| Severity | Exposure | C1 | C2 | C3 |
| :--- | :--- | :--- | :--- | :--- |
| **S1** | E1–E3 | QM | QM | QM |
| **S1** | E4 | QM | QM | A |
| **S2** | E1–E2 | QM | QM | QM |
| **S2** | E3 | QM | QM | A |
| **S2** | E4 | QM | A | B |
| **S3** | E1 | QM | QM | QM |
| **S3** | E2 | QM | QM | A |
| **S3** | E3 | QM | A | B |
| **S3** | E4 | A | B | C |
| **S3** | E4 (C3) | — | — | **D** *(when S3 + E4 + C3)* |

*(Correction note: In ISO 26262-3 Table 4, S3 + E3 + C3 = **C**, and S3 + E4 + C3 = **D**.)*

---

## 5. General Vehicle-Level Assumptions
* **12 V Low-Voltage Independence:** Loss of HV traction power does not cause loss of 12 V electric power steering (EPS) or hydraulic/electro-hydraulic braking assistance.
* **Egress & Warning Time:** A thermal event provides sufficient occupant egress only if early thermal warning occurs prior to cell venting; sudden unannounced thermal runaway in an enclosed space or traffic is assessed as `S3`.
* **HV Isolation Barrier:** Direct contact with live 400 V DC conductors is prevented during normal operation by IP2X/IPXXB enclosures and HVIL, except during invasive maintenance or post-crash barrier breach.
