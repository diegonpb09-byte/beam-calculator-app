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
">
<b>Developed by:</b> Diego Pulido<br>
<b>Course:</b> CE2070.02<br>
<b>Assignment:</b> Final Project
</div>
""", unsafe_allow_html=True)

# ==============================
# INPUTS
# ==============================
st.markdown("## 🔧 Inputs")

beam_type = st.sidebar.selectbox("Beam Type", ["Simply Supported", "Cantilever"])

L = st.sidebar.number_input("Beam Length (m)", 1.0, 100.0, 10.0)
E = st.sidebar.number_input("Elastic Modulus E (Pa)", value=200e9, format="%.2e")
I = st.sidebar.number_input("Moment of Inertia I (m⁴)", value=1e-6, format="%.2e")

# ==============================
# LOADS
# ==============================
num_loads = st.sidebar.number_input("Number of Loads", 1, 5, 1)

loads = []
for i in range(int(num_loads)):
    st.sidebar.markdown(f"### Load {i+1}")

    load_type = st.sidebar.selectbox("Type", ["Point Load", "UDL"], key=f"type_{i}")

    if load_type == "Point Load":
        P = st.sidebar.number_input(f"P{i+1}", key=f"P_{i}")
        a = st.sidebar.number_input(f"Position {i+1}", 0.0, L, key=f"a_{i}")
        loads.append(("point", P, a))
    else:
        w = st.sidebar.number_input(f"w{i+1}", key=f"w_{i}")
        a = st.sidebar.number_input(f"Start {i+1}", 0.0, L, key=f"start_{i}")
        b = st.sidebar.number_input(f"End {i+1}", 0.0, L, key=f"end_{i}")
        loads.append(("udl", w, a, b))

# ==============================
# EXTERNAL MOMENT
# ==============================
moment_value = st.sidebar.number_input("Moment (N·m)", value=0.0)
moment_pos = st.sidebar.number_input("Moment Position (m)", 0.0, L, L/2)

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
    R2 = (total_moment + moment_value) / L
    R1 = total_force - R2

    # APPLY reactions (THIS WAS MISSING)
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

    elif load[0] == "udl":
        w, a, b = load[1], load[2], load[3]

        V += np.where(x < a, 0,
             np.where(x <= b, -w*(x - a), -w*(b - a)))

        M += np.where(x < a, 0,
             np.where(x <= b, -w*(x - a)**2 / 2,
                      -w*(b - a)*(x - (a + b)/2)))

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

col1, col2, col3 = st.columns(3)

col1.metric("Max Shear (N)", f"{np.max(np.abs(V)):.2f}")
col2.metric("Max Moment (N·m)", f"{np.max(np.abs(M)):.2f}")
col3.metric("Max Deflection (m)", f"{np.max(np.abs(deflection)):.6e}")

# ==============================
# FBD
# ==============================
st.markdown("## 🏗️ Free Body Diagram")

fig_fbd, ax = plt.subplots(figsize=(10,3))

ax.plot([0, L], [0, 0], linewidth=6)

# Supports
ax.plot(0, 0, marker="^", markersize=12)
ax.plot(L, 0, marker="o", markersize=10)

# Reactions
ax.arrow(0, -0.1, 0, 0.8, head_width=0.2, head_length=0.2)
ax.text(0, 1.0, f"R1={R1:.0f}", ha='center')

ax.arrow(L, -0.1, 0, 0.8, head_width=0.2, head_length=0.2)
ax.text(L, 1.0, f"R2={R2:.0f}", ha='center')

# Loads
for load in loads:
    if load[0] == "point":
        _, P, a = load
        ax.arrow(a, 1.5, 0, -1.0, head_width=0.2, head_length=0.2)
        ax.text(a, 1.7, f"P={P:.0f}", ha='center')
    else:
        _, w, a, b = load
        for xi in np.linspace(a, b, 8):
            ax.arrow(xi, 1.5, 0, -1.0, head_width=0.15, head_length=0.15)
        ax.text((a+b)/2, 1.7, f"w={w:.0f}", ha='center')

# Beam scale
for pos in np.arange(0, L+1, 1):
    ax.plot([pos, pos], [0, -0.15], color='black')
    ax.text(pos, -0.35, f"{int(pos)}", ha='center', fontsize=8)

ax.set_xlim(-0.5, L+0.5)
ax.set_ylim(-1, 2)
ax.axis('off')

st.pyplot(fig_fbd)

# ==============================
# DIAGRAMS
# ==============================
fig, ax = plt.subplots(3,1, figsize=(10,10))

ax[0].plot(x, V)
ax[0].set_title("Shear Force")

ax[1].plot(x, M)
ax[1].set_title("Moment")

ax[2].plot(x, deflection)
ax[2].set_title("Deflection")

plt.tight_layout()
st.pyplot(fig)
