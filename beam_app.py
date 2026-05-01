import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==============================
# PAGE SETUP
# ==============================
st.set_page_config(page_title="Beam Analysis Tool", layout="wide")

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h2 style='margin-bottom:0;'>Beam Analysis Tool</h2>
<p style='margin-top:0; font-size:14px; opacity:0.7;'>
Interactive structural analysis for beams
</p>
<hr>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    padding:10px;
    border-radius:10px;
    margin-bottom:15px;
    border: 1px solid rgba(150,150,150,0.3);
    background-color: transparent;
">
<b>Developed by:</b> Diego Pulido<br>
<b>Course:</b> CE2070.02<br>
<b>Assignment:</b> Final Project
</div>
""", unsafe_allow_html=True)

# ==============================
# SIDEBAR INPUTS
# ==============================
st.markdown("## 🔧 Inputs")
st.markdown("Define beam geometry, material properties, and loading conditions.")
st.sidebar.header("🔧 Beam Settings")

beam_type = st.sidebar.selectbox(
    "Beam Type",
    ["Simply Supported", "Cantilever"]
)

L = st.sidebar.number_input("Beam Length (m)", 1.0, 100.0, 10.0)
E = st.sidebar.number_input("Elastic Modulus E (Pa)", value=200e9, format="%.2e")
I = st.sidebar.number_input("Moment of Inertia I (m⁴)", value=1e-6, format="%.2e")

# ==============================
# LOADS
# ==============================
st.sidebar.header("📦 Loads")

num_loads = st.sidebar.number_input("Number of Loads", 1, 5, 1)
loads = []

for i in range(int(num_loads)):
    st.sidebar.markdown(f"### Load {i+1}")

    load_type = st.sidebar.selectbox(
        "Type", ["Point Load", "UDL"], key=f"type_{i}"
    )

    if load_type == "Point Load":
        P = st.sidebar.number_input(f"P{i+1} (N)", key=f"P_{i}")
        a = st.sidebar.number_input(f"Position {i+1} (m)", 0.0, L, key=f"a_{i}")
        loads.append(("point", P, a))
    else:
        w = st.sidebar.number_input(f"w{i+1} (N/m)", key=f"w_{i}")
        a = st.sidebar.number_input(f"Start {i+1}", 0.0, L, key=f"start_{i}")
        b = st.sidebar.number_input(f"End {i+1}", 0.0, L, key=f"end_{i}")
        loads.append(("udl", w, a, b))

# ==============================
# EXTERNAL MOMENT
# ==============================
st.sidebar.header("🔄 External Moment")

moment_value = st.sidebar.number_input("Moment (N·m)", value=0.0)
moment_pos = st.sidebar.number_input("Position (m)", 0.0, L, L/2)

# ==============================
# DISCRETIZATION
# ==============================
x = np.linspace(0, L, 800)
dx = x[1] - x[0]

V = np.zeros_like(x)
M = np.zeros_like(x)

# ==============================
# REACTIONS
# ==============================
total_force = 0
total_moment = 0

for load in loads:
    if load[0] == "point":
        P, a = load[1], load[2]
        total_force += P
        total_moment += P * a
    else:
        w, a, b = load[1], load[2], load[3]
        W = w * (b - a)
        centroid = (a + b) / 2
        total_force += W
        total_moment += W * centroid

if beam_type == "Simply Supported":
    R2 = total_moment / L
    R1 = total_force - R2
    V += R1
    M += R1 * x
else:
    R1 = total_force
    M_fixed = total_moment
    V += R1
    M += R1 * x - M_fixed

# ==============================
# SUPERPOSITION
# ==============================
for load in loads:

    if load[0] == "point":
        P, a = load[1], load[2]
        V += np.where(x >= a, -P, 0)
        M += np.where(x >= a, -P * (x - a), 0)

    else:
        w, a, b = load[1], load[2], load[3]

        for i in range(len(x)):
            xi = x[i]

            if xi < a:
                continue
            elif a <= xi <= b:
                V[i] -= w * (xi - a)
                M[i] -= w * (xi - a)**2 / 2
            else:
                V[i] -= w * (b - a)
                M[i] -= w * (b - a) * (xi - (a + b)/2)

# External moment
M += np.where(x >= moment_pos, moment_value, 0)

# ==============================
# DEFLECTION
# ==============================
curvature = M / (E * I)
slope = np.cumsum(curvature) * dx
deflection = np.cumsum(slope) * dx

if beam_type == "Simply Supported":
    deflection -= np.linspace(deflection[0], deflection[-1], len(deflection))
else:
    deflection -= deflection[0]
    slope -= slope[0]
    deflection = np.cumsum(slope) * dx

# ==============================
# RESULTS
# ==============================
st.markdown("## 📊 Results")
st.markdown("Key response values for the selected beam configuration.")

col1, col2, col3 = st.columns(3)

col1.metric("Max Shear (N)", f"{np.max(np.abs(V)):.2f}")
col2.metric("Max Moment (N·m)", f"{np.max(np.abs(M)):.2f}")
col3.metric("Max Deflection (m)", f"{np.max(np.abs(deflection)):.6e}")

with st.expander("🔍 View Detailed Inputs"):
    st.write("Beam Length (m):", L)
    st.write("Elastic Modulus (Pa):", E)
    st.write("Moment of Inertia (m⁴):", I)
    st.write("Loads:", loads)
    st.write("External Moment:", moment_value)
# ==============================
# POLISHED FBD (FIXED)
# ==============================
st.markdown("## 🏗️ Free Body Diagram")
st.markdown("Visual representation of supports, loads, and reactions.")

fig_fbd, ax = plt.subplots(figsize=(10,3))

# Beam line
ax.plot([0, L], [0, 0], linewidth=6)

# Supports
if beam_type == "Simply Supported":
    ax.plot(0, 0, marker="^", markersize=12)
    ax.plot(L, 0, marker="o", markersize=10)
else:
    ax.plot(0, 0, marker="s", markersize=12)

# --- REACTIONS ---
ax.arrow(0, -0.1, 0, 0.8,
         head_width=0.2, head_length=0.2, length_includes_head=True)
ax.text(0, 1.0, f"R1={R1:.0f}", ha='center')

if beam_type == "Simply Supported":
    ax.arrow(L, -0.1, 0, 0.8,
             head_width=0.2, head_length=0.2, length_includes_head=True)
    ax.text(L, 1.0, f"R2={R2:.0f}", ha='center')

# --- LOADS (OFFSET ABOVE BEAM, CLEAN) ---
for load in loads:
    if load[0] == "point":
        _, P, a = load
        ax.arrow(a, 1.5, 0, -1.0,
                 head_width=0.2, head_length=0.2, length_includes_head=True)
        ax.text(a, 1.7, f"P={P:.0f}", ha='center')

    else:
        _, w, a, b = load
        for xi in np.linspace(a, b, 8):
            ax.arrow(xi, 1.5, 0, -1.0,
                     head_width=0.15, head_length=0.15, length_includes_head=True)
        ax.text((a+b)/2, 1.7, f"w={w:.0f}", ha='center')

# --- MOMENT (ON BEAM, LABEL BELOW) ---
if moment_value != 0:
    theta = np.linspace(0, np.pi, 50)

    r = 0.45
    y_center = -0.05   # slight shift BELOW beam so it visually sits on it

    # Draw arc
    ax.plot(
        moment_pos + r * np.cos(theta),
        y_center + r * np.sin(theta),
        linewidth=2
    )

    # Arrow head at end of arc
    ax.arrow(
        moment_pos + r*np.cos(theta[-2]),
        y_center + r*np.sin(theta[-2]),
        0.001, 0.001,
        head_width=0.12,
        head_length=0.12,
        length_includes_head=True
    )

    # Label BELOW the beam
    ax.text(
        moment_pos,
        y_center - 0.5,
        f"M = {moment_value:.0f} N·m",
        ha='center'
    )
# ==============================
# BEAM SCALE (TICKS + LABELS)
# ==============================

# Choose number of ticks (adjust if you want more/less)
num_ticks = 6

tick_positions = np.linspace(0, L, num_ticks)

for pos in tick_positions:
    # Draw small vertical tick
    ax.plot([pos, pos], [0, -0.15], color='black', linewidth=1)

    # Add label below beam
    ax.text(pos, -0.35, f"{pos:.1f}", ha='center', fontsize=8)

# --- FORMATTING ---
ax.set_xlim(-0.5, L + 0.5)
ax.set_ylim(-1.0, 2.0)   # THIS fixes scaling issues
ax.set_title("Free Body Diagram", pad=10)
ax.axis('off')

st.pyplot(fig_fbd)

# ==============================
# DIAGRAMS WITH MAX HIGHLIGHTING
# ==============================
st.markdown("## 📈 Analysis Diagrams")
st.markdown("Shear force, bending moment, and deflection along the beam.")

fig, ax = plt.subplots(3, 1, figsize=(10,10))

# --- FIND MAX INDICES ---
max_shear_idx = np.argmax(np.abs(V))
max_moment_idx = np.argmax(np.abs(M))
max_deflection_idx = np.argmax(np.abs(deflection))


# ==============================
# SHEAR FORCE DIAGRAM
# ==============================
ax[0].plot(x, V)
ax[0].scatter(x[max_shear_idx], V[max_shear_idx])

y_offset_shear = -30 if V[max_shear_idx] > 0 else 30

ax[0].annotate(
    f"Max = {np.max(np.abs(V)):.2f} N",
    (x[max_shear_idx], V[max_shear_idx]),
    textcoords="offset points",
    xytext=(10, y_offset_shear),
    bbox=dict(boxstyle="round,pad=0.3")
)

ax[0].set_title("Shear Force Diagram", pad=15)
ax[0].set_xlabel("Position (m)")
ax[0].set_ylabel("Shear (N)")
ax[0].grid()


# ==============================
# BENDING MOMENT DIAGRAM
# ==============================
ax[1].plot(x, M)
ax[1].scatter(x[max_moment_idx], M[max_moment_idx])

y_offset_moment = -30 if M[max_moment_idx] > 0 else 30

ax[1].annotate(
    f"Max = {np.max(np.abs(M)):.2f} N·m",
    (x[max_moment_idx], M[max_moment_idx]),
    textcoords="offset points",
    xytext=(10, y_offset_moment),
    bbox=dict(boxstyle="round,pad=0.3")
)

ax[1].set_title("Bending Moment Diagram", pad=15)
ax[1].set_xlabel("Position (m)")
ax[1].set_ylabel("Moment (N·m)")
ax[1].grid()


# ==============================
# DEFLECTION DIAGRAM
# ==============================
ax[2].plot(x, deflection)
ax[2].scatter(x[max_deflection_idx], deflection[max_deflection_idx])

y_offset_defl = -30 if deflection[max_deflection_idx] > 0 else 30

ax[2].annotate(
    f"Max = {np.max(np.abs(deflection)):.6e} m",
    (x[max_deflection_idx], deflection[max_deflection_idx]),
    textcoords="offset points",
    xytext=(10, y_offset_defl),
    bbox=dict(boxstyle="round,pad=0.3")
)

ax[2].set_title("Deflection Diagram", pad=15)
ax[2].set_xlabel("Position (m)")
ax[2].set_ylabel("Deflection (m)")
ax[2].grid()

st.markdown("---")
st.caption("© 2026 Diego Pulido | CE2070 Beam Analysis Tool")

plt.tight_layout(pad=3.0)
st.pyplot(fig)
