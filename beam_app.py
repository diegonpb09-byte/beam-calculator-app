import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- PAGE CONFIG ---
st.set_page_config(page_title="Beam Analysis App", layout="wide")

# --- TITLE ---
st.title("🏗️ Beam Analysis Calculator")
st.markdown("""
<div style="
    background-color:#f0f2f6;
    padding:10px;
    border-radius:10px;
    margin-bottom:15px;
    color:black;
">
<b>Developed by:</b> Diego Pulido<br>
<b>Course:</b> CE2070.02<br>
<b>Assignment:</b> Final Project
</div>
""", unsafe_allow_html=True)
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

# --- VARIABLE EXPLANATION ---
st.markdown("### 📘 Variable Definitions")
st.info("""
- **L (Length):** Total length of the beam  
- **E (Modulus of Elasticity):** Measures material stiffness  
- **I (Moment of Inertia):** Resistance of the cross-section to bending  
- **P (Point Load):** Concentrated force applied at one point  
- **w (Distributed Load):** Load spread evenly along the beam  
""")

# --- BEAM DIAGRAM FUNCTION ---
def draw_beam_diagram(beam_type, load_type, L, load, a=None):
    fig, ax = plt.subplots(figsize=(10,3))

    # --- Beam line ---
    ax.plot([0, L], [0, 0], linewidth=6)

    # --- SUPPORTS + REACTIONS ---
    if beam_type == "Simply Supported Beam":
        # Supports
        ax.plot(0, 0, marker="^", markersize=12)
        ax.text(0, -0.5, "Pin", ha='center')

        ax.plot(L, 0, marker="o", markersize=10)
        ax.text(L, -0.5, "Roller", ha='center')

        # Reactions
        if load_type == "Point Load":
            R1 = load * (L - a) / L
            R2 = load * a / L
        else:  # UDL
            R1 = R2 = load * L / 2

        # Reaction arrows
        ax.arrow(0, -0.2, 0, 0.8, head_width=0.2, head_length=0.2, color='green')
        ax.text(0, 0.9, f"R₁ = {R1:.0f} N", ha='center', color='green')

        ax.arrow(L, -0.2, 0, 0.8, head_width=0.2, head_length=0.2, color='green')
        ax.text(L, 0.9, f"R₂ = {R2:.0f} N", ha='center', color='green')

    else:  # Cantilever
        ax.plot(0, 0, marker="s", markersize=12)
        ax.text(0, -0.5, "Fixed Support", ha='center')

        # Reaction force at wall
        if load_type == "Point Load":
            R = load
        else:
            R = load * L

        ax.arrow(0, -0.2, 0, 0.8, head_width=0.2, head_length=0.2, color='green')
        ax.text(0, 0.9, f"R = {R:.0f} N", ha='center', color='green')

    # --- LOADS ---
    if load_type == "Point Load":
        ax.arrow(a, 1.2, 0, -1, head_width=0.2, head_length=0.3)
        ax.text(a, 1.5, f"P = {load:.0f} N", ha='center')

    else:
        for i in np.linspace(0, L, 12):
            ax.arrow(i, 1.2, 0, -1, head_width=0.15, head_length=0.2)
        ax.text(L/2, 1.5, f"w = {load:.0f} N/m", ha='center')

    # --- LENGTH DIMENSION ---
    ax.annotate(
        "",
        xy=(0, -1.2),
        xytext=(L, -1.2),
        arrowprops=dict(arrowstyle="<->")
    )
    ax.text(L/2, -1.5, f"L = {L:.2f} m", ha='center')

    # --- FORMATTING ---
    ax.set_xlim(-1, L+1)
    ax.set_ylim(-2, 2)
    ax.set_title("Beam Free Body Diagram", pad=15)
    ax.axis('off')

    return fig

# --- CALCULATIONS ---
x = np.linspace(0, L, 500)

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

# --- FIND MAX VALUES ---
max_shear = np.max(np.abs(V))
max_shear_index = np.argmax(np.abs(V))

max_moment = np.max(np.abs(M))
max_moment_index = np.argmax(np.abs(M))

# --- RESULTS ---
st.markdown("## 📊 Results")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Max Deflection (m)", f"{delta_max:.3e}")

with col2:
    st.metric("Max Shear (N)", f"{max_shear:.2f}")

with col3:
    st.metric("Max Moment (N·m)", f"{max_moment:.2f}")

# --- BEAM DIAGRAM ---
st.markdown("## 🏗️ Beam Diagram")

if load_type == "Point Load":
    fig_beam = draw_beam_diagram(beam_type, load_type, L, P, a)
else:
    fig_beam = draw_beam_diagram(beam_type, load_type, L, w)

st.pyplot(fig_beam)

# --- PLOTS ---
st.markdown("## 📈 Shear Force & Bending Moment Diagrams")

fig, ax = plt.subplots(2, 1, figsize=(10, 8))

# SHEAR
ax[0].plot(x, V)
ax[0].scatter(x[max_shear_index], V[max_shear_index])

# Dynamic offset
y_offset_shear = -30 if V[max_shear_index] > 0 else 30

ax[0].annotate(
    f"Max = {max_shear:.2f} N",
    (x[max_shear_index], V[max_shear_index]),
    textcoords="offset points",
    xytext=(10, y_offset_shear),
    ha='left',
    bbox=dict(boxstyle="round,pad=0.3")
)
ax[0].set_title("Shear Force Diagram", pad=15)
ax[0].set_xlabel("Position (m)")
ax[0].set_ylabel("Shear (N)")
ax[0].grid()

# MOMENT
ax[1].plot(x, M)
ax[1].scatter(x[max_moment_index], M[max_moment_index])

# Dynamic offset to avoid overlap with title
y_offset = -30 if M[max_moment_index] > 0 else 30

ax[1].annotate(
    f"Max = {max_moment:.2f} N·m",
    (x[max_moment_index], M[max_moment_index]),
    textcoords="offset points",
    xytext=(10, y_offset),
    ha='left',
    bbox=dict(boxstyle="round,pad=0.3")
)
ax[1].set_title("Bending Moment Diagram", pad=15)
ax[1].set_xlabel("Position (m)")
ax[1].set_ylabel("Moment (N·m)")
ax[1].grid()

plt.tight_layout(pad=3.0)
st.pyplot(fig)

# --- FOOTER ---
st.markdown("---")
st.caption("Developed for Civil Engineering Beam Analysis | Streamlit App")
