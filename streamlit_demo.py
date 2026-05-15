import copy
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="그래프 계산기", layout="wide")

# 세션 초기화
if "eqs" not in st.session_state:
    st.session_state.eqs = [{"id": 0, "expr": "", "color": "#3b82f6", "visible": True}]

# 그래프 그리기 버튼을 눌렀을 때만 업데이트되도록 스냅샷 저장
if "snapshot_eqs" not in st.session_state:
    st.session_state.snapshot_eqs = []
    st.session_state.snapshot_x   = (-10.0, 10.0)

# 그래프 그리기 함수
def draw(eqs, x_min, x_max):
    fig, ax = plt.subplots(figsize=(9, 6))
    x = np.linspace(x_min, x_max, 800)

    for eq in eqs:
        if not eq["visible"] or not eq["expr"].strip():
            continue
        try:
            y = eval(eq["expr"], {"x": x, **vars(np)})
            ax.plot(x, y, color=eq["color"], linewidth=2)
        except Exception:
            pass  # 잘못된 수식 무시

    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xlim(x_min, x_max)
    plt.tight_layout()
    return fig

# 사이드바: 수식 입력 패널
with st.sidebar:
    st.title("수식 목록")

    c1, c2 = st.columns(2)
    x_min = c1.number_input("x 최솟값", value=-10.0, step=1.0)
    x_max = c2.number_input("x 최댓값", value=10.0,  step=1.0)
    st.divider()

    for i, eq in enumerate(st.session_state.eqs):
        with st.container(border=True):
            row = st.columns([3, 1, 1, 1])
            eq["expr"]    = row[0].text_input("수식",  value=eq["expr"],  placeholder="예: sin(x)", key=f"txt_{eq['id']}", label_visibility="collapsed")
            eq["color"]   = row[1].color_picker("색상", value=eq["color"],                          key=f"clr_{eq['id']}", label_visibility="collapsed")
            eq["visible"] = row[2].checkbox("표시",     value=eq["visible"],                         key=f"chk_{eq['id']}")
            if row[3].button("삭제", key=f"del_{eq['id']}"):
                st.session_state.eqs.pop(i)
                st.rerun()

    st.divider()
    if st.button("수식 추가", use_container_width=True, type="primary"):
        new_id = max(e["id"] for e in st.session_state.eqs) + 1 if st.session_state.eqs else 0
        st.session_state.eqs.append({"id": new_id, "expr": "", "color": "#3b82f6", "visible": True})
        st.rerun()

    # 버튼 클릭 시점의 상태를 스냅샷으로 저장
    if st.button("그래프 그리기", use_container_width=True):
        st.session_state.snapshot_eqs = copy.deepcopy(st.session_state.eqs)
        st.session_state.snapshot_x   = (x_min, x_max)

# 메인: 그래프 출력
st.title("그래프 계산기")

if st.session_state.snapshot_eqs:
    st.pyplot(draw(st.session_state.snapshot_eqs, *st.session_state.snapshot_x))
else:
    st.info("수식을 입력하고 그래프 그리기 버튼을 눌러주세요.")