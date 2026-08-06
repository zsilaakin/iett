# 🚍 İETT Driver Risk Scoring Project

Bu proje, İETT stajı kapsamında sürücü davranışlarının analiz edilmesi ve gelecekte sürücü risk puanlama modeli oluşturulabilmesi amacıyla geliştirilmiştir.

Proje kapsamında Dahua DSM (Driver Monitoring System) alarm kayıtları ile araç telemetri verileri eşleştirilmiş, sürücü bazlı özellikler (features) üretilmiş ve keşifsel veri analizi (EDA) çalışmaları gerçekleştirilmiştir.

---

# 🎯 Project Goal

- DSM alarm kayıtlarını sürücü bilgileri ile eşleştirmek
- Sürücü bazında feature engineering yapmak
- Alarm dağılımlarını analiz etmek
- Telemetri verileri ile yeni özellikler üretmek
- Güvenli sürüşü değerlendirebilecek Driver Risk Score altyapısını oluşturmak

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

```
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
│   └── analyze_driver_features.py
│
├── outputs/
│   ├── plots/
│   ├── csv/
│   └── excel/
│
├── db.py
├── config.py
└── requirements.txt
```

---

# 🔄 Data Pipeline

```
DSM Alarms
      │
      ▼
Driver Matching
(match_dahua_dsm_driver.py)
      │
      ▼
dahua_dsm_alarms_driver_test
      │
      ▼
Feature Engineering
(build_driver_features.py)
      │
      ▼
driver_features_test
      │
      ▼
Exploratory Data Analysis
(analyze_driver_features.py)
```

---

# 📊 Current Features

- Total Alarm Count
- Head Down Alarm
- Seatbelt Alarm
- Eye Closure Alarm
- Phone Call Alarm
- Lane Departure Alarm
- Driver Leave Seat Alarm
- Yawning Alarm
- Close Distance Warning
- Looking Around Alarm
- Infrared Blocking Glasses Alarm
- Smoking Alarm

---

# 🚧 Planned Features

- Working Hours
- Total Distance
- Average Speed
- Maximum Speed
- Speed >70 km/h Detection
- Harsh Braking Detection
- Harsh Acceleration Detection
- Driver Risk Score
- Risk Level Classification

---

# 📈 Current Analysis

- Driver-based alarm distributions
- Top risky drivers
- Alarm correlations
- Alarm density analysis
- Outlier detection
- Alarm percentage distributions
- Visualization of driver behavior

---

# 👩‍💻 Author

**Zübeyde Sıla Akın**

Computer Engineering Student

Intern @ İETT Information Technologies Department
