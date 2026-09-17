# 🏭 SteelPlant AI Command Center

### Industrial Energy + Gas Intelligence | Monitor • Predict • Detect • Explain • Simulate • Recommend

A portfolio project inspired by industrial energy and gas-consumption problems from the SAIL Technical Internship project list.

## ⭐ What makes this different?

Instead of building a static Power BI-style dashboard, this prototype demonstrates an **AI-assisted industrial decision-support workflow**:

> **Monitor → Forecast → Detect anomalies → Explain drivers → Simulate savings → Create an engineering action queue**

### Core modules

| Module | Technique | Business purpose |
|---|---|---|
| Control Room | KPI engineering | Plant-wide visibility |
| Intensity Analytics | Normalization by production | Fair unit comparison |
| Forecast | Random Forest + lag/rolling features | Plan upcoming energy demand |
| Anomaly Radar | Isolation Forest | Screen abnormal consumption |
| Explainability | Permutation importance | Understand predictive drivers |
| What-if Simulator | Scenario modelling | Estimate potential savings |
| Action Queue | Rule-based screening | Turn analytics into next actions |

## Tech Stack

**Python, Pandas, NumPy, Scikit-learn, Streamlit, Matplotlib**

## Demo Data

The repository includes **2,920 synthetic daily records** across four representative industrial units over 2024–2025.

> The data is synthetic and is **not SAIL data**. It is included only to demonstrate the analytics pipeline.

## Run

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## CV-ready description

**SteelPlant AI Command Center | Python, Scikit-learn, Streamlit**
- Built an end-to-end industrial decision-support prototype for plant-wise energy and gas intelligence, combining KPI analytics, forecasting, anomaly detection, explainability and scenario simulation.
- Developed a Random Forest energy forecasting pipeline using production, equipment load, ambient conditions and lag/rolling features with chronological hold-out validation.
- Implemented Isolation Forest anomaly screening to identify abnormal energy/gas intensity and a permutation-importance layer to explain model drivers.
- Added a what-if efficiency simulator and engineering action queue to translate model outputs into potential savings scenarios and investigation priorities.

## Interview pitch

> “I wanted to solve the problem beyond a normal dashboard. I built a mini industrial control center that first measures energy and gas intensity, then forecasts energy demand, detects abnormal consumption, explains which operating variables influence predictions, and finally lets an engineer test a what-if efficiency scenario. Because real plant data is confidential, I used synthetic data and designed the pipeline so authorized data can be plugged in later.”

## Ethical/data note

Do **not** claim this was trained on SAIL data. The prototype is inspired by the internship problem statements and uses synthetic data.
