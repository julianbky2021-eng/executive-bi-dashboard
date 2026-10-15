from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "latihan1.js"
NUMERIC_COLUMNS = [
    "Age", "Study_Hours", "Sleep_Hours", "Attendance", "Exam_Score",
    "Monthly_Spending", "Screen_Hours", "Satisfaction",
]
MODEL_FEATURES = ["Study_Hours", "Attendance", "Sleep_Hours", "Screen_Hours"]
RADAR_COLUMNS = ["Study_Hours", "Sleep_Hours", "Attendance", "Exam_Score", "Satisfaction"]
RADAR_LIMITS = {"Study_Hours": 18, "Sleep_Hours": 12, "Attendance": 100, "Exam_Score": 100, "Satisfaction": 10}

st.set_page_config(page_title="Executive BI Dashboard", page_icon="📊", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    """Read the JSON-compatible object literal assigned in the JavaScript file."""
    source = DATA_PATH.read_text(encoding="utf-8")
    prefix = "globalThis.LATIHAN1_DATA = "
    if not source.startswith(prefix):
        raise ValueError(f"Format {DATA_PATH.name} tidak sesuai.")
    object_literal = source[len(prefix):].strip()
    if object_literal.endswith(";"):
        object_literal = object_literal[:-1]
    # The data literal uses strict JSON syntax, so parse data without executing JS.
    dataset = json.loads(object_literal)
    frame = pd.DataFrame(dataset["rows"], columns=dataset["columns"])
    for column in NUMERIC_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["Gender"] = frame["Gender"].astype(str).str.upper()
    return frame.dropna(subset=NUMERIC_COLUMNS).reset_index(drop=True)


@st.cache_data
def fit_model(frame: pd.DataFrame) -> dict:
    x = frame[MODEL_FEATURES].to_numpy(dtype=float)
    y = frame["Exam_Score"].to_numpy(dtype=float)
    means = x.mean(axis=0)
    stds = x.std(axis=0)
    stds[stds == 0] = 1
    z = (x - means) / stds
    design = np.column_stack((np.ones(len(z)), z))
    beta = np.linalg.lstsq(design, y, rcond=None)[0]
    prediction = design @ beta
    total = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - float(np.sum((y - prediction) ** 2)) / total if total else 0.0
    return {
        "intercept": float(beta[0]),
        "coefficients": dict(zip(MODEL_FEATURES, beta[1:].tolist())),
        "means": dict(zip(MODEL_FEATURES, means.tolist())),
        "stds": dict(zip(MODEL_FEATURES, stds.tolist())),
        "r2": r2,
    }


def grade(score: float) -> str:
    if score >= 85:
        return "A"
    if score >= 75:
        return "B"
    if score >= 65:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def score_prediction(values: dict[str, float], model: dict) -> tuple[float, list[str]]:
    terms = []
    result = model["intercept"]
    for feature in MODEL_FEATURES:
        value = values[feature]
        mean = model["means"][feature]
        std = model["stds"][feature]
        coefficient = model["coefficients"][feature]
        z_score = (value - mean) / std
        contribution = z_score * coefficient
        result += contribution
        terms.append(
            f"{feature}: ({value:g} − {mean:.2f}) / {std:.2f} × "
            f"{coefficient:.2f} = {contribution:+.2f}"
        )
    return float(np.clip(result, 0, 100)), terms


def correlation(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[NUMERIC_COLUMNS].corr().fillna(0)


def main() -> None:
    data = load_data()
    model = fit_model(data)

    st.title("📊 Executive BI Dashboard")
    st.caption("Student performance · Descriptive statistics · Predictive analytics")

    with st.sidebar:
        st.header("Dashboard")
        gender = st.selectbox("Filter gender", ["Semua", "Female (F)", "Male (M)"])
        st.divider()
        st.caption("Data dimuat dari `latihan1.json` yang disertakan bersama aplikasi.")

    selected_gender = {"Semua": None, "Female (F)": "F", "Male (M)": "M"}[gender]
    view = data if selected_gender is None else data[data["Gender"] == selected_gender]

    if view.empty:
        st.warning("Tidak ada siswa untuk filter ini.")
        return

    avg_score = float(view["Exam_Score"].mean())
    risk_count = int((view["Exam_Score"] < 60).sum())
    corr = correlation(view)
    ranked = corr["Exam_Score"].drop("Exam_Score").sort_values(key=lambda s: s.abs(), ascending=False)
    top_factor = ranked.index[0]
    st.info(
        f"Rata-rata nilai adalah **{avg_score:.1f}** dari **{len(view)} siswa**. "
        f"Hubungan terkuat dengan Exam Score terlihat pada **{top_factor}** "
        f"(korelasi {ranked.iloc[0]:+.2f}). Ada **{risk_count} siswa** dengan nilai di bawah 60."
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Rata-rata Exam Score", f"{avg_score:.1f}", "dari 100")
    k2.metric("Rata-rata Study Hours", f"{view['Study_Hours'].mean():.1f} jam")
    k3.metric("Rata-rata Attendance", f"{view['Attendance'].mean():.1f}%")
    k4.metric("Butuh Intervensi", risk_count, f"dari {len(view)} siswa")

    st.divider()
    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("What-If Simulator")
        st.caption("Geser nilai untuk memperkirakan Exam Score dari model OLS dataset.")
        defaults = {
            "Study_Hours": float(data["Study_Hours"].mean()),
            "Attendance": float(data["Attendance"].mean()),
            "Sleep_Hours": float(data["Sleep_Hours"].mean()),
            "Screen_Hours": float(data["Screen_Hours"].mean()),
        }
        limits = {"Study_Hours": (0.0, 18.0, 0.5), "Attendance": (0.0, 100.0, 1.0),
                  "Sleep_Hours": (0.0, 12.0, 0.5), "Screen_Hours": (0.0, 16.0, 0.5)}
        labels = {"Study_Hours": "Study Hours", "Attendance": "Attendance (%)",
                  "Sleep_Hours": "Sleep Hours", "Screen_Hours": "Screen Hours"}
        values = {}
        for feature in MODEL_FEATURES:
            low, high, step = limits[feature]
            values[feature] = st.slider(labels[feature], low, high, float(np.clip(defaults[feature], low, high)), step=step)

        estimate, terms = score_prediction(values, model)
        st.metric("Estimasi Exam Score", f"{estimate:.1f} / 100", f"Grade {grade(estimate)}")
        with st.expander("Behind the Scenes · lihat rincian OLS"):
            st.latex(r"\hat{y} = \beta_0 + \sum_j \beta_j \left(\frac{x_j-\mu_j}{\sigma_j}\right)")
            st.write(f"Intercept (β₀): **{model['intercept']:.2f}**")
            for line in terms:
                st.code(line, language=None)
            st.caption(f"R² pada data yang tersedia: {model['r2'] * 100:.2f}%. R² dihitung dari dataset; nilainya dapat berubah jika data berubah.")

    with right:
        st.subheader("Radar Profil Gender")
        st.caption("Setiap sumbu dinormalisasi ke skala 0–100 agar metrik dengan satuan berbeda bisa dibandingkan.")
        radar = go.Figure()
        for code, label, color in [("F", "Female (F)", "#38bdf8"), ("M", "Male (M)", "#f472b6")]:
            group = data[data["Gender"] == code]
            if group.empty:
                continue
            values_radar = [group[c].mean() / RADAR_LIMITS[c] * 100 for c in RADAR_COLUMNS]
            radar.add_trace(go.Scatterpolar(r=values_radar, theta=RADAR_COLUMNS, fill="toself", name=label,
                                            line={"color": color}, opacity=0.78))
        radar.update_layout(template="plotly_dark", height=360, margin={"l": 35, "r": 35, "t": 20, "b": 20},
                            polar={"radialaxis": {"visible": True, "range": [0, 100]}})
        st.plotly_chart(radar, use_container_width=True)

    st.divider()
    st.subheader("Analisis Faktor Korelasi Target")
    controls = st.columns(2)
    with controls[0]:
        target = st.selectbox("Target (Y)", NUMERIC_COLUMNS, index=NUMERIC_COLUMNS.index("Exam_Score"))
    factors = [c for c in NUMERIC_COLUMNS if c != target]
    with controls[1]:
        factor = st.selectbox("Faktor (X) untuk scatter plot", factors,
                              index=factors.index("Study_Hours") if "Study_Hours" in factors else 0)
    selected_corr = view[NUMERIC_COLUMNS].corr()[target].drop(target).sort_values(key=lambda s: s.abs(), ascending=True)
    bar = px.bar(x=selected_corr.values, y=selected_corr.index, orientation="h", color=selected_corr.values,
                 color_continuous_scale=["#fb7185", "#334155", "#34d399"], range_color=[-1, 1],
                 labels={"x": f"Korelasi dengan {target}", "y": "Faktor"}, template="plotly_dark")
    bar.update_layout(height=350, coloraxis_showscale=False, xaxis={"range": [-1, 1]})
    scatter = px.scatter(view, x=factor, y=target, color="Gender", hover_data=["Student_ID"],
                         template="plotly_dark", labels={factor: factor, target: target})
    scatter.update_layout(height=350)
    c1, c2 = st.columns(2, gap="large")
    c1.plotly_chart(bar, use_container_width=True)
    c2.plotly_chart(scatter, use_container_width=True)

    st.divider()
    st.subheader("Matriks Korelasi")
    st.caption("Pearson correlation: hijau menunjukkan hubungan positif, merah menunjukkan hubungan negatif.")
    heat = px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale="RdYlGn",
                     aspect="auto", template="plotly_dark", labels={"color": "Korelasi"})
    heat.update_layout(height=560, margin={"l": 10, "r": 10, "t": 20, "b": 10})
    st.plotly_chart(heat, use_container_width=True)

    st.divider()
    st.subheader("Data Siswa")
    query = st.text_input("Cari di semua kolom", placeholder="Contoh: F, 78, atau ID siswa")
    shown = view.copy()
    if query.strip():
        mask = shown.astype(str).apply(lambda column: column.str.contains(query, case=False, regex=False)).any(axis=1)
        shown = shown[mask]
    st.caption(f"Menampilkan {len(shown)} dari {len(view)} siswa.")
    st.dataframe(shown, use_container_width=True, hide_index=True)
    csv_bytes = shown.to_csv(index=False).encode("utf-8-sig")
    st.download_button("Unduh data sebagai CSV", csv_bytes, file_name="student_data.csv", mime="text/csv")


if __name__ == "__main__":
    main()
