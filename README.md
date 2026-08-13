# 🚍 IETT Driver Risk Scoring Project

This project was developed during my internship at **IETT Information Technologies Department** to analyze driver behavior using Driver Monitoring System (DSM) alarms and vehicle telemetry data.

The project matches DSM alarms with drivers, generates driver-based behavioral features, enriches them with telemetry information, and produces a driver risk score that can support safe driving analysis.

---

# 🎯 Project Goals

- Match DSM alarms with driver information
- Generate driver-based behavioral features
- Enrich alarm data with telemetry features
- Calculate a Driver Risk Score
- Classify drivers according to risk level
- Produce interpretable risk analysis for each driver

---

# 🛠 Technologies

- Python
- Pandas
- SQL
- ClickHouse
- VS Code
- Git & GitHub

---

# 📂 Project Structure

```text
iett
│
├── queries/
│   ├── dahua_dsm.sql
│   ├── telemetry_akia.sql
│   ├── telemetry_otokar.sql
│   └── kts.sql
│
├── scripts/
│   ├── match_dahua_dsm_driver.py
│   ├── match_kts_driver.py
│   ├── build_driver_features.py
│   ├── build_driver_analysis.py
│   └── build_driver_score.py
│
├── outputs/
│   ├── csv/
│   ├── excel/
│   └── plots/
│
├── db.py
├── config.py
├── requirements.txt
└── README.md
```

---

# 🔄 Data Pipeline

```text
DSM Alarms
      │
      ▼
Driver Matching
      │
      ▼
driver_features_test
      │
      ▼
Telemetry Feature Engineering
      │
      ▼
driver_analysis_test
      │
      ▼
Risk Scoring
      │
      ▼
driver_score_test
```

---

# 📊 Driver Features

### DSM Features

- Total Alarm Count
- Head Down
- Eye Closure
- Phone Call
- Looking Around
- Lane Departure
- Seatbelt
- Leave Seat
- Yawning
- Close Distance
- Smoking
- Infrared Blocking Glasses

### Telemetry Features

- Average Vehicle Speed
- Maximum Vehicle Speed
- Speed Standard Deviation
- Speeding Events (>70 km/h)
- Total Telemetry Records
- Alarm Per Hour

---

# ⚠️ Driver Risk Scoring

The risk scoring model combines weighted DSM alarm counts and speeding events.

Each alarm type is assigned a different weight according to its impact on driving safety.

The calculated raw score is normalized into a **0–100 Driver Risk Score** using Min-Max Scaling.

Drivers are classified into four categories:

- LOW
- MEDIUM
- HIGH
- CRITICAL

For interpretability, the three most influential risk factors are also reported:

- TOP_RISK_REASON_1
- TOP_RISK_REASON_2
- TOP_RISK_REASON_3

---

# 📈 Outputs

The project automatically generates:

### ClickHouse Tables

- driver_features_test
- driver_analysis_test
- driver_score_test

### Excel Reports

- driver_analysis.xlsx
- driver_score.xlsx

---

# 📊 Example Output

The generated risk report contains:

- Driver Name
- Risk Score (0–100)
- Risk Level
- Top 3 Risk Reasons
- Telemetry Features
- DSM Alarm Features

---

# 🚀 Future Improvements

- Distance-based normalization
- Harsh Braking Detection
- Harsh Acceleration Detection
- Rolling-window driver analysis
- Machine Learning based risk prediction
- Interactive dashboard (Power BI / Streamlit)

---

# 👩‍💻 Author

**Zübeyde Sıla Akın**

Computer Engineering Student

Intern @ IETT Information Technologies Department
