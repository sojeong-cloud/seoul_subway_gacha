import streamlit as st
import pandas as pd
import random
import time
import json
import os
import streamlit.components.v1 as components

# 1. 조회수 로직 (에러 방지 처리)
counter_file = "view_count.json"
if 'view_count_now' not in st.session_state:
    st.session_state.view_count_now = 0

if 'is_counted' not in st.session_state:
    current_views = 0
    if os.path.exists(counter_file):
        try:
            with open(counter_file, "r") as f:
                data = json.load(f)
                current_views = data.get("views", 0)
        except: pass
    
    current_views += 1
    try:
        with open(counter_file, "w") as f:
            json.dump({"views": current_views}, f)
    except: pass # 서버 권한 에러 무시
    
    st.session_state.view_count_now = current_views
    st.session_state.is_counted = True
else:
    current_views = st.session_state.view_count_now

# 2. 페이지 설정 및 디자인
st.set_page_config(page_title="메트로 가챠", page_icon="🚇", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    .main-title { color: #FFDD59; text-align: center; font-size: 40px; font-weight: bold; margin-bottom: 20px; }
    .step-box { background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #333; margin-bottom: 20px; text-align: center; }
    .result-card { background-color: #2D3436; padding: 30px; border-radius: 20px; border: 3px solid #FFDD59; text-align: center; }
    div.stButton > button { background-color: #FFDD59 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; width: 100% !important; height: 50px !important; }
    .stLinkButton a { background-color: #FFDD59 !important; color: #000 !important; font-weight: bold !important; text-decoration: none !important; display: block !important; text-align: center !important; padding: 10px !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로드
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv", encoding='utf-8')
        def get_line_name(x):
            import re
            match = re.search(r'\d+', str(x))
            return f"{int(match.group())}호선" if match else "기타"
        df['호선_정리'] = df['호선'].apply(get_line_name)
        return df
    except: return None

df = load_data()
if df is not None:
    st.markdown('<div class="main-title">🚇 메트로 가챠</div>', unsafe_allow_html=True)
    
    if 'step' not in st.session_state:
        st.session_state.step = 1

    if st.session_state.step == 1:
        st.markdown('<div class="step-box"><h3>🗺️ 오늘의 여행지는 어디?</h3></div>', unsafe_allow_html=True)
        image_place = st.empty()
        image_place.image("image/gacha2.png", use_container_width=True)
        if st.button("🎰 호선 번호 뽑기 시작!"):
            image_place.image("image/gacha.gif", use_container_width=True)
            time.sleep(1.5)
            st.session_state.selected_line = f"{random.randint(1, 9)}호선"
            st.session_state.step = 2
            st.rerun()

    elif st.session_state.step == 2:
        line = st.session_state.selected_line
        stations = df[df['호선_정리'] == line].reset_index(drop=True)
        st.markdown(f'<div class="step-box"><h3>✅ {line} 당첨!</h3></div>', unsafe_allow_html=True)
        image_place = st.empty()
        image_place.image("image/gacha2.png", use_container_width=True)
        if st.button(f"🎲 {line} 역 추첨하기!"):
            image_place.image("image/gacha.gif", use_container_width=True)
            time.sleep(1.5)
            lucky_idx = random.randint(0, len(stations) - 1)
            final_station = stations.iloc[lucky_idx]
            st.balloons()
            st.markdown(f'<div class="result-card"><h1>{final_station["전철역명"]}</h1></div>', unsafe_allow_html=True)
            st.link_button(f"🍴 {final_station['전철역명']} 맛집 검색", f"https://map.naver.com/v5/search/{final_station['전철역명']} 맛집")
        if st.button("🔄 다시 하기"):
            st.session_state.step = 1
            st.rerun()

# 4. 하단 조회수
st.markdown(f'<div style="text-align: right; color: gray; font-size: 0.8rem; margin-top: 50px;">누적 조회수: {current_views}</div>', unsafe_allow_html=True)
st.write("---")


# --- 💬 방문자 피드백 (디자인 수정 버전) ---
st.write("---")
st.markdown('<h3 style="text-align: center;">💬 의견을 남겨주세요!</h3>', unsafe_allow_html=True)


my_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSctHf3pKpaTY6qUvo7KrEUpL6Zh2HXJF-ne-TxdCzl41PMw4g/viewform?embedded=true"

# 폼 주변에 어두운 박스(#1E1E1E)
st.markdown(f"""
    <div style="background-color: #1E1E1E; padding: 15px; border-radius: 15px; border: 1px solid #333;">
        <iframe src="{my_form_url}" 
                width="100%" height="800" frameborder="0" marginheight="0" marginwidth="0">로드 중…</iframe>
    </div>
""", unsafe_allow_html=True)

# 하단 직접 가기 버튼
st.markdown("<br>", unsafe_allow_html=True)
st.link_button("📢 직접 의견 남기러 가기", my_form_url)
