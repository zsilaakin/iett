"""
Driver Feature Engineering

Bu script sürücü bazında DSM alarm özniteliklerini (features)
oluşturmak amacıyla geliştirilmiştir.

Script kapsamında:

- Dahua DSM alarm kayıtları okunur.
- Her sürücünün aldığı toplam alarm sayısı hesaplanır.
- Alarm türleri sütunlara dönüştürülerek öznitelik tablosu oluşturulur.
- Eksik alarm türleri sıfır ile tamamlanır.
- Sonuçlar driver_features_test tablosuna yazılır.

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
# ======================================================
# Veriyi Çek
# ======================================================

df = client.query_df("""

SELECT
    DRIVER_NAME,
    ALARM_NAME
FROM telemetri_data_warehouse_test.dahua_dsm_alarms_driver_test
WHERE DRIVER_NAME IS NOT NULL

""")

# ======================================================
# Toplam Alarm
# ======================================================

total_alarm = (
    df.groupby("DRIVER_NAME")
      .size()
      .rename("TOTAL_ALARM")
)

# ======================================================
# Alarmları Sütun Yap
# ======================================================

alarm_counts = (
    df.groupby(["DRIVER_NAME", "ALARM_NAME"])
      .size()
      .unstack(fill_value=0)
)

# ======================================================
# Birleştir
# ======================================================

driver_features = alarm_counts.join(total_alarm)
driver_features = driver_features.reset_index()

# ======================================================
# Sütun İsimlerini Düzenle
# ======================================================

driver_features = driver_features.rename(columns={
    "Head Down Alarm (Distracted Driving)": "HEAD_DOWN",
    "Seatbelt Not Worn Alarm": "SEATBELT",
    "Eye Closure Alarm (Fatigue Driving)": "EYE_CLOSURE",
    "Phone Call Alarm": "PHONE_CALL",
    "Lane Departure Alarm": "LANE_DEPARTURE",
    "Driver Leave Seat Alarm": "LEAVE_SEAT",
    "Yawning Alarm (Fatigue Driving)": "YAWNING",
    "Close Distance Warning": "CLOSE_DISTANCE",
    "Looking Around Alarm (Distracted Driving)": "LOOKING_AROUND",
    "Infrared Blocking Glasses Alarm": "INFRARED_GLASSES",
    "Smoking Alarm": "SMOKING"
})

# ======================================================
# Eksik Alarm Sütunlarını Oluştur
# ======================================================

expected_cols = [
    "HEAD_DOWN",
    "SEATBELT",
    "EYE_CLOSURE",
    "PHONE_CALL",
    "LANE_DEPARTURE",
    "LEAVE_SEAT",
    "YAWNING",
    "CLOSE_DISTANCE",
    "LOOKING_AROUND",
    "INFRARED_GLASSES",
    "SMOKING"
]

for col in expected_cols:
    if col not in driver_features.columns:
        driver_features[col] = 0

# ======================================================
# ClickHouse Sütun Sırası
# ======================================================

driver_features = driver_features[
    [
        "DRIVER_NAME",
        "TOTAL_ALARM",
        "HEAD_DOWN",
        "SEATBELT",
        "EYE_CLOSURE",
        "PHONE_CALL",
        "LANE_DEPARTURE",
        "LEAVE_SEAT",
        "YAWNING",
        "CLOSE_DISTANCE",
        "LOOKING_AROUND",
        "INFRARED_GLASSES",
        "SMOKING"
    ]
]

# ======================================================
# Kontrol
# ======================================================

print(driver_features.head())
print(driver_features.columns.tolist())
print(f"\nToplam sürücü: {len(driver_features)}")

# ======================================================
# ClickHouse'a Yaz
# ======================================================

client.command("TRUNCATE TABLE telemetri_data_warehouse_test.driver_features_test")

client.insert_df(
    "telemetri_data_warehouse_test.driver_features_test",
    driver_features
)

print("\nVeriler başarıyla yazıldı.")


##########

# ======================================================
# Excel'e Kaydet
# ======================================================

# ======================================================
# Excel'e Kaydet
# ======================================================

with pd.ExcelWriter(EXCEL_DIR / "driver_features.xlsx") as writer:

    driver_features.to_excel(
        writer,
        sheet_name="Driver Features",
        index=False
    )

    pd.DataFrame({
        "Metric": [
            "Driver Count",
            "Alarm Type Count"
        ],
        "Value": [
            len(driver_features),
            len(expected_cols)
        ]
    }).to_excel(
        writer,
        sheet_name="Summary",
        index=False
    )

print("\n✓ Excel dosyası oluşturuldu.")
print(f"Konum: outputs/excel/driver_features.xlsx")