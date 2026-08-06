from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import pandas as pd

from db import client

# ======================================================
# Klasörler
# ======================================================

QUERY_DIR = BASE_DIR / "queries"
OUTPUT_DIR = BASE_DIR / "outputs" / "excel"


# ======================================================
# SQL Dosyasını Oku
# ======================================================

def read_sql(filename):
    with open(QUERY_DIR / filename, "r", encoding="utf-8") as file:
        return file.read().strip().rstrip(";")


# ======================================================
# Veriyi Çek
# ======================================================

def load_data():

    print("KTS verisi okunuyor...")

    kts = client.query_df(
        read_sql("kts.sql")
    )

    print(f"KTS kayıt sayısı : {len(kts):,}")

    print("Telemetri verisi okunuyor...")

    telemetry = client.query_df(
        read_sql("telemetry_otokar.sql")
    )

    print(f"Telemetri kayıt sayısı : {len(telemetry):,}")

    return kts, telemetry


# ======================================================
# Ön İşleme
# ======================================================

def preprocess(kts, telemetry):

    # datetime
    kts["EVENT_START_TIME"] = pd.to_datetime(
        kts["EVENT_START_TIME"],
        errors="coerce"
    )

    telemetry["TS"] = pd.to_datetime(
        telemetry["TS"],
        errors="coerce"
    )

    # merge anahtarları boş olamaz
    kts = kts.dropna(
        subset=["DOOR_NUMBER", "EVENT_START_TIME"]
    )

    telemetry = telemetry.dropna(
        subset=["DOOR_NUMBER", "TS", "DRIVER_NAME"]
    )

    # boşlukları temizle
    kts["DOOR_NUMBER"] = (
        kts["DOOR_NUMBER"]
        .astype(str)
        .str.strip()
    )

    telemetry["DOOR_NUMBER"] = (
        telemetry["DOOR_NUMBER"]
        .astype(str)
        .str.strip()
    )

    # DSM kodundaki gibi zaman öncelikli sırala
    kts = (
        kts
        .sort_values(
            ["EVENT_START_TIME", "DOOR_NUMBER"]
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

    return kts, telemetry


# ======================================================
# Şoför Eşleştirme
# ======================================================

def match_driver(kts, telemetry):

    result = pd.merge_asof(

        left=kts,

        right=telemetry,

        left_on="EVENT_START_TIME",

        right_on="TS",

        by="DOOR_NUMBER",

        direction="backward"

    )

    result["TIME_DIFF_MIN"] = (
        result["EVENT_START_TIME"] -
        result["TS"]
    ).dt.total_seconds() / 60

    return result


# ======================================================
# Excel'e Kaydet
# ======================================================

def save_result(df):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = OUTPUT_DIR / "kts_driver_match.xlsx"

    df.to_excel(
        output_file,
        index=False
    )

    print("\nDosya oluşturuldu.")

    print(output_file)


# ======================================================
# Main
# ======================================================

def main():

    print("=" * 60)
    print("KTS DRIVER MATCH")
    print("=" * 60)

    kts, telemetry = load_data()

    kts, telemetry = preprocess(
        kts,
        telemetry
    )

    result = match_driver(
        kts,
        telemetry
    )

    print("\nKTS dtypes")
    print(kts.dtypes)

    print("\nTelemetri dtypes")
    print(telemetry.dtypes)

    print("\nKTS ilk 10")
    print(kts[["DOOR_NUMBER", "EVENT_START_TIME"]].head(10))

    print("\nTelemetri ilk 10")
    print(telemetry[["DOOR_NUMBER", "TS"]].head(10))

    print("\nSıralı mı?")
    print("KTS :", kts["EVENT_START_TIME"].is_monotonic_increasing)
    print("Telemetri :", telemetry["TS"].is_monotonic_increasing)

    result = match_driver(
        kts,
        telemetry
    )

    print("\nİlk 10 kayıt\n")

    print(result.head(10))

    print("\nİstatistik")

    print("-" * 60)

    print(
        f"Toplam kayıt      : {len(result):,}"
    )

    print(
        f"Eşleşen sürücü    : {result['DRIVER_NAME'].notna().sum():,}"
    )

    print(
        f"Eşleşmeyen kayıt  : {result['DRIVER_NAME'].isna().sum():,}"
    )

    save_result(result)


if __name__ == "__main__":
    main()