import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# 1. 페이지 설정
st.set_page_config(page_title="메트로 가챠", page_icon="🚇", layout="centered")

# 2. 구글 시트 연결 설정
sheet_url = "https://docs.google.com/spreadsheets/d/18G3usNykL9ncp0bg4V6esSGw2jsG7u5a9ikN_Uvhnxw/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. 조회수 로직 (구글 시트 기반)
@st.cache_data(ttl=0)
def get_view_count():
    try:
        df = conn.read(spreadsheet=sheet_url, usecols=[0])
        return int(df.iloc[0, 0])
    except:
        return 0

if 'is_counted' not in st.session_state:
    current_views = get_view_count()
    current_views += 1
    
    # 구글 시트 업데이트
    new_df = pd.DataFrame({"views": [current_views]})
    conn.update(spreadsheet=sheet_url, data=new_df)
    
    st.session_state.is_counted = True
    st.session_state.view_count_now = current_views
else:
    current_views = st.session_state.view_count_now

# 4. 디자인 CSS
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    .main-title { color: #FFDD59; text-align: center; font-size: 40px; font-weight: bold; margin-bottom: 20px; }
    .step-box { background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #333; margin-bottom: 20px; text-align: center; }
    .result-card { background-color: #2D3436; padding: 30px; border-radius: 20px; border: 3px solid #FFDD59; text-align: center; }
    div.stButton > button { background-color: #FFDD59 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; }
    .stLinkButton a { background-color: #FFDD59 !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# 5. 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv", encoding='utf-8')
    def get_line_name(x):
        import re
        match = re.search(r'\d+', str(x))
        return f"{int(match.group())}호선" if match else "기타"
    df['호선_정리'] = df['호선'].apply(get_line_name)
    return df

df = load_data()
st.markdown('<div class="main-title">🚇 메트로 가챠</div>', unsafe_allow_html=True)

if 'step' not in st.session_state:
    st.session_state.step = 1

# --- 1단계: 호선 뽑기 ---
if st.session_state.step == 1:
    st.markdown('<div class="step-box"><h3>🗺️ 오늘의 여행지는 어디?</h3></div>', unsafe_allow_html=True)
    image_place = st.empty()
    image_place.image("image/gacha2.png", use_container_width=True)
    if st.button("🎰 호선 번호 뽑기 시작!"):
        image_place.image("image/gacha.gif", use_container_width=True)
        time.sleep(2)
        st.session_state.selected_line = f"{random.randint(1, 9)}호선"
        st.session_state.step = 2
        st.rerun()

# --- 2단계: 역 뽑기 ---
elif st.session_state.step == 2:
    line = st.session_state.selected_line
    stations = df[df['호선_정리'] == line].reset_index(drop=True)
    st.markdown(f'<div class="step-box"><h3>✅ {line} 당첨!</h3></div>', unsafe_allow_html=True)
    image_place = st.empty()
    image_place.image("image/gacha2.png", use_container_width=True)
    if st.button(f"🎲 {line} 역 번호 추첨하기!"):
        image_place.image("image/gacha.gif", use_container_width=True)
        time.sleep(2)
        lucky_idx = random.randint(0, len(stations) - 1)
        final_station = stations.iloc[lucky_idx]
        st.balloons()
        st.markdown(f'<div class="result-card"><h1>{final_station["전철역명"]}</h1></div>', unsafe_allow_html=True)
        st.link_button(f"🍴 {final_station['전철역명']} 맛집 검색", f"https://map.naver.com/v5/search/{final_station['전철역명']} 맛집")
    if st.button("🔄 다시 하기"):
        st.session_state.step = 1
        st.rerun()

# --- 6. 하단 조회수 출력 (오른쪽 정렬 회색 글씨) ---
st.markdown(
    f"""
    <div style="text-align: right; color: gray; font-size: 0.8rem; margin-top: 50px; padding-bottom: 20px;">
        누적 조회수: {current_views}
    </div>
    """,
    unsafe_allow_html=True
)

# 비밀 확인 (주소창 ?check=admin)
if st.query_params.get("check") == "admin":
    st.info(f"🕵️ 관리자 모드: 구글 시트와 동기화된 조회수는 {current_views}회입니다.")
