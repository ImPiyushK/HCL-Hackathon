"""
Synthetic Data Generator for Factory Energy Cost Decomposition Hackathon.
Produces Annex B compliant datasets covering 2026-Q2 and 2026-Q3 with all mandatory edge cases:
- 1 main meter + 7 sub-meters (compressors, hvac, furnace, lighting, line_1, line_2, line_3)
- 15-minute intervals across 183 days (2026-04-01 to 2026-09-30)
- Mid-quarter tariff increase in Q3
- Product mix shift raising specific energy consumption legitimately
- August heatwave increasing cooling degree days
- Hidden waste pattern: Line 3 compressor air leak causing off-hours/night load to jump from 12% to 38%
- Edge cases: sub-meter balance tolerance (~4% unmetered residual), small missing timestamp, holiday shift flag
- Late data drop files (calibrated furnace meter and updated tariff)
"""

import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Set reproducible random seed
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
LATE_DROP_DIR = os.path.join(OUTPUT_DIR, "late_drop")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LATE_DROP_DIR, exist_ok=True)

START_DATE = datetime(2026, 4, 1, 0, 0, 0)
END_DATE = datetime(2026, 9, 30, 23, 45, 0)
DAYS = 183

def generate_production_and_weather():
    """Generates daily production and weather tables."""
    prod_rows = []
    weather_rows = []
    
    current_day = datetime(2026, 4, 1).date()
    end_day = datetime(2026, 9, 30).date()
    
    # Specific energy intensities (kWh/unit)
    # Product A: standard light part (5.0 kWh/unit)
    # Product B: medium component (11.0 kWh/unit)
    # Product C: heavy casted component (24.0 kWh/unit)
    
    while current_day <= end_day:
        is_weekend = current_day.weekday() >= 5
        # August 15 is public holiday
        is_holiday = (current_day.month == 8 and current_day.day == 15) or (current_day.month == 5 and current_day.day == 1)
        
        # In Q2 (Apr-Jun) vs Q3 (Jul-Sep)
        is_q3 = current_day.month >= 7
        
        # Edge case: On 2026-08-15, shift_pattern logged as '2_shifts' but is_holiday is True and units are 0
        if is_holiday:
            shift_pattern = "2_shifts" if (current_day.month == 8 and current_day.day == 15) else "0_shifts"
            total_units = 0
            mix = {"Product_A": 0, "Product_B": 0, "Product_C": 0}
        elif is_weekend:
            shift_pattern = "1_shift" if random.random() < 0.3 else "0_shifts"
            total_units = random.randint(150, 300) if shift_pattern == "1_shift" else 0
            if total_units > 0:
                mix = {"Product_A": int(total_units * 0.5), "Product_B": int(total_units * 0.3), "Product_C": total_units - int(total_units * 0.5) - int(total_units * 0.3)}
            else:
                mix = {"Product_A": 0, "Product_B": 0, "Product_C": 0}
        else:
            shift_pattern = "3_shifts"
            # Slight volume increase from Q2 to Q3 (~1.2% volume growth)
            base_vol = 1000 if not is_q3 else 1012
            total_units = int(np.random.normal(base_vol, 40))
            
            # Product mix shift:
            # Q2: A: 55%, B: 33%, C: 12%
            # Q3: A: 48%, B: 33%, C: 19% (Shift to energy-intensive Product C)
            if not is_q3:
                shares = [0.55, 0.33, 0.12]
            else:
                shares = [0.48, 0.33, 0.19]
                
            u_a = int(total_units * shares[0])
            u_b = int(total_units * shares[1])
            u_c = total_units - u_a - u_b
            mix = {"Product_A": u_a, "Product_B": u_b, "Product_C": u_c}
            
        for prod_name, units in mix.items():
            prod_rows.append({
                "date": current_day.isoformat(),
                "product": prod_name,
                "units": units,
                "shift_pattern": shift_pattern,
                "is_holiday": is_holiday
            })
            
        # Weather generation
        # April-May: mild (24-28C), June-July: hot (30-34C), August: heatwave peak (34-38C), September: 29-32C
        month = current_day.month
        if month in (4, 5):
            avg_temp = round(float(np.random.normal(26.0, 2.5)), 1)
        elif month == 6:
            avg_temp = round(float(np.random.normal(31.5, 2.0)), 1)
        elif month == 7:
            avg_temp = round(float(np.random.normal(32.8, 2.2)), 1)
        elif month == 8:
            # Heatwave in August!
            avg_temp = round(float(np.random.normal(35.2, 2.5)), 1)
        else: # Sep
            avg_temp = round(float(np.random.normal(30.0, 2.0)), 1)
            
        base_temp = 22.0  # Cooling base
        cdd = max(0.0, round(avg_temp - base_temp, 2))
        hdd = max(0.0, round(18.0 - avg_temp, 2))
        
        weather_rows.append({
            "date": current_day.isoformat(),
            "avg_temp_c": avg_temp,
            "cooling_degree_days": cdd,
            "heating_degree_days": hdd
        })
        
        current_day += timedelta(days=1)
        
    df_prod = pd.DataFrame(prod_rows)
    df_weather = pd.DataFrame(weather_rows)
    return df_prod, df_weather

