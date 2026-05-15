import streamlit as st

st.set_page_config(layout="wide")
st.title("📈 Desmos 스타일 수식 관리자 (Streamlit)")

# 세션 상태 초기화
if "equations" not in st.session_state:
    st.session_state.equations = [{"id": 0}]

# 사이드바 레이아웃 (왼쪽 입력창 리스트)
with st.sidebar:
    st.header("📝 수식 입력")
    
    for idx, eq in enumerate(st.session_state.equations):
        with st.container(border=True):
            cols = st.columns([4, 1, 1, 1])
            cols[0].text_input(f"수식 {idx+1}", key=f"txt_{eq['id']}", label_visibility="collapsed")
            cols[1].color_picker("색상", key=f"clr_{eq['id']}", label_visibility="collapsed")
            cols[2].checkbox("👁️", value=True, key=f"chk_{eq['id']}")
            if cols[3].button("🗑️", key=f"del_{eq['id']}"):
                st.session_state.equations.pop(idx)
                st.rerun()

    if st.button("➕ 수식 추가", use_container_width=True, type="primary"):
        new_id = st.session_state.equations[-1]["id"] + 1 if st.session_state.equations else 0
        st.session_state.equations.append({"id": new_id})
        st.rerun()

# 오른쪽 그래프 영역
st.subheader("📊 그래프 미리보기")
st.info("여기에 수식 결과 그래프가 표시됩니다.")