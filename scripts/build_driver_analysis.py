"""
Driver Analysis Feature Engineering

Bu script driver_features_test tablosunu telemetri verileri ile
zenginleştirerek sürücü bazında yeni analiz öznitelikleri oluşturur.

İlk aşamada:

- Ortalama araç hızı (AVG_VEHICLE_SPEED)

hesaplanacaktır.

Author: Zübeyde Sıla Akın
"""

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from db import client
import pandas as pd

EXCEL_DIR = BASE_DIR / "outputs" / "excel"
EXCEL_DIR.mkdir(parents=True, exist_ok=True) 

SPEED_LIMIT = 70

# ======================================================
# Driver Features
# ======================================================

driver_features = client.query_df("""

SELECT *
FROM telemetri_data_warehouse_test.driver_features_test

""")

print(f"Driver Features: {len(driver_features)} kayıt") 


# ======================================================
# Telemetri
# ======================================================

telemetry = client.query_df("""

SELECT
    DRIVER_NAME,
    TS,
    VEHICLE_SPEED
FROM telemetri_data_warehouse_test.telemetri_fact_akia_test
WHERE DRIVER_NAME IS NOT NULL

""")

telemetry = telemetry.sort_values(
    ["DRIVER_NAME", "TS"]
).reset_index(drop=True)

print(f"Telemetri: {len(telemetry)} kayıt") 



# ======================================================
# Ortalama Hız
# ======================================================

avg_speed = (
    telemetry
    .groupby("DRIVER_NAME")["VEHICLE_SPEED"]
    .mean()
    .round(2)
    .rename("AVG_VEHICLE_SPEED")
    .reset_index()
)

print("\nOrtalama Hızlar")
print(avg_speed.head())
print(f"\nToplam sürücü: {len(avg_speed)}")




# ======================================================
# Maksimum Hız
# ======================================================

max_speed = (
    telemetry
    .groupby("DRIVER_NAME")["VEHICLE_SPEED"]
    .max()
    .round(2)
    .rename("MAX_VEHICLE_SPEED")
    .reset_index()
)

print("\nMaksimum Hızlar")
print(max_speed.head())




# ======================================================
# Hız Standart Sapması
# ======================================================

std_speed = (
    telemetry
    .groupby("DRIVER_NAME")["VEHICLE_SPEED"]
    .std()
    .fillna(0)
    .round(2)
    .rename("STD_VEHICLE_SPEED")
    .reset_index()
)

print("\nHız Standart Sapmaları")
print(std_speed.head())


# ======================================================
# Çalışma Süresi (Vardiya Bazlı)
# ======================================================

SESSION_GAP = pd.Timedelta(minutes=5)

working_hours = []

for driver, group in telemetry.groupby("DRIVER_NAME"):

    group = group.sort_values("TS").reset_index(drop=True)

    session_start = group.loc[0, "TS"]
    session_end = group.loc[0, "TS"]

    total_seconds = 0

    for i in range(1, len(group)):

        current_ts = group.loc[i, "TS"]
        previous_ts = group.loc[i - 1, "TS"]

        # Eğer kayıtlar arasında 5 dakikadan fazla boşluk varsa
        # önceki vardiya bitmiş kabul edilir.
        if current_ts - previous_ts > SESSION_GAP:

            total_seconds += (
                session_end - session_start
            ).total_seconds()

            session_start = current_ts

        session_end = current_ts

    # Son vardiyayı ekle
    total_seconds += (
        session_end - session_start
    ).total_seconds()

    working_hours.append({
        "DRIVER_NAME": driver,
        "WORKING_HOURS": round(total_seconds / 3600, 2)
    })

working_hours = pd.DataFrame(working_hours)

print("\nÇalışma Süreleri")
print(working_hours.head())

# ======================================================
# Toplam Telemetri Kaydı
# ======================================================

record_count = (
    telemetry
    .groupby("DRIVER_NAME")
    .size()
    .rename("TOTAL_RECORDS")
    .reset_index()
)

print("\nToplam Telemetri Kaydı")
print(record_count.head())




# ======================================================
# Speeding Events
# ======================================================

speeding_events = []