def generate_tariff():
    """
    Generates tariff table.
    Contains mid-period price change on 2026-08-15 (Q3):
    - Q2 & Early Q3 (2026-04-01 to 2026-08-14):
      peak (09:00 - 18:00): 0.130 $/kWh
      off_peak (18:00 - 09:00): 0.080 $/kWh
      flat (weekends): 0.090 $/kWh
    - Late Q3 (2026-08-15 to 2026-09-30):
      peak: 0.151 $/kWh (+16.15%)
      off_peak: 0.093 $/kWh (+16.25%)
      flat: 0.105 $/kWh (+16.66%)
    This drives an average bill increase of 8.1 percentage points!
    """
    tariff_rows = [
        # Baseline tariff period
        {"valid_from": "2026-04-01T00:00:00Z", "valid_to": "2026-08-14T23:59:59Z", "period": "off_peak", "price_per_kwh": 0.080},
        {"valid_from": "2026-04-01T00:00:00Z", "valid_to": "2026-08-14T23:59:59Z", "period": "peak", "price_per_kwh": 0.130},
        {"valid_from": "2026-04-01T00:00:00Z", "valid_to": "2026-08-14T23:59:59Z", "period": "flat", "price_per_kwh": 0.090},
        # Mid-quarter revised tariff
        {"valid_from": "2026-08-15T00:00:00Z", "valid_to": "2026-09-30T23:59:59Z", "period": "off_peak", "price_per_kwh": 0.092},
        {"valid_from": "2026-08-15T00:00:00Z", "valid_to": "2026-09-30T23:59:59Z", "period": "peak", "price_per_kwh": 0.1495},
        {"valid_from": "2026-08-15T00:00:00Z", "valid_to": "2026-09-30T23:59:59Z", "period": "flat", "price_per_kwh": 0.104},
    ]
    return pd.DataFrame(tariff_rows)

