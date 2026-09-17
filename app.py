
import streamlit as st
import pandas as pd, numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, r2_score

st.set_page_config(page_title="SteelPlant AI Command Center", page_icon="🏭", layout="wide")

DATA = Path(__file__).parent/"data"/"synthetic_steelplant_data.csv"

@st.cache_data
def load(path):
    return pd.read_csv(path, parse_dates=["date"])

df = load(DATA)

st.title("🏭 SteelPlant AI Command Center")
st.caption("Industrial Energy + Gas Intelligence | Forecast • Detect • Explain • Simulate • Recommend")

with st.sidebar:
    st.header("Control Room")
    unit = st.selectbox("Plant Unit", ["All"] + sorted(df.unit.unique()))
    start,end = st.date_input("Analysis window", [df.date.min().date(), df.date.max().date()])
    energy_price = st.number_input("Energy price (₹/MWh)", value=650, min_value=1)
    gas_price = st.number_input("Gas price (₹/kNm³)", value=900, min_value=1)
    anomaly_rate = st.slider("Anomaly sensitivity", .01, .10, .035, .005)

v=df[(df.date>=pd.Timestamp(start))&(df.date<=pd.Timestamp(end))].copy()
if unit!="All": v=v[v.unit==unit]
if v.empty: st.stop()

# ---- Executive KPIs ----
st.subheader("Executive Control Room")
cols=st.columns(6)
cols[0].metric("Production", f"{v.production_tpd.sum():,.0f} t")
cols[1].metric("Energy", f"{v.energy_mwh.sum():,.0f} MWh")
cols[2].metric("Gas", f"{v.gas_knm3.sum():,.0f} kNm³")
cols[3].metric("Energy intensity", f"{v.energy_intensity_kwh_t.mean():.1f} kWh/t")
cols[4].metric("Gas intensity", f"{v.gas_intensity_nm3_t.mean():.1f} Nm³/t")
cols[5].metric("Estimated utility cost", f"₹{(v.energy_mwh.sum()*energy_price+v.gas_knm3.sum()*gas_price)/1e7:.2f} Cr")

tab1,tab2,tab3,tab4,tab5 = st.tabs(["📈 Monitor","🔮 Forecast","🚨 Detect","🧪 Simulate","🧠 Explain"])

with tab1:
    st.subheader("Consumption & Intensity Trends")
    daily=v.groupby("date").agg(energy_mwh=("energy_mwh","sum"),gas_knm3=("gas_knm3","sum"),production=("production_tpd","sum"))
    daily["energy_intensity"]=daily.energy_mwh*1000/daily.production
    daily["gas_intensity"]=daily.gas_knm3*1000/daily.production
    st.line_chart(daily[["energy_mwh","gas_knm3"]])
    c1,c2=st.columns(2)
    with c1: st.line_chart(daily["energy_intensity"])
    with c2: st.line_chart(daily["gas_intensity"])
    s=v.groupby("unit").agg(
        production=("production_tpd","sum"), energy=("energy_mwh","sum"), gas=("gas_knm3","sum"),
        energy_intensity=("energy_intensity_kwh_t","mean"), gas_intensity=("gas_intensity_nm3_t","mean")
    ).sort_values("energy_intensity",ascending=False)
    st.dataframe(s.style.format("{:,.2f}"),use_container_width=True)

with tab2:
    st.subheader("14-Day Energy Forecast")
    d=v.groupby("date").agg(y=("energy_mwh","sum"),prod=("production_tpd","sum"),
                             load=("load_pct","mean"),temp=("ambient_temp_c","mean")).reset_index()
    d["lag1"]=d.y.shift(1); d["lag7"]=d.y.shift(7); d["roll7"]=d.y.rolling(7).mean(); d["dow"]=d.date.dt.dayofweek
    d=d.dropna()
    feats=["prod","load","temp","lag1","lag7","roll7","dow"]
    if len(d)>=90:
        split=int(len(d)*.8); tr=d.iloc[:split]; te=d.iloc[split:]
        model=RandomForestRegressor(n_estimators=300,min_samples_leaf=2,random_state=42)
        model.fit(tr[feats],tr.y)
        pred=model.predict(te[feats])
        mae=mean_absolute_error(te.y,pred); r2=r2_score(te.y,pred)
        a,b=st.columns(2); a.metric("Hold-out MAE",f"{mae:.1f} MWh"); b.metric("Hold-out R²",f"{r2:.3f}")
        chart=pd.DataFrame({"Actual":te.y.values,"Predicted":pred},index=te.date)
        st.line_chart(chart)
        hist=d.copy()
        last=hist.date.max(); last_y=hist.y.iloc[-1]; future=[]
        for i in range(1,15):
            nd=last+pd.Timedelta(days=i); recent=hist.tail(7)
            X=pd.DataFrame([[recent["prod"].mean(),recent["load"].mean(),recent["temp"].mean(),
                             last_y,hist.y.iloc[-7],hist.y.tail(7).mean(),nd.dayofweek]],columns=feats)
            yhat=float(model.predict(X)[0]); future.append([nd,yhat])
            hist=pd.concat([hist,pd.DataFrame([[nd,yhat,recent["prod"].mean(),recent["load"].mean(),recent["temp"].mean(),last_y,hist.y.iloc[-7],hist.y.tail(7).mean(),nd.dayofweek]],columns=["date","y","prod","load","temp","lag1","lag7","roll7","dow"])],ignore_index=True)
            last_y=yhat
        fc=pd.DataFrame(future,columns=["date","forecast_mwh"]).set_index("date")
        st.write("Next 14 days:")
        st.dataframe(fc.style.format("{:,.1f}"),use_container_width=True)
        st.line_chart(fc)
    else: st.info("Select a longer period.")

