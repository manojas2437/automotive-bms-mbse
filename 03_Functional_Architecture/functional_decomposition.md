# BMS Functional Architecture 

## 1. Purpose 
The Battery Management System manages the safe and efficient operation of the high-volatge battery pack.

## 2. Main functions 

| Function ID | Function | Input |Output |
|---|---|---|---|
| BMS-F-001| Battery Monitoring | Sensor Signals | Battery Measures |
| BMS-F-002 | State Estimation | Voltage, current, temperature | SoC, SoH, SoP |
| BMS-F-003 | Energy Management | SoC, SoP, temperature | Charge/discharge limits |
| BMS-F-004 | Thermal Management | Cell temperature | Cooling/heating request |
| BMS-F-005 | Cell Balancing | Cell voltages | Balancing commands |
| BMS-F-006 | HV Management | Vehicle requests, safety status | Contactor commands |
| BMS-F-007 | Fault Management | Diagnostic signals | Fault status and reactions |
| BMS-F-008 | Communication | Internal data | ECU messages |

## 3. Architecture Principles

- Separation of functions.
- Defined input and output interfaces.
- Functional independence where required.
- Requirements traceability.
- Safety-oriented design.