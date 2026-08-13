"""
Driver Risk Score

Author: Zübeyde Sıla Akın
"""

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from db import client
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

EXCEL_DIR = BASE_DIR / "outputs" / "excel" 
EXCEL_DIR.mkdir(parents=True, exist_ok=True)

# ======================================================
# Driver Analysis
# ======================================================

df = client.query_df("""

SELECT *
FROM telemetri_data_warehouse_test.driver_analysis_test

""")

print(f"{len(df)} sürücü okundu.")

# ======================================================
# Alarm Katsayıları
# ======================================================

weights = {

    "HEAD_DOWN": 3,

    "EYE_CLOSURE": 5,

    "PHONE_CALL": 4,

    "LOOKING_AROUND": 3,

    "YAWNING": 2,

    "LANE_DEPARTURE": 4,

    "CLOSE_DISTANCE": 2,

    "LEAVE_SEAT": 2,

    "SMOKING": 1,

    "SEATBELT": 3,

    "SPEEDING_EVENTS": 5

}

# ======================================================
# Ham Risk Puanı
# ======================================================

df["RAW_SCORE"] = 0

for feature, weight in weights.items():

    df["RAW_SCORE"] += df[feature] * weight

print("\nHam Risk Puanı")

print(
    df[
        [
            "DRIVER_NAME",
            "RAW_SCORE"
        ]
    ].head()
)



# ======================================================
# Risk Nedenleri
# ======================================================

reason_columns = list(weights.keys())

reason_map = {
    "HEAD_DOWN": "Head Down",
    "EYE_CLOSURE": "Eye Closure",
    "PHONE_CALL": "Phone Call",
    "LOOKING_AROUND": "Looking Around",
    "YAWNING": "Yawning",
    "LANE_DEPARTURE": "Lane Departure",
    "CLOSE_DISTANCE": "Close Distance",
    "LEAVE_SEAT": "Leave Seat",
    "SMOKING": "Smoking",
    "SEATBELT": "Seatbelt",
    "SPEEDING_EVENTS": "Speeding"
}

top1 = []
top2 = []
top3 = []

for _, row in df.iterrows():

    scores = {}

    for col in reason_columns:
        scores[col] = row[col] * weights[col]

    ranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top1.append(f"{reason_map[ranked[0][0]]} ({int(row[ranked[0][0]])})")
    top2.append(f"{reason_map[ranked[1][0]]} ({int(row[ranked[1][0]])})")
    top3.append(f"{reason_map[ranked[2][0]]} ({int(row[ranked[2][0]])})")

df["TOP_RISK_REASON_1"] = top1
df["TOP_RISK_REASON_2"] = top2
df["TOP_RISK_REASON_3"] = top3


# ======================================================
# 0-100 Normalize
# ======================================================

scaler = MinMaxScaler()

df["RISK_SCORE"] = scaler.fit_transform(
    df[["RAW_SCORE"]]
) * 100

df["RISK_SCORE"] = df["RISK_SCORE"].round(2)

# ======================================================
# Risk Seviyesi
# ======================================================

def risk_level(score):

    if score < 20:
        return "LOW"

    elif score < 40:
        return "MEDIUM"

    elif score < 70:
        return "HIGH"

    return "CRITICAL"

df["RISK_LEVEL"] = df["RISK_SCORE"].apply(risk_level)

# ======================================================
# En Riskli 20
# ======================================================

print("\nEn Riskli İlk 20\n")

print(

    df[
        [
            "DRIVER_NAME",
            "RISK_SCORE",
            "RISK_LEVEL",
            "TOP_RISK_REASON_1",
            "TOP_RISK_REASON_2",
            "TOP_RISK_REASON_3"
        ]
    ]

    .sort_values(
        "RISK_SCORE",
        ascending=False
    )

    .head(20)

)

# ======================================================
# Özet İstatistikler
# ======================================================

print("\nRisk Dağılımı\n")

print(df["RISK_LEVEL"].value_counts())

print()

print(f"Toplam Sürücü : {len(df)}")
print(f"En Yüksek Puan: {df['RISK_SCORE'].max():.2f}")
print(f"En Düşük Puan : {df['RISK_SCORE'].min():.2f}")
print(f"Ortalama Puan : {df['RISK_SCORE'].mean():.2f}")



# ======================================================
# ClickHouse
# ======================================================

print("\nDriver Score tablosu temizleniyor...")

client.command("""

TRUNCATE TABLE telemetri_data_warehouse_test.driver_score_test

""")

print("Driver Score yazılıyor...")


table_columns = client.query_df("""

DESCRIBE TABLE telemetri_data_warehouse_test.driver_score_test

""")["name"].tolist()

df = df[table_columns]


df = df.astype(object).where(pd.notna(df), None)

client.insert_df(

    "telemetri_data_warehouse_test.driver_score_test",

    df

)

print("✓ Driver Score başarıyla yazıldı.")

# ======================================================
# Excel
# ======================================================

with pd.ExcelWriter(EXCEL_DIR / "driver_score.xlsx") as writer:

    df.sort_values(
        "RISK_SCORE",
        ascending=False
    ).to_excel(
        writer,
        sheet_name="Driver Score",
        index=False
    )

print("\n✓ driver_score.xlsx oluşturuldu.")