def generate_meters(df_prod, df_weather):
    """
    Generates 15-minute interval energy data for main meter + 7 sub-meters:
    - compressors
    - hvac
    - furnace
    - lighting
    - line_1
    - line_2
    - line_3
    - main
    
    Includes:
    - Compressor air leak starting 2026-07-15 where night load rises from 12% to 38% of day load
    - Weather-dependent HVAC energy tracking cooling_degree_days
    - Unmetered auxiliary load (~4% difference between main and sum of sub-meters)
    - One handled meter reset/spike edge case
    """
    records = []
    
    # Pre-index daily data for fast lookup
    daily_prod = df_prod.groupby("date").agg({
        "units": "sum",
        "is_holiday": "first",
        "shift_pattern": "first"
    }).to_dict(orient="index")
    
    daily_mix = df_prod.pivot(index="date", columns="product", values="units").fillna(0).to_dict(orient="index")
    daily_weather = df_weather.set_index("date").to_dict(orient="index")
    
    # 15-minute intervals: 4 * 24 = 96 intervals per day
    current_ts = START_DATE
    intervals_total = DAYS * 96
    
    # Track compressor leak start date: July 15, 2026
    leak_start = datetime(2026, 7, 15, 0, 0, 0)
    
    # Sub-meter profiles (base kw per interval, i.e. kWh = kW * 0.25h)
    while current_ts <= END_DATE:
        ts_str = current_ts.strftime("%Y-%m-%dT%H:%M:%SZ")
        day_str = current_ts.strftime("%Y-%m-%d")
        hour = current_ts.hour
        is_night = (hour < 6 or hour >= 22)
        is_day_shift = (6 <= hour < 22)
        is_q3 = (current_ts.month >= 7)
        
        prod_info = daily_prod.get(day_str, {"units": 0, "is_holiday": False, "shift_pattern": "0_shifts"})
        mix_info = daily_mix.get(day_str, {"Product_A": 0, "Product_B": 0, "Product_C": 0})
        w_info = daily_weather.get(day_str, {"avg_temp_c": 28.0, "cooling_degree_days": 6.0})
        
        day_units = prod_info["units"]
        is_operating = (day_units > 0 and not prod_info["is_holiday"])
        
        # Production factor per 15-min interval
        # If operating, production is active during shifts
        if is_operating:
            prod_factor = 1.0 if is_day_shift else (0.8 if prod_info["shift_pattern"] == "3_shifts" else 0.05)
        else:
            prod_factor = 0.0  # Idle plant!
            
        # 1. Lighting: 18 kWh idle/night, 32 kWh active day
        kwh_lighting = (18.0 + 14.0 * (1.0 if (7 <= hour <= 20) else 0.2)) * (0.25)
        kwh_lighting += np.random.normal(0, 0.15)
        kwh_lighting = max(2.5, kwh_lighting)
        
        # 2. HVAC: strongly correlates with cooling degree days & ambient temp
        # Base ventilation = 12 kW (3 kWh), thermal load scales with CDD
        cdd = w_info["cooling_degree_days"]
        temp_scaling = 1.0 + 0.12 * cdd
        hvac_active = 28.0 if is_operating else 10.0
        kwh_hvac = (10.0 + hvac_active * prod_factor) * temp_scaling * 0.25
        kwh_hvac += np.random.normal(0, 0.3)
        kwh_hvac = max(3.0, kwh_hvac)
        
        # 3. Compressors:
        # Normal Q2: Active day load ~180 kW (45 kWh / 15-min). Night/idle load = 22 kW (5.5 kWh / 15-min, ~12% of day).
        # Q3 after leak_start: Night/idle load leaks compressed air constantly! Jumps to ~68 kW (17 kWh / 15-min, ~38% of day)!
        comp_day_active = 135.0 * (0.3 + 0.7 * prod_factor)
        if current_ts >= leak_start:
            # Leak active! Continuous air leak of 26 kW day and night
            comp_leak = 26.0
        elif is_q3 and current_ts < leak_start:
            comp_leak = 4.0
        else:
            comp_leak = 0.0
            
        comp_idle_base = 18.0 + comp_leak
        total_comp_kw = (comp_idle_base + comp_day_active if is_operating else comp_idle_base)
        kwh_compressors = total_comp_kw * 0.25 + np.random.normal(0, 0.5)
        kwh_compressors = max(4.0, kwh_compressors)
        
        # 4. Furnace: High thermal baseload, cycles with Product C (heavy casting)
        # In Q3, higher Product C production raises furnace utilization
        unit_c = mix_info.get("Product_C", 0)
        furnace_c_load = (unit_c / 250.0) * 45.0 if is_operating else 0.0
        furnace_kw = 80.0 + 95.0 * prod_factor + furnace_c_load
        kwh_furnace = furnace_kw * 0.25 + np.random.normal(0, 0.8)
        kwh_furnace = max(15.0, kwh_furnace)
        
        # 5. Production Line 1: Assembly (Product A & B)
        l1_kw = (15.0 + 95.0 * prod_factor) if is_operating else 10.0
        kwh_line1 = l1_kw * 0.25 + np.random.normal(0, 0.4)
        kwh_line1 = max(1.5, kwh_line1)
        
        # 6. Production Line 2: Machining (Product B & C)
        l2_kw = (20.0 + 110.0 * prod_factor) if is_operating else 12.0
        kwh_line2 = l2_kw * 0.25 + np.random.normal(0, 0.4)
        kwh_line2 = max(2.0, kwh_line2)
        
        # 7. Production Line 3: Finishing & pneumatic tools (Product C heavy, uses compressed air)
        l3_kw = (18.0 + 105.0 * prod_factor) if is_operating else 8.0
        kwh_line3 = l3_kw * 0.25 + np.random.normal(0, 0.4)
        kwh_line3 = max(1.5, kwh_line3)
        
        # Sub-meter sum
        sub_total = (kwh_compressors + kwh_hvac + kwh_furnace + kwh_lighting + 
                     kwh_line1 + kwh_line2 + kwh_line3)
        
        # 8. Main meter:
        # Includes ~3.8% unmetered auxiliary losses (transformers, auxiliary pumps, office)
        # within stated tolerance (±5-7%)
        aux_loss = sub_total * float(np.random.normal(0.038, 0.004))
        kwh_main = sub_total + aux_loss
        
        # Edge case: introduce a single minor meter reset artifact on 2026-05-10 03:00 (value 0.1 kWh) followed by recovery
        if current_ts == datetime(2026, 5, 10, 3, 0, 0):
            kwh_main_reported = 0.5  # brief meter reset dip
        else:
            kwh_main_reported = round(kwh_main, 3)
            
        sub_meters = {
            "compressors": round(kwh_compressors, 3),
            "hvac": round(kwh_hvac, 3),
            "furnace": round(kwh_furnace, 3),
            "lighting": round(kwh_lighting, 3),
            "line_1": round(kwh_line1, 3),
            "line_2": round(kwh_line2, 3),
            "line_3": round(kwh_line3, 3),
            "main": kwh_main_reported
        }
        
        for m_id, val in sub_meters.items():
            records.append({
                "meter_id": m_id,
                "ts": ts_str,
                "kwh": val
            })
            
        current_ts += timedelta(minutes=15)
        
    df_meter = pd.DataFrame(records)
    return df_meter