with tab3:
    st.subheader("Abnormal Consumption Radar")
    X=v[["energy_intensity_kwh_t","gas_intensity_nm3_t","load_pct","process_pressure_bar"]].fillna(0)
    iso=IsolationForest(contamination=anomaly_rate,random_state=42)
    v["score"]=iso.fit_predict(X); v["risk"]=np.where(v.score==-1,"HIGH","NORMAL")
    alerts=v[v.score==-1].sort_values("date",ascending=False)
    st.metric("Potential abnormal days",len(alerts))
    st.dataframe(alerts[["date","unit","production_tpd","energy_intensity_kwh_t","gas_intensity_nm3_t","load_pct","risk"]].head(30),use_container_width=True)
    st.caption("Alerts are screening signals for engineering investigation—not proof of equipment failure or leakage.")

with tab4:
    st.subheader("What-if Energy Efficiency Simulator")
    st.write("Estimate savings if an operating area reduces energy intensity by a chosen percentage.")
    reduction=st.slider("Target reduction in energy intensity",0,20,8)
    baseline=v.energy_mwh.sum()
    estimated=baseline*(reduction/100)
    savings=estimated*energy_price
    c1,c2,c3=st.columns(3)
    c1.metric("Baseline energy",f"{baseline:,.0f} MWh")
    c2.metric("Potential reduction",f"{estimated:,.0f} MWh")
    c3.metric("Indicative savings",f"₹{savings/1e5:,.1f} lakh")
    st.info("This is a scenario model. Actual savings must be validated against process constraints, production targets and plant engineering data.")

with tab5:
    st.subheader("Explainable Analytics")
    d=v.dropna(subset=["energy_mwh","production_tpd","load_pct","ambient_temp_c","process_pressure_bar"]).copy()
    features=["production_tpd","load_pct","ambient_temp_c","process_pressure_bar"]
    if len(d)>80:
        split=int(len(d)*.8)
        m=RandomForestRegressor(n_estimators=250,random_state=42,min_samples_leaf=2).fit(d.iloc[:split][features],d.iloc[:split].energy_mwh)
        pi=permutation_importance(m,d.iloc[split:][features],d.iloc[split:].energy_mwh,n_repeats=8,random_state=42)
        imp=pd.DataFrame({"feature":features,"importance":pi.importances_mean}).sort_values("importance",ascending=False)
        st.bar_chart(imp.set_index("feature"))
        st.write("Interpretation: permutation importance measures how much model performance changes when a feature is shuffled. It indicates predictive influence, not causality.")
    else: st.info("Select a longer period.")

st.divider()
st.subheader("Engineering Action Queue")
overall_e=v.energy_intensity_kwh_t.mean(); overall_g=v.gas_intensity_nm3_t.mean()
for u,g in v.groupby("unit"):
    ei=g.energy_intensity_kwh_t.mean(); gi=g.gas_intensity_nm3_t.mean()
    flags=[]
    if ei>overall_e*1.08: flags.append("Investigate high energy intensity")
    if gi>overall_g*1.08: flags.append("Investigate high gas intensity / wastage")
    if flags:
        st.warning(f"**{u}** → " + " • ".join(flags))
    else:
        st.success(f"**{u}** → No priority flag from current screening rules.")

st.caption("Portfolio prototype using synthetic data. Do not represent the official dataset.")