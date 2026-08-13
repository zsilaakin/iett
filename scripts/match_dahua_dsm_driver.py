

"""
Dahua Driver Matching

Bu script Dahua DSM alarm kayıtlarını telemetri verileri ile eşleştirerek:

- Alarm anındaki sürücüyü belirler.
- Alarm anındaki araç hızını (VEHICLE_SPEED) ekler.
- Alarm zamanı ile telemetri zamanı arasındaki farkı hesaplar.
- Elde edilen sonuçları dahua_dsm_alarms_driver_test tablosuna kaydeder.

Author: Zübeyde Sıla Akın
"""

# ======================================================
# Imports
# ======================================================

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import pandas as pd

from db import client


# ======================================================
# Paths
# ======================================================

QUERY_DIR = BASE_DIR / "queries"


# ======================================================
# SQL Oku
# ======================================================

def read_sql(filename):

    with open(QUERY_DIR / filename, "r", encoding="utf-8") as file:

        return file.read().strip().rstrip(";")


# ======================================================
# Veriyi Çek
# ======================================================

def load_data():

    print("Dahua DSM okunuyor...")

    dsm = client.query_df(
        read_sql("dahua_dsm.sql")
    )

    print(f"{len(dsm):,} kayıt")

    print("Akia Telemetri okunuyor...")

    sql = read_sql("telemetry_akia.sql")

    print("Telemetri sorgusu çalıştırılıyor...")

    telemetry = client.query_df(sql) 

    print(f"{len(telemetry):,} kayıt")

    return dsm, telemetry


# ======================================================
# Ön İşleme
# ======================================================

def preprocess(dsm, telemetry):

    dsm["ALARM_DATE"] = pd.to_datetime(
        dsm["ALARM_DATE"],
        errors="coerce"
    )

    telemetry["TS"] = pd.to_datetime(
        telemetry["TS"],
        errors="coerce"
    )

    dsm = dsm.dropna(
        subset=["DOOR_NUMBER", "ALARM_DATE"]
    ).copy()

    telemetry = telemetry.dropna(
        subset=["DOOR_NUMBER", "TS", "DRIVER_NAME"]
    ).copy()

    dsm["DOOR_NUMBER"] = (
        dsm["DOOR_NUMBER"]
        .astype(str)
        .str.strip()
    )

    telemetry["DOOR_NUMBER"] = (
        telemetry["DOOR_NUMBER"]
        .astype(str)
        .str.strip()
    )

    dsm = (
        dsm
        .sort_values(
            ["ALARM_DATE", "DOOR_NUMBER"]
        )
        .reset_index(drop=True)
    )

    telemetry = (
        telemetry
        .sort_values(
            ["TS", "DOOR_NUMBER"]
        )
        .reset_index(drop=True)
    )

    return dsm, telemetry


# ======================================================
# Şoför Eşleştirme
# ======================================================

def match_driver(dsm, telemetry):

    result = pd.merge_asof(

        left=dsm,

        right=telemetry,

        left_on="ALARM_DATE",

        right_on="TS",

        by="DOOR_NUMBER",

        direction="backward",

        tolerance=pd.Timedelta("10min")

    )

    if "DRIVER_NAME_y" in result.columns:
        result["DRIVER_NAME"] = result["DRIVER_NAME_y"]
        result.drop(columns=["DRIVER_NAME_y"], inplace=True)

    if "DRIVER_NAME_x" in result.columns:
        result.drop(columns=["DRIVER_NAME_x"], inplace=True)

    result["TIME_DIFF_SECOND"] = (

        result["ALARM_DATE"] -
        result["TS"]

    ).dt.total_seconds()

    print("\nMerge sonrası kolonlar:")
    print(result.columns.tolist())

    return result



# ======================================================
# Main
# ======================================================

def main():

    print("=" * 60)
    print("DAHUA DRIVER MATCH")
    print("=" * 60)

    dsm, telemetry = load_data()

    dsm, telemetry = preprocess(
        dsm,
        telemetry
    )

    result = match_driver(
        dsm,
        telemetry
    )

    print("\nİlk 10 eşleşme:")
    print(result.head(10))

    print()

    print("=" * 60)

    print(f"Toplam Alarm       : {len(result):,}")

    print(
        f"Eşleşen Sürücü     : {result['DRIVER_NAME'].notna().sum():,}"
    )

    print(
        f"Eşleşmeyen Alarm   : {result['DRIVER_NAME'].isna().sum():,}"
    )
    print("\nSonuç kolonları:")
    print(result.columns.tolist())

    table_columns = client.query_df(
        """
        DESCRIBE TABLE telemetri_data_warehouse_test.dahua_dsm_alarms_driver_test
        """
    )["name"].tolist()

    result = result[table_columns]

    result = result.astype(object).where(pd.notna(result), None)

    print("ClickHouse'a yazılıyor...")

    print(f"DB Kolon Sayısı      : {len(table_columns)}")
    print(f"DataFrame Kolon Sayısı : {len(result.columns)}")



    print("Eski tablo temizleniyor...")

    client.command("""
    TRUNCATE TABLE telemetri_data_warehouse_test.dahua_dsm_alarms_driver_test
    """)

    client.insert_df(
        "telemetri_data_warehouse_test.dahua_dsm_alarms_driver_test",
        result
    )

    print("✓ Veriler başarıyla yazıldı.")
    print("=" * 60)
    print("İŞLEM TAMAMLANDI")
    print("=" * 60)
    print("✓ Dahua DSM eşleştirmesi tamamlandı.")
    print("✓ Sonuçlar ClickHouse'a yazıldı.")

    success_rate = (
    result["DRIVER_NAME"].notna().mean()*100
)

    print(
    f"Eşleşme Başarısı : %{success_rate:.2f}"
)

if __name__ == "__main__":
    main()