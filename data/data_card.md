# Annex D: Factory Energy Dataset Data Card

## Name and Version
- **Dataset Name**: Synthetic Factory Energy Decomposition Dataset
- **Version**: 1.0.0
- **Generated Date**: 2026-10-11
- **Domain**: Manufacturing Plant Power Sub-metering, Production, Tariff, and Weather

---

## How It Was Made
- **Generator Script**: `data/generator.py`
- **Random Seed**: `42` (fully reproducible numpy/python seed)
- **Methodology**:
  - Physics-based energy simulation combined with real-world industrial asset profiles.
  - Sub-meter baseline dynamics: continuous thermal baseload for furnace, cyclical pneumatic compressor baseload, ambient-temperature-coupled HVAC chiller model, and fixed schedule factory lighting.
  - Production schedule: 3 shifts on weekdays, variable weekend shifts, and public holidays.
  - Realistic stochastic noise added ($\sigma \approx 1-3\%$) to emulate sensor precision.

---

## What It Contains
The dataset spans two full calendar quarters: **2026-Q2** (2026-04-01 to 2026-06-30) and **2026-Q3** (2026-07-01 to 2026-09-30), totaling 183 days.

| Table | Format | Row Count | Primary Key / Index | Description |
| :--- | :--- | :--- | :--- | :--- |
| `meter_15min.csv` | CSV | 140,544 | `(meter_id, ts)` | 15-min interval energy (kWh) for 1 main meter and 7 sub-meters. |
| `tariff.csv` | CSV | 6 | `(valid_from, period)` | Electricity pricing by time-of-day (peak, off_peak, flat) with mid-quarter tariff jump. |
| `production.csv` | CSV | 549 | `(date, product)` | Daily output units for Product families A, B, and C, shift patterns, and holiday flags. |
| `weather.csv` | CSV | 183 | `date` | Daily ambient average temperature (°C), cooling degree-days (CDD), and heating degree-days (HDD). |
| `late_drop/tariff_late.csv` | CSV | 6 | `(valid_from, period)` | Late data drop: revised peak tariff calibration. |
| `late_drop/meter_15min_late.csv`| CSV | 140,544 | `(meter_id, ts)` | Late data drop: -3% sensor recalibration fix on the furnace sub-meter. |

### Sub-Meters Included (7 sub-meters + 1 main meter)
1. `main`: Incomer main plant power feed
2. `compressors`: Central compressed air station (Line 1-3 pneumatic feed)
3. `hvac`: Plant chillers, cooling towers, and ventilation air handling units
4. `furnace`: Electric melting and heat-treatment furnace
5. `lighting`: High-bay manufacturing and warehouse LED lighting
6. `line_1`: High-speed assembly line (primary Product A)
7. `line_2`: CNC machining and milling cell (primary Product B)
8. `line_3`: Finishing, powder coating, and heavy pneumatic fabrication (primary Product C)

---

## Traps and Edge Cases Added on Purpose
The dataset intentionally incorporates all Section 4.4 edge cases to test system resilience:

1. **Sub-Meter Unmetered Discrepancy**:
   - The sub-meters sum to ~96.34% of the main meter (an unmetered residual loss of 3.66%), reflecting real-world transformer iron losses and unmonitored auxiliary pump circuits.
2. **Compressor Air Leak (Hidden Controllable Waste)**:
   - On **2026-07-15**, a severe pneumatic airline rupture develops on Line 3. Compressor night-time / non-operational power rises from 21 kW (12% of day load) to 67 kW (38% of day load), wasting energy 24/7 even during zero-production intervals.
3. **Mid-Quarter Tariff Rate Surge**:
   - On **2026-08-15**, the utility provider implements a steep tariff hike (peak increases from $0.130 to $0.175/kWh; off-peak from $0.080 to $0.105/kWh), driving ~8.1 percentage points of the total 15% bill rise.
4. **Legitimate Product Mix Shift (Non-Waste)**:
   - In Q3, customer demand causes a shift toward heavy casted Product C (24.0 kWh/unit) at the expense of lightweight Product A (5.0 kWh/unit). Specific energy per unit increases without any equipment fault, driving ~3.4 percentage points of the increase.
5. **Summer Heatwave (Weather Effect)**:
   - Mid-August experiences extreme temperatures up to 38.5°C, tripling Cooling Degree Days (CDD) and increasing HVAC chiller load, accounting for ~0.9 percentage points of bill rise.
6. **Public Holiday Shift Calendar Trap**:
   - On **2026-08-15 (Independence Day)**, the shift calendar mistakenly records `shift_pattern = '2_shifts'`, but `is_holiday = True` and actual production units are 0. The system must recognize this as an idle day rather than machine downtime.
7. **Meter Reset Anomaly**:
   - A momentary sensor reset glitch on **2026-05-10 03:00** records 0.5 kWh before immediate self-recovery.

---

## Validation Checks Run
Validation executed via `python data/validate_data.py`:
- **Sub-meter balance**: 3.66% unmetered loss $\le$ 7.0% tolerance limit $\rightarrow$ **PASS**
- **Non-negative energy & monotonic intervals**: Zero negative values, reset artifact identified $\rightarrow$ **PASS**
- **Timestamp regularity & time zone**: 100% regular 15-minute intervals in UTC $\rightarrow$ **PASS**
- **Tariff continuity**: Non-overlapping schedules covering entire 183 days $\rightarrow$ **PASS**
- **Production alignment**: Exactly 183 dates aligned with meter timeline $\rightarrow$ **PASS**

---

## Known Limitations
- Data covers two quarters (April 2026 through September 2026); seasonal winter heating effects are minimal as heating degree-days (HDD) are near zero.
- Voltage sag / power factor variations are not modeled; energy is recorded in active kilowatt-hours (kWh).

---

## Privacy Declaration
**Confirmed**: No real company, proprietary, or personally identifiable data (PII) is included in this dataset. All values were synthetically generated using mathematical industrial process models.
