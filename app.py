import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

st.set_page_config(layout="wide")
st.title("포물선 운동 시뮬레이터")

g = 9.81
rho = 1.225
C_d = 0.47
r = 0.005
A = np.pi * r**2
v0 = 4.5
angle_deg = 45
angle_rad = np.radians(angle_deg)
v0x = v0 * np.cos(angle_rad)
v0y = v0 * np.sin(angle_rad)
y0 = 1.0

masses = [5, 100, 500, 1000]
colors = ['red', 'orange', 'green', 'blue']

if 'trajectories' not in st.session_state:
    st.session_state.trajectories = []

placeholder = st.empty()

def air_resistance(v, m):
    base_drag = 0.5 * C_d * rho * A * v**2 / m
    return 2 * base_drag

def simulate(mass_g, resistance=True, dt=0.01, max_t=5.0):
    mass = mass_g / 1000
    x, y = 0.0, y0
    vx, vy = v0x, v0y
    t = 0
    X, Y = [], []

    while y >= 0 and t < max_t:
        v = np.sqrt(vx**2 + vy**2)
        if resistance:
            ax = -air_resistance(v, mass) * (vx / v)
            ay = -g - air_resistance(v, mass) * (vy / v)
        else:
            ax = 0
            ay = -g

        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt

        if y < 0:
            y = 0
            X.append(x)
            Y.append(y)
            break

        X.append(x)
        Y.append(y)
        t += dt

    return np.array(X), np.array(Y)

if st.button("초기화"):
    st.session_state.trajectories = []

resist = st.radio("공기 저항 선택", ["공기 저항 없음", "공기 저항 있음"])
with_resistance = (resist == "공기 저항 있음")

for i, mass in enumerate(masses):
    if st.button(f"{mass}g 공 던지기", key=f"btn_{mass}_{resist}"):
        x_new, y_new = simulate(mass, resistance=with_resistance)
        max_len = len(x_new)

        for step in range(1, max_len, 3):
            fig, ax = plt.subplots(figsize=(12,7))
            ax.set_xlim(0, 3)
            ax.set_ylim(0, 3)
            ax.set_xlabel("거리 (m)")
            ax.set_ylabel("높이 (m)")
            ax.set_title("포물선 궤적 시각화")

           
            for traj_x, traj_y, color, label in st.session_state.trajectories:
                ax.plot(traj_x, traj_y, color=color, alpha=0.4, label=label)
                ax.plot(traj_x[-1], traj_y[-1], 'o', color=color, markersize=8)
                
                ax.axvline(x=traj_x[-1], color=color, linestyle='--', alpha=0.6)
               
                ax.text(traj_x[-1], 2.9, f"{traj_x[-1]:.2f} m", color=color,
                        fontsize=10, rotation=90, verticalalignment='top', horizontalalignment='right')

           
            ax.plot(x_new[:step], y_new[:step], color=colors[i], linewidth=2, label=f"{mass}g ({resist}) - 진행중")
            ax.plot(x_new[step-1], y_new[step-1], 'o', color=colors[i], markersize=12)

            ax.legend()
            placeholder.pyplot(fig)
            time.sleep(0.01)

        st.session_state.trajectories.append((x_new, y_new, colors[i], f"{mass}g ({resist})"))
