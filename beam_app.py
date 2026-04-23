import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- PAGE CONFIG ---
st.set_page_config(page_title="Beam Analysis App", layout="wide")

# --- TITLE ---
st.title("🏗️ Beam Analysis Calculator")
st.markdown("Analyze beam behavior including **shear force**, **bending moment**, and **deflection**.")

# --- SIDEBAR INPUTS ---
st.sidebar.header("Input Parameters")

beam_type = st.sidebar.selectbox(
    "Beam Type",
    ["Simply Supported Beam", "Cantilever Beam"]
)

load_type = st.sidebar.selectbox(
    "Load Type",
    ["Point Load", "Uniformly Distributed Load (UDL)"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Geometry")

L = st.sidebar.number_input("Beam Length L (meters)", min_value=0.1, value=5.0)

st.sidebar.markdown("---")
st.sidebar.subheader("Material Properties")

E = st.sidebar.number_input(
    "Modulus of Elasticity E (Pa)",
    min_value=1.0,
    value=200e9,
    format="%.2e",
    help="Material stiffness (e.g., Steel ≈ 200 GPa)"
)

I = st.sidebar.number_input(
    "Moment of Inertia I (m⁴)",
    min_value=1e-9,
    value=1e-6,
    format="%.2e",
    help="Cross-sectional resistance to bending"
)

st.sidebar.markdown("---")
st.sidebar.subheader("Loading")

if load_type == "Point Load":
    P = st.sidebar.number_input("Point Load P (Newtons)", min_value=1.0, value=1000.0)
    a = st.sidebar.number_input("Load Position a (meters from left)", min_value=0.0, max_value=L, value=L/2)
else:
    w = st.sidebar.number_input("Uniform Load w (N/m)", min_value=1.0, value=500.0)

# --- DESCRIPTION SECTION ---
st.markdown("### 📘 Variable Definitions")
st.info("""
- **L (Length):** Total length of the beam  
- **E (Modulus of Elasticity):** Measures how stiff the material is  
- **I (Moment of Inertia):** Describes how the beam's cross-section resists bending  
- **P (Point Load):** Concentrated force applied at one location  
- **w (Distributed Load):** Force spread evenly across the beam  
""")

# --- CALCULATIONS ---
x = np.linspace(0, L, 200)

if beam_type == "Simply Supported Beam" and load_type == "Point Load":
    R1 = P * (L - a) / L
    V = np.where(x < a, R1, R1 - P)
    M = np.where(x < a, R1 * x, R1 * x - P * (x - a))
    delta_max = (P * a * (L**2 - a**2)**1.5) / (9 * np.sqrt(3) * E * I * L)

elif beam_type == "Simply Supported Beam" and load_type == "Uniformly Distributed Load (UDL)":
    V = w * (L/2 - x)
    M = (w/2) * (L*x - x**2)
    delta_max = (5 * w * L**4) / (384 * E * I)

elif beam_type == "Cantilever Beam" and load_type == "Point Load":
    V = np.where(x < L, P, 0)
    M = P * (L - x)
    delta_max = (P * L**3) / (3 * E * I)

elif beam_type == "Cantilever Beam" and load_type == "Uniformly Distributed Load (UDL)":
    V = w * (L - x)
    M = (w/2) * (L - x)**2
    delta_max = (w * L**4) / (8 * E * I)

# --- RESULTS ---
st.markdown("## 📊 Results")

col1, col2 = st.columns(2)

with col1:
    st.metric("Maximum Deflection (meters)", f"{delta_max:.6e}")

with col2:
    st.metric("Beam Length (meters)", f"{L:.2f}")

# --- PLOTS ---
st.markdown("## 📈 Diagrams")

fig, ax = plt.subplots(2, 1, figsize=(8, 6))

# Shear
ax[0].plot(x, V)
ax[0].set_title("Shear Force Diagram")
ax[0].set_xlabel("Position along beam (m)")
ax[0].set_ylabel("Shear Force (N)")
ax[0].grid()

# Moment
ax[1].plot(x, M)
ax[1].set_title("Bending Moment Diagram")
ax[1].set_xlabel("Position along beam (m)")
ax[1].set_ylabel("Moment (N·m)")
ax[1].grid()

st.pyplot(fig)

# --- FOOTER ---
st.markdown("---")
st.caption("Developed for CE Engineering Analysis | Beam Calculator Tool")