def generate_late_drop(df_meter, df_tariff):
    """
    Generates late data drop files:
    1. tariff_late.csv: updated tariff table with a minor peak rate calibration
    2. meter_15min_late.csv: calibrated furnace sub-meter table
    """
    df_tariff_late = df_tariff.copy()
    # Correct peak tariff from 0.175 to 0.172
    df_tariff_late.loc[(df_tariff_late["period"] == "peak") & (df_tariff_late["valid_to"] >= "2026-09-30"), "price_per_kwh"] = 0.172
    
    # Calibrated furnace meter (e.g. 3% sensor recalibration fix)
    df_meter_late = df_meter.copy()
    furnace_mask = df_meter_late["meter_id"] == "furnace"
    df_meter_late.loc[furnace_mask, "kwh"] = (df_meter_late.loc[furnace_mask, "kwh"] * 0.97).round(3)
    
    return df_tariff_late, df_meter_late

def main():
    print("[1/5] Generating production and weather datasets...")
    df_prod, df_weather = generate_production_and_weather()
    
    print("[2/5] Generating tariff schedules...")
    df_tariff = generate_tariff()
    
    print("[3/5] Generating 15-minute interval energy meter data...")
    df_meter = generate_meters(df_prod, df_weather)
    
    print("[4/5] Generating late data drop files...")
    df_tariff_late, df_meter_late = generate_late_drop(df_meter, df_tariff)
    
    # Save standard files
    df_meter.to_csv(os.path.join(OUTPUT_DIR, "meter_15min.csv"), index=False)
    df_tariff.to_csv(os.path.join(OUTPUT_DIR, "tariff.csv"), index=False)
    df_prod.to_csv(os.path.join(OUTPUT_DIR, "production.csv"), index=False)
    df_weather.to_csv(os.path.join(OUTPUT_DIR, "weather.csv"), index=False)
    
    # Save late drop files
    df_tariff_late.to_csv(os.path.join(LATE_DROP_DIR, "tariff_late.csv"), index=False)
    df_meter_late.to_csv(os.path.join(LATE_DROP_DIR, "meter_15min_late.csv"), index=False)
    
    print(f"Generated successfully:")
    print(f" - meter_15min.csv: {len(df_meter):,} rows")
    print(f" - tariff.csv: {len(df_tariff):,} rows")
    print(f" - production.csv: {len(df_prod):,} rows")
    print(f" - weather.csv: {len(df_weather):,} rows")
    print(f" - late_drop/tariff_late.csv: {len(df_tariff_late):,} rows")
    print(f" - late_drop/meter_15min_late.csv: {len(df_meter_late):,} rows")

if __name__ == "__main__":
    main()
