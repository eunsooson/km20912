import streamlit as st
import numpy as np
import plotly.graph_objects as go


g = 9.81
rho = 1.225
C_d = 0.47
diameter = 0.01
A = np.pi * (diameter / 2) ** 2
v0 = 20
theta = np.radians(45)


def simulate(mass, air):
    dt = 0.01
    vx, vy = v0 * np.cos(theta), v0 * np.sin(theta)
    x, y = 0, 0
    xs, ys = [x], [y]
    while y >= 0:
        v = np.hypot(vx, vy)
        if air:
            F_d = 3 * 0.5 * C_d * rho * A * v ** 2
            ax = -F_d * vx / (v * mass)
            ay = -g - F_d * vy / (v * mass)
        else:
            ax, ay = 0, -g
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        xs.append(x)
        ys.append(y)
    return xs, ys


def color_with_opacity(color, opacity):
    if color == "red":
        return f"rgba(255,0,0,{opacity})"
    elif color == "green":
        return f"rgba(0,128,0,{opacity})"
    elif color == "blue":
        return f"rgba(0,0,255,{opacity})"
    else:
        return color



if "trajectories" not in st.session_state:
    st.session_state.trajectories = []  # (label, xs, ys, color, distance, y_text_pos, air)

st.set_page_config(layout="wide")
st.title("포물선 운동 시뮬레이터")


col_buttons, col_graph = st.columns([1, 4])

with col_buttons:
    air = st.checkbox("공기 저항", value=True)

    label = None
    mass = None
    color = None

    if st.button("1g", key="btn1g"):
        label = "1g"
        mass = 0.001
        color = "red"
    if st.button("100g", key="btn100g"):
        label = "100g"
        mass = 0.1
        color = "green"
    if st.button("1000g", key="btn1000g"):
        label = "1000g"
        mass = 1.0
        color = "blue"

    if st.button("초기화", key="btnclear"):
        st.session_state.trajectories = []

    if label is not None:
        xs, ys = simulate(mass, air)
        distance = xs[-1]
        y_text_pos = 0.5 + 0.7 * len(st.session_state.trajectories)
        st.session_state.trajectories.append((label, xs, ys, color, distance, y_text_pos, air))

with col_graph:
    if len(st.session_state.trajectories) == 0:
        st.write("왼쪽 버튼을 눌러 공을 던지세요")
    else:
        fixed_traces = []
        fixed_lines = []
        fixed_texts = []
        for label_i, xs, ys, color, distance, y_text_pos, air_on in st.session_state.trajectories[:-1]:
            opacity = 0.4 if air_on else 1.0
            fixed_traces.append(
                go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=2), opacity=opacity, name=label_i)
            )
            fixed_lines.append(
                go.layout.Shape(
                    type="line",
                    x0=distance,
                    y0=0,
                    x1=distance,
                    y1=15,
                    line=dict(color=color_with_opacity(color, opacity), dash="dash", width=2),
                )
            )
            fixed_texts.append(
                dict(
                    x=distance + 0.3,
                    y=y_text_pos,
                    text=f"{label_i} - {distance:.1f}m",
                    showarrow=False,
                    font=dict(color=color, size=14),
                    xanchor="left",
                )
            )

        last_label, last_xs, last_ys, last_color, last_distance, last_y_text_pos, last_air = st.session_state.trajectories[
            -1
        ]
        last_opacity = 0.4 if last_air else 1.0

        frames = []
        for i in range(len(last_xs)):
            data = fixed_traces.copy()
            data.append(
                go.Scatter(
                    x=last_xs[: i + 1],
                    y=last_ys[: i + 1],
                    mode="lines",
                    line=dict(color=last_color, width=3),
                    opacity=last_opacity,
                    name=last_label,
                )
            )
            data.append(
                go.Scatter(
                    x=[last_xs[i]],
                    y=[last_ys[i]],
                    mode="markers",
                    marker=dict(color=last_color, size=14, opacity=last_opacity),
                )
            )
            frames.append(go.Frame(data=data, name=str(i)))

        init_data = fixed_traces.copy()
        init_data.append(
            go.Scatter(x=[last_xs[0]], y=[last_ys[0]], mode="markers", marker=dict(color=last_color, size=14, opacity=last_opacity))
        )

        fig = go.Figure(data=init_data, frames=frames)

        fig.update_layout(
            xaxis=dict(range=[0, 45], title="거리 (m)"),
            yaxis=dict(range=[0, 15], title="높이 (m)"),
            title="포물선 운동 시뮬레이터",
            showlegend=False,
            transition=dict(duration=0),
            shapes=fixed_lines,
            annotations=fixed_texts,
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    buttons=[
                        dict(
                            label="",
                            method="animate",
                            args=[
                                None,
                                {"frame": {"duration": 25, "redraw": True}, "fromcurrent": True, "mode": "immediate"},
                            ],
                        )
                    ],
                )
            ],
        )

        
        fig.add_shape(
            type="line",
            x0=last_distance,
            y0=0,
            x1=last_distance,
            y1=15,
            line=dict(color=color_with_opacity(last_color, last_opacity), dash="dash", width=2),
        )
        fig.add_annotation(
            x=last_distance + 0.3,
            y=last_y_text_pos,
            text=f"{last_label} - {last_distance:.1f}m",
            showarrow=False,
            font=dict(color=last_color, size=14),
            xanchor="left",
        )

        st.plotly_chart(fig, use_container_width=True)

