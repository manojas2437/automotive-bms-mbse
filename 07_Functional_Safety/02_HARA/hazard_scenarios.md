# 02 HARA — Hazardous Scenarios Definition

## 1. Purpose
This document details the vehicle-level hazardous scenarios derived from the preliminary BMS hazard list (`HAZ-001` through `HAZ-005`). Each scenario establishes the operational context, BMS malfunctioning behavior, resulting vehicle behavior, and potential harm to support objective $S$, $E$, and $C$ classification.

---

## 2. Detailed Scenario Descriptions

### Scenario 1 – Battery Overtemperature (`HAZ-002`)
* **Operating situation:** EV driving at highway speed (~120 km/h) or undergoing high-power DC fast charging in warm ambient conditions with occupants inside the vehicle.
* **Malfunction:** BMS temperature monitoring fails (e.g., stuck-at-normal NTC reading or missed threshold evaluation) and fails to detect excessive cell temperature rise or request cooling/derating.
* **Vehicle behaviour:** Battery pack continues operating at high current outside its thermal Safe Operating Area (SOA) without power derating or HV contactor isolation.
* **Potential consequence:** Cell separator breakdown leads to exothermic thermal runaway, venting of toxic/flammable gases, and vehicle fire, posing life-threatening or fatal injury risk to vehicle occupants or nearby persons.
* **Required analysis:** Evaluate Severity ($S$) based on fire/toxic gas hazard, Exposure ($E$) for highway driving or fast charging frequency, and Controllability ($C$) considering the driver cannot stop an internal electrochemical runaway once initiated.

### Scenario 2 – Unintended HV Disconnection (`HAZ-003`)
* **Operating situation:** Vehicle driving at high speed on a multi-lane highway (e.g., during merging or overtaking maneuvers in dense traffic).
* **Malfunction:** Main HV contactors open unexpectedly due to a false fault trigger, spurious contactor driver command, or Master BMS state machine error.
* **Vehicle behaviour:** Sudden, unannounced loss of traction propulsion and regenerative braking (while 12 V steering and friction brakes remain available).
* **Potential consequence:** Rapid deceleration relative to surrounding high-speed traffic increases the risk of a rear-end or side-impact collision with severe to life-threatening injuries.
* **Required analysis:** Evaluate Severity ($S$) for high-speed traffic collision impact, Exposure ($E$) for highway overtaking/cruising frequency, and Controllability ($C$) accounting for driver reaction time and availability of safe road shoulders.

### Scenario 3 – Battery Overvoltage (`HAZ-001`)
* **Operating situation:** Vehicle connected to an external AC On-Board Charger (OBC) or DC Fast Charger (e.g., parked in a residential garage or public charging station).
* **Malfunction:** Cell voltage acquisition (`CMU`) or Master BMS overvoltage detection fails (e.g., frozen voltage telemetry or failure to open contactors when a cell exceeds maximum voltage).
* **Vehicle behaviour:** Charging continues beyond the maximum permitted cell voltage limit ($> 4.25\text{ V}$ for NMC) because the BMS fails to reduce `MaxChargeCurrent` to `0 A` or isolate the pack.
* **Potential consequence:** Lithium plating, electrolyte decomposition, internal short circuit, and subsequent thermal runaway or fire in an occupied vehicle or residential building.
* **Required analysis:** Evaluate Severity ($S$) for fire/explosion hazard in a parked/occupied environment, Exposure ($E$) for routine charging operations, and Controllability ($C$) given charging often occurs unattended or with sleeping occupants.

### Scenario 4 – Unintended Contactor Closure (`HAZ-004`)
* **Operating situation:** Vehicle is in `Standby` or `Service` mode (e.g., maintenance technician inspecting HV components or disconnected HV harness when HVIL should prevent closure).
* **Malfunction:** BMS contactor driver shorts high-side/low-side or Master BMS commands main contactor closure without valid `HV_Enable_Request` and valid `HVILStatus`.
* **Vehicle behaviour:** Unexpected energization of the external 400 V DC HV bus without pre-charge or authorization.
* **Potential consequence:** Severe electric shock / electrocution or arc-flash burn injury to maintenance personnel or first responders exposed to HV terminals.
* **Required analysis:** Evaluate Severity ($S$) for 400 V DC electrocution, Exposure ($E$) for maintenance/service access frequency, and Controllability ($C$) as electrical energization is instantaneous and invisible.

### Scenario 5 – Incorrect Battery Current Limitation (`HAZ-005`)
* **Operating situation:** Vehicle charging at low ambient temperature ($< 0\,^\circ\text{C}$) or undergoing heavy regenerative braking at high State of Charge ($> 95\%$).
* **Malfunction:** `Energy_Management` computes an excessively high `MaxChargeCurrent` limit (e.g., due to corrupted `BatterySoC` or `CellTemperature` input) and transmits it to the OBC/VCU.
* **Vehicle behaviour:** Charger or inverter injects excessive charging current into cold or nearly full cells while voltages remain transiently below immediate hardware trip thresholds.
* **Potential consequence:** Accelerated lithium plating and dendritic growth causing latent internal cell short circuits and delayed thermal runaway during subsequent driving or parking.
* **Required analysis:** Evaluate Severity ($S$) for latent thermal event, Exposure ($E$) for cold-weather charging or high-SoC regenerative braking, and Controllability ($C$) since internal cell damage occurs without immediate driver perception.
