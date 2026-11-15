
# Automotive BMS - Basic Engineering Calculations

# Illustrative battery configuration
series_cells = 96
nominal_cell_voltage = 3.7
capacity_ah = 100

# Battery pack calculations
pack_voltage = series_cells * nominal_cell_voltage
energy_kwh = pack_voltage * capacity_ah / 1000

# Example operating values
pack_current = 100

pack_power_kw = pack_voltage * pack_current / 1000

print("Battery Management System")
print("-------------------------")
print(f"Series Cells: {series_cells}")
print(f"Nominal Pack Voltage: {pack_voltage} V")
print(f"Battery Capacity: {capacity_ah} Ah")
print(f"Nominal Energy: {energy_kwh} kWh")
print(f"Pack Power: {pack_power_kw} kW")