for driver, group in telemetry.groupby("DRIVER_NAME"):

    event_count = 0
    speeding = False

    for speed in group["VEHICLE_SPEED"]:

        if speed > SPEED_LIMIT and not speeding:
            event_count += 1
            speeding = True

        elif speed <= SPEED_LIMIT:
            speeding = False

    speeding_events.append({
        "DRIVER_NAME": driver,
        "SPEEDING_EVENTS": event_count
    })

speeding_events = pd.DataFrame(speeding_events)

print("\nSpeeding Events")
print(speeding_events.head())

# ======================================================
# Driver Analysis
# ======================================================

driver_analysis = (
    driver_features
    .merge(
        avg_speed,
        on="DRIVER_NAME",
        how="left"
    )
    .merge(
        max_speed,
        on="DRIVER_NAME",
        how="left"
    )
    .merge(
        std_speed,
        on="DRIVER_NAME",
        how="left"
    )
    .merge(
        record_count,
        on="DRIVER_NAME",
        how="left"
    )
    .merge(
    speeding_events,
    on="DRIVER_NAME",
    how="left"
    )
    .merge(
    working_hours,
    on="DRIVER_NAME",
    how="left"
    )

)

print("\nDriver Analysis")

print(
    driver_analysis.head()
)

print(
    f"\nToplam sürücü: {len(driver_analysis)}"
)


# ======================================================
# Alarm / Saat
# ======================================================

driver_analysis["ALARM_PER_HOUR"] = (
    driver_analysis["TOTAL_ALARM"] /
    driver_analysis["WORKING_HOURS"]
).round(2)

driver_analysis["ALARM_PER_HOUR"] = (
    driver_analysis["ALARM_PER_HOUR"]
    .replace([float("inf")], 0)
    .fillna(0)
)

print("\nAlarm / Saat")
print(
    driver_analysis[
        ["DRIVER_NAME", "ALARM_PER_HOUR"]
    ].head()
)

# ======================================================
# en fazla hız ihlali yapan ilk 20 sürücü
# ======================================================


print("\nEn fazla hız ihlali yapan ilk 20 sürücü")

print(
    speeding_events
    .sort_values(
        "SPEEDING_EVENTS",
        ascending=False
    )
    .head(20)
)

# ======================================================
# ClickHouse'a Yaz
# ======================================================

print("\nDriver Analysis tablosu temizleniyor...")

client.command("""
TRUNCATE TABLE telemetri_data_warehouse_test.driver_analysis_test
""")

table_columns = client.query_df("""

DESCRIBE TABLE telemetri_data_warehouse_test.driver_analysis_test

""")["name"].tolist()

driver_analysis = driver_analysis[table_columns]

print("Driver Analysis yazılıyor...")

driver_analysis = (
    driver_analysis
    .astype(object)
    .where(pd.notna(driver_analysis), None)
)


if driver_analysis["AVG_VEHICLE_SPEED"].isna().any():

    print("\nTelemetri kaydı bulunamayan sürücüler:")

    print(
        driver_analysis.loc[
            driver_analysis["AVG_VEHICLE_SPEED"].isna(),
            "DRIVER_NAME"
        ].to_list()
    )


driver_analysis = driver_analysis.fillna({
    "AVG_VEHICLE_SPEED": 0.0,
    "MAX_VEHICLE_SPEED": 0.0,
    "STD_VEHICLE_SPEED": 0.0,
    "TOTAL_RECORDS": 0,
    "WORKING_HOURS": 0.0,
    "ALARM_PER_HOUR": 0.0,
    "SPEEDING_EVENTS": 0
    
})

driver_analysis = driver_analysis.infer_objects(copy=False)

print(driver_analysis.isnull().sum())


client.insert_df(
    "telemetri_data_warehouse_test.driver_analysis_test",
    driver_analysis
)

print("✓ Driver Analysis başarıyla yazıldı.")



# ======================================================
# Excel
# ======================================================

with pd.ExcelWriter(EXCEL_DIR / "driver_analysis.xlsx") as writer:

    driver_analysis.to_excel(
        writer,
        sheet_name="Driver Analysis",
        index=False
    )

print("✓ Excel oluşturuldu.")
print("Konum: outputs/excel/driver_analysis.xlsx")