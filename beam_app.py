import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==============================
# PAGE SETUP
# ==============================
st.set_page_config(page_title="Beam Analysis Tool", layout="wide")

st.title("🏗️ Beam Analysis Tool")

st.markdown("""
<div style="background-color:rgba(240,242,246,0.8);
padding:10px;border-radius:10px;margin-bottom:15px;">
<b>Developed by:</b> Diego Pulido<br>
<b>Course:</b> CE2070.02<br>
<b>Assignment:</b> Final Project
</div>
""", unsafe_allow_html=True)

# ==============================
# SIDEBAR INPUTS
# ==============================
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

col1, col2, col3 = st.columns(3)

col1.metric("Max Shear (N)", f"{np.max(np.abs(V)):.2f}")
col2.metric("Max Moment (N·m)", f"{np.max(np.abs(M)):.2f}")
col3.metric("Max Deflection (m)", f"{np.max(np.abs(deflection)):.6e}")

# ==============================
# POLISHED FBD
# ==============================
fig_fbd, ax = plt.subplots(figsize=(10,3))

# Beam
ax.plot([0, L], [0, 0], linewidth=6)

# Supports
if beam_type == "Simply Supported":
    ax.plot(0, 0, marker="^", markersize=12)
    ax.plot(L, 0, marker="o", markersize=10)
else:
    ax.plot(0, 0, marker="s", markersize=12)

# Reactions
ax.arrow(0, -0.2, 0, 1.2)
ax.text(0, 1.5, f"R1={R1:.0f}", ha='center')

if beam_type == "Simply Supported":
    ax.arrow(L, -0.2, 0, 1.2)
    ax.text(L, 1.5, f"R2={R2:.0f}", ha='center')

# Loads (OFFSET ABOVE BEAM)
for load in loads:
    if load[0] == "point":
        _, P, a = load
        ax.arrow(a, 2.0, 0, -1.6)
        ax.text(a, 2.2, f"P={P:.0f}", ha='center')
    else:
        _, w, a, b = load
        for xi in np.linspace(a, b, 10):
            ax.arrow(xi, 2.0, 0, -1.6)
        ax.text((a+b)/2, 2.2, f"w={w:.0f}", ha='center')

# External moment
theta = np.linspace(0, np.pi, 50)
r = 0.5
ax.plot(moment_pos + r*np.cos(theta), 1.2 + r*np.sin(theta))
ax.text(moment_pos, 2.0, f"M={moment_value:.0f}", ha='center')

ax.set_xlim(-1, L+1)
ax.set_ylim(-1, 3)
ax.axis('off')

st.pyplot(fig_fbd)

# ==============================
# DIAGRAMS WITH MAX HIGHLIGHTING
# ==============================
st.markdown("## 📈 Diagrams")

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


plt.tight_layout(pad=3.0)
st.pyplot(fig)
