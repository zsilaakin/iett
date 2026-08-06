"""
Driver Features - Exploratory Data Analysis (EDA)

Bu script driver_features_test tablosu üzerinde:

- Genel istatistikleri çıkarır.
- Alarm dağılımlarını analiz eder.
- En riskli sürücüleri listeler.
- Alarm türleri arasındaki korelasyonları hesaplar.
- Grafikleri outputs/plots klasörüne kaydeder.

Author: Zübeyde Sıla Akın
"""

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

PLOT_DIR = BASE_DIR / "outputs" / "plots"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

import pandas as pd
import matplotlib.pyplot as plt

from db import client



pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.expand_frame_repr", False)

df = client.query_df("""

SELECT *
FROM telemetri_data_warehouse_test.driver_features_test

""")
################


print("=" * 60)
print("GENEL BİLGİLER")
print("=" * 60)

print(f"Sürücü Sayısı : {len(df)}")
print(f"Kolon Sayısı  : {len(df.columns)}")

print("\nİstatistikler:")
print(df.describe().T)


##############


print("\n" + "=" * 60)
print("EN FAZLA ALARM ALAN İLK 20 SÜRÜCÜ")
print("=" * 60)

top20 = (
    df.sort_values(
        "TOTAL_ALARM",
        ascending=False
    )
    .head(20)
)

print(top20[["DRIVER_NAME", "TOTAL_ALARM"]])


###############


alarm_cols = [
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

print("\n" + "=" * 60)
print("ALARM TÜRLERİNİN TOPLAM SAYILARI")
print("=" * 60)

print(df[alarm_cols].sum().sort_values(ascending=False))

#################


print("\n" + "=" * 60)
print("TOTAL_ALARM KORELASYONLARI")
print("=" * 60)

corr = df[alarm_cols + ["TOTAL_ALARM"]].corr()

print(corr["TOTAL_ALARM"].sort_values(ascending=False))

##################

print("\n" + "=" * 60)
print("ALARM TÜRLERİ KORELASYON MATRİSİ")
print("=" * 60)

print(corr.round(2))

###################

print("\n" + "=" * 60)
print("ALARM ALMAYAN SÜRÜCÜLER")
print("=" * 60)

print(f"Hiç alarm almayan sürücü sayısı : {(df['TOTAL_ALARM'] == 0).sum()}")


####################


print("\n" + "=" * 60)
print("ALARM ORANLARI")
print("=" * 60)

alarm_sum = df[alarm_cols].sum()

alarm_percent = (
    alarm_sum /
    alarm_sum.sum() * 100
).round(2)

print(alarm_percent.sort_values(ascending=False))



####################


print("\n" + "=" * 60)
print("ALARM YOĞUNLUĞU")
print("=" * 60)


bins = [0,5,10,20,40,100]
labels = [
    "1-5",
    "6-10",
    "11-20",
    "21-40",
    "40+"
]

df["ALARM_GROUP"] = pd.cut(
    df["TOTAL_ALARM"],
    bins=bins,
    labels=labels,
    include_lowest=True
)

print(df["ALARM_GROUP"].value_counts().sort_index())


####################


print("\n" + "=" * 60)
print("AYKIRI SÜRÜCÜLER")
print("=" * 60)


outliers = df[df["TOTAL_ALARM"] > 40]

print(outliers)




####################


print("\n" + "=" * 60)
print("AYKIRI PROFİLİ İLK 10 SÜRÜCÜ")
print("=" * 60)


print(
    top20[
        [
            "DRIVER_NAME",
            "HEAD_DOWN",
            "EYE_CLOSURE",
            "PHONE_CALL",
            "SMOKING"
        ]
    ]
)


####################

print("\n" + "=" * 60)
print("HER ALARMI ALAN SÜRÜCÜ SAYISI")
print("=" * 60)

driver_count = (df[alarm_cols] > 0).sum()

print(driver_count.sort_values(ascending=False))


####################
# GRAFİKLER
####################

print("\n" + "=" * 60)
print("GRAFİKLER OLUŞTURULUYOR")
print("=" * 60)

# --------------------------------------------------
# Alarm Türlerinin Dağılımı
# --------------------------------------------------

plt.figure(figsize=(10,6))

alarm_percent.sort_values().plot(kind="barh")

plt.title("Alarm Türlerinin Yüzdesel Dağılımı")
plt.xlabel("Yüzde (%)")
plt.ylabel("Alarm Türü")

plt.tight_layout()

plt.savefig(
    PLOT_DIR / "alarm_oranlari.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# --------------------------------------------------
# Alarm Yoğunluğu
# --------------------------------------------------

plt.figure(figsize=(8,5))

df["ALARM_GROUP"].value_counts().sort_index().plot(kind="bar")

plt.title("Sürücülerin Alarm Yoğunluğu")
plt.xlabel("Toplam Alarm Aralığı")
plt.ylabel("Sürücü Sayısı")

plt.tight_layout()

plt.savefig(
    PLOT_DIR / "alarm_yogunlugu.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# --------------------------------------------------
# En Fazla Alarm Alan İlk 20 Sürücü
# --------------------------------------------------

plt.figure(figsize=(14,6))

top20.plot(
    x="DRIVER_NAME",
    y="TOTAL_ALARM",
    kind="bar",
    legend=False
)

plt.title("En Fazla Alarm Alan İlk 20 Sürücü")
plt.xlabel("Sürücü")
plt.ylabel("Toplam Alarm")

plt.xticks(rotation=75)

plt.tight_layout()

plt.savefig(
    PLOT_DIR / "top20_surucu.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# --------------------------------------------------
# Korelasyon Matrisi
# --------------------------------------------------

plt.figure(figsize=(10,8))

plt.imshow(corr, cmap="coolwarm")

plt.xticks(
    range(len(corr.columns)),
    corr.columns,
    rotation=90
)

plt.yticks(
    range(len(corr.columns)),
    corr.columns
)

plt.colorbar()

plt.title("Alarm Korelasyon Matrisi")

plt.tight_layout()

plt.savefig(
    PLOT_DIR / "korelasyon_matrisi.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("\nGrafikler başarıyla oluşturuldu!")
print(f"Konum: {PLOT_DIR}")

print("\nOluşturulan grafikler:")

for file in PLOT_DIR.glob("*.png"):
    print(f"  ✓ outputs/plots/{file.name}")