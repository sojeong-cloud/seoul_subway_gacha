import streamlit as st
import pandas as pd
import random
import time

# 1. 페이지 설정
st.set_page_config(page_title="서울 지하철 랜덤 여행", page_icon="🚇", layout="centered")

# 디자인 CSS
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    .main-title { color: #FFDD59; text-align: center; font-size: 40px; font-weight: bold; margin-bottom: 20px; }
    .step-box { background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #333; margin-bottom: 20px; text-align: center; }
    .result-card { background-color: #2D3436; padding: 30px; border-radius: 20px; border: 3px solid #FFDD59; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 (절대 경로)
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv", encoding='utf-8')
    def get_line_name(x):
        import re
        match = re.search(r'\d+', str(x))
        return f"{int(match.group())}호선" if match else "기타"
    df['호선_정리'] = df['호선'].apply(get_line_name)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 읽기 오류: {e}")
    st.stop()

st.markdown('<div class="main-title">🚇 서울 지하철 랜덤 가챠</div>', unsafe_allow_html=True)

if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.selected_line = None

# --- 1단계: 시작 화면 및 호선 뽑기 ---
if st.session_state.step == 1:
    st.markdown('<div class="step-box"><h3>🗺️ 오늘의 여행지는 어디?</h3></div>', unsafe_allow_html=True)
    
    # [추가] 시작 화면 이미지
    try:
        st.image("image/gacha2.png", use_container_width=True)
    except:
        st.info("시작 화면 이미지를 불러올 수 없습니다. (경로 확인 필요)")

    if st.button("🎰 호선 번호 뽑기 시작!"):
        placeholder = st.empty()
        placeholder.image("image/gacha.gif", use_container_width=True)
        time.sleep(2)
        placeholder.empty()
        
        lucky_line_num = random.randint(1, 9)
        st.session_state.selected_line = f"{lucky_line_num}호선"
        st.session_state.step = 2
        st.rerun()

# --- 2단계: 호선 선택 완료 및 역 뽑기 ---
elif st.session_state.step == 2:
    line = st.session_state.selected_line
    stations = df[df['호선_정리'] == line].reset_index(drop=True)
    total_count = len(stations)
    
    st.markdown(f'<div class="step-box"><h3>✅ {line} 당첨!</h3><p>총 <b>{total_count}</b>개의 역 중에서 운명의 장소를 골라보세요.</p></div>', unsafe_allow_html=True)
    
    # [추가] 호선 선택 시 보여줄 이미지
    try:
        st.image("image/gacha2.png", use_container_width=True)
    except:
        st.info("호선 선택 이미지를 불러올 수 없습니다.")

    if st.button(f"🎲 {line} 역 번호 추첨하기!"):
        placeholder = st.empty()
        placeholder.image("image/gacha.gif", use_container_width=True)
        time.sleep(2)
        placeholder.empty()
        
        if total_count > 0:
            lucky_idx = random.randint(0, total_count - 1)
            final_station = stations.iloc[lucky_idx]
            
            st.balloons()
            st.markdown(f"""
                <div class="result-card">
                    <h2 style="color: #FFDD59;">🎉 {lucky_idx + 1}번 역 당첨!</h2>
                    <h1 style="font-size: 60px; margin: 10px 0;">{final_station['전철역명']}</h1>
                    <p style="font-size: 20px; color: #BDC3C7;">({final_station['전철명명(영문)']})</p>
                </div>
            """, unsafe_allow_html=True)
            
            search_query = f"{final_station['전철역명']} 맛집"
            map_url = f"https://map.naver.com/v5/search/{search_query}"
            st.link_button(f"🍴 {final_station['전철역명']} 맛집 검색", map_url)
        
    if st.button("🔄 처음부터 다시 하기"):
        st.session_state.step = 1
        st.rerun()
