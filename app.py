import streamlit as st
import numpy as np
import time

st.set_page_config(
    page_title="Predictive Maintenance",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
.stApp { background-color: #1e2128 !important; color: #d4dbe8 !important; font-family: 'Inter', sans-serif !important; }
header[data-testid="stHeader"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

div[data-testid="stNumberInput"] label { display: none !important; }
div[data-testid="stNumberInput"] input {
    background: #2a2d35 !important;
    border: 1px solid #3d4350 !important;
    border-radius: 6px 0 0 6px !important;
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    text-align: center !important;
}
div[data-testid="stNumberInput"] input:focus {
    border-color: #6c63ff !important;
    box-shadow: 0 0 0 2px rgba(108,99,255,0.25) !important;
    outline: none !important;
}
div[data-testid="stNumberInput"] button {
    background: #3a3d4a !important;
    border: 1px solid #3d4350 !important;
    color: #c8d0de !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    width: 36px !important;
    min-width: 36px !important;
    height: 100% !important;
    cursor: pointer !important;
    transition: background .15s ease !important;
}
div[data-testid="stNumberInput"] button:hover {
    background: #6c63ff !important;
    border-color: #6c63ff !important;
    color: #fff !important;
}

.stButton > button {
    background: transparent !important;
    border: 1px solid #4a4f5c !important;
    border-radius: 8px !important;
    color: #8a95a5 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    padding: 10px 28px !important;
}
.stButton > button:hover { background: #6c63ff !important; border-color: #6c63ff !important; color: #fff !important; }

/* Nav pill aktif */
.nav-active {
    background: #6c63ff;
    border: 1px solid #6c63ff;
    padding: 6px 18px;
    border-radius: 6px;
    display: inline-block;
}
.nav-inactive {
    background: transparent;
    border: 1px solid transparent;
    padding: 6px 18px;
    border-radius: 6px;
    display: inline-block;
}

#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── dummy model ──
def predict_rul(a, b, c, d, e, f):
    base = 200
    p  = (a - 1400) * 0.05
    p += (b - 1300) * 0.04
    p += max(0, c - 8000) * 0.002
    p += max(0, d - 40)   * 0.3
    p += max(0, e - 400)  * 0.1
    p += max(0, f - 7000) * 0.003
    return round(max(0, base - p + np.random.normal(0, 2)), 1)

def health_label(rul):
    if rul >= 100: return "BAIK",    "#22c55e", 1.0
    if rul >= 50:  return "WASPADA", "#f59e0b", rul / 100
    return              "KRITIS",   "#ef4444", rul / 100

# ── session state ──
for k, v in dict(suhu_hpc=1589.0, suhu_lpt=1400.0,
                 rasio_tekanan=9046.0, tekanan_ruang=47.4,
                 rasio_bbm=521.6, kecepatan_poros=8138.0, result=None).items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── TOP BAR ──
st.markdown("""
<div style="background:#3b3580;border-bottom:1px solid #2d2870;padding:14px 28px;
            display:flex;align-items:center;justify-content:space-between;">
  <div style="display:flex;align-items:center;gap:24px;">
    <span style="font-size:17px;font-weight:700;color:#fff;font-family:'Inter',sans-serif;">
      ⚙️&nbsp; Predictive Maintenance
    </span>
    <span style="font-size:11px;color:#a89fe8;font-family:'JetBrains Mono',monospace;">
      ANN Regression Engine · Estimasi sisa umur katup mesin
    </span>
  </div>
  <div style="display:flex;align-items:center;gap:12px;">
    <span style="font-size:11px;color:#a89fe8;font-family:'JetBrains Mono',monospace;">MODEL v2.1</span>
    <span style="background:#5b52c8;color:#fff;font-size:11px;font-weight:600;
                 padding:3px 14px;border-radius:20px;border:1px solid #7c74e8;">● Live</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── 2 KOLOM UTAMA ──
inp_col, res_col = st.columns([2.2, 1.4])

# ── INPUT PANEL ──
with inp_col:
    st.markdown("""
    <div style="padding:12px 8px 10px;">
      <span style="font-size:10px;letter-spacing:.14em;color:#565e70;
                   font-family:'JetBrains Mono',monospace;font-weight:600;">
        // INPUT SENSOR TELEMETRI
      </span>
    </div>""", unsafe_allow_html=True)

    sensors = [
        ("suhu_hpc",        "Suhu HPC",           "HP Compressor outlet",   "°C",  "1589.0"),
        ("suhu_lpt",        "Suhu LPT",            "LP Turbine outlet",      "°C",  "1400.0"),
        ("rasio_tekanan",   "Rasio tekanan",        "Overall pressure ratio", "",    "9046.0"),
        ("tekanan_ruang",   "Tekanan ruang bakar",  "Combustion chamber",     "",    "47.4"),
        ("rasio_bbm",       "Rasio aliran BBM",     "Fuel flow to pressure",  "",    "521.6"),
        ("kecepatan_poros", "Kecepatan poros",      "Core shaft speed",       "",    "8138.0"),
    ]

    for i in range(0, len(sensors), 2):
        c1, c2 = st.columns(2, gap="medium")
        for col, (key, title, sub, unit, default) in zip([c1, c2], sensors[i:i+2]):
            with col:
                with st.container():
                    t1, t2 = st.columns([3, 1])
                    with t1:
                        st.markdown(
                            f"<p style='margin:8px 0 0 0;font-size:13px;font-weight:600;"
                            f"color:#c8d0de;font-family:Inter,sans-serif;'>◻ {title}</p>",
                            unsafe_allow_html=True,
                        )
                    with t2:
                        if unit:
                            st.markdown(
                                f"<p style='margin:8px 0 0 0;font-size:10px;color:#8a95a5;"
                                f"font-family:JetBrains Mono,monospace;text-align:right;'>{unit}</p>",
                                unsafe_allow_html=True,
                            )
                    st.caption(sub)
                    st.number_input(
                        label=title,
                        key=key,
                        value=float(default),
                        format="%.1f",
                        step=1.0,
                        label_visibility="collapsed",
                    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    _, bc, __ = st.columns([0.01, 0.42, 0.57])
    with bc:
        if st.button("◻  Analisis sekarang"):
            with st.spinner("Menghitung…"):
                time.sleep(0.4)
            st.session_state.result = predict_rul(
                st.session_state.suhu_hpc, st.session_state.suhu_lpt,
                st.session_state.rasio_tekanan, st.session_state.tekanan_ruang,
                st.session_state.rasio_bbm, st.session_state.kecepatan_poros,
            )

# ── RESULT PANEL ──
with res_col:
    st.markdown("""
    <div style="padding:12px 8px 10px;">
      <span style="font-size:10px;letter-spacing:.14em;color:#565e70;
                   font-family:'JetBrains Mono',monospace;font-weight:600;">
        // HASIL PREDIKSI
      </span>
    </div>""", unsafe_allow_html=True)

    if st.session_state.result is None:
        st.markdown("""
        <div style="margin:20px 8px 0;background:#252830;border:1px dashed #2d3139;
                    border-radius:10px;padding:56px 20px;text-align:center;">
          <div style="font-size:30px;opacity:.3;margin-bottom:12px;">📊</div>
          <div style="font-size:11px;color:#565e70;line-height:1.7;">
            Atur nilai sensor lalu tekan<br>
            <span style="color:#6c63ff;font-weight:600;">Analisis sekarang</span>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        rul = st.session_state.result
        lbl, clr, ratio = health_label(rul)
        bw = int(ratio * 100)

        rows = "".join(
            f"<div style='display:flex;justify-content:space-between;padding:5px 0;"
            f"border-bottom:1px solid #2d3139;'>"
            f"<span style='font-size:11px;color:#565e70;font-family:JetBrains Mono,monospace;'>{k}</span>"
            f"<span style='font-size:11px;color:#c8d0de;font-weight:600;font-family:JetBrains Mono,monospace;'>{v}</span>"
            f"</div>"
            for k, v in [
                ("T_HPC",   f"{st.session_state.suhu_hpc:.1f} °C"),
                ("T_LPT",   f"{st.session_state.suhu_lpt:.1f} °C"),
                ("P_ratio", f"{st.session_state.rasio_tekanan:.1f}"),
                ("P_comb",  f"{st.session_state.tekanan_ruang:.1f}"),
                ("FF/P",    f"{st.session_state.rasio_bbm:.1f}"),
                ("N_core",  f"{st.session_state.kecepatan_poros:.1f}"),
            ]
        )

        st.markdown(
            f"<div style='margin:0 8px;'>"
            f"<div style='background:#252830;border:1px solid #2d3139;border-radius:10px;"
            f"padding:20px 18px;margin-bottom:12px;'>"
            f"<div style='font-size:10px;letter-spacing:.1em;color:#565e70;"
            f"font-family:JetBrains Mono,monospace;margin-bottom:8px;'>ESTIMASI SISA UMUR (RUL)</div>"
            f"<div style='display:flex;align-items:baseline;gap:8px;'>"
            f"<span style='font-size:44px;font-weight:700;color:{clr};"
            f"font-family:JetBrains Mono,monospace;line-height:1;'>{rul}</span>"
            f"<span style='font-size:13px;color:#8a95a5;'>siklus</span></div>"
            f"<div style='background:#1e2128;border-radius:4px;height:6px;margin:14px 0 8px;overflow:hidden;'>"
            f"<div style='background:{clr};width:{bw}%;height:100%;border-radius:4px;'></div></div>"
            f"<div style='display:flex;justify-content:space-between;align-items:center;'>"
            f"<span style='font-size:10px;color:#565e70;'>Kondisi mesin</span>"
            f"<span style='background:{clr}22;color:{clr};font-size:10px;font-weight:700;"
            f"padding:2px 10px;border-radius:20px;font-family:JetBrains Mono,monospace;'>{lbl}</span>"
            f"</div></div>"
            f"<div style='background:#252830;border:1px solid #2d3139;border-radius:10px;padding:14px 16px;'>"
            f"<div style='font-size:10px;letter-spacing:.1em;color:#565e70;"
            f"font-family:JetBrains Mono,monospace;margin-bottom:10px;'>NILAI SENSOR INPUT</div>"
            f"{rows}</div></div>",
            unsafe_allow_html=True
        )

# ── FOOTER ──
st.markdown("""
<div style="border-top:1px solid #2d3139;padding:10px 28px;text-align:center;margin-top:20px;">
  <span style="font-size:10px;color:#3d4350;font-family:'JetBrains Mono',monospace;letter-spacing:.1em;">
    PROJECT SC 2026 · PREDICTIVE MAINTENANCE SYSTEM
  </span>
</div>""", unsafe_allow_html=True)
