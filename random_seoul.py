import streamlit as st
import pandas as pd
import random
import time
#from streamlit_extras.let_it_snow import let_it_snow #폭죽효과 가져오기

# 1. 페이지 설정
st.set_page_config(page_title="메트로 가챠", page_icon="🚇", layout="centered")

# 디자인 CSS (라이트 모드에서도 버튼 글씨가 보이도록 고정)
st.markdown("""
    <style>
    /* 기본 배경 및 텍스트 설정 */
    .stApp { background-color: #121212; color: white; }
    .main-title { color: #FFDD59; text-align: center; font-size: 40px; font-weight: bold; margin-bottom: 20px; }
    .step-box { background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #333; margin-bottom: 20px; text-align: center; }
    .result-card { background-color: #2D3436; padding: 30px; border-radius: 20px; border: 3px solid #FFDD59; text-align: center; }
    
    /* 모든 버튼 스타일 강제 고정 (글씨 안 보이는 현상 해결) */
    div.stButton > button {
        background-color: #FFDD59 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        width: 100% !important;
        height: 50px !important;
        font-size: 18px !important;
    }

    /* 맛집 검색(링크) 버튼 스타일 고정 */
    .stLinkButton a {
        background-color: #FFDD59 !important;
        color: #000000 !important;
        font-weight: bold !important;
        text-decoration: none !important;
        display: block !important;
        text-align: center !important;
        padding: 10px !important;
        border-radius: 10px !important;
        font-size: 18px !important;
    }

    /* 버튼 호버 효과 */
    div.stButton > button:hover {
        background-color: #FFC107 !important;
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 (상대 경로 및 캐싱)
@st.cache_data
def load_data():
    # 깃허브 서버(리눅스) 환경에 맞춰 인코딩 및 경로 설정
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

st.markdown('<div class="main-title">🚇 메트로 가챠 </div>', unsafe_allow_html=True)

# 세션 상태 관리
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.selected_line = None

# --- 1단계: 시작 화면 및 호선 뽑기 ---
if st.session_state.step == 1:
    st.markdown('<div class="step-box"><h3>🗺️ 오늘의 여행지는 어디?</h3></div>', unsafe_allow_html=True)
    
    # 이미지 전용 빈 박스 생성
    image_place = st.empty()
    
    # 기본 이미지 표시
    try:
        image_place.image("image/gacha2.png", use_container_width=True)
    except:
        st.info("시작 이미지를 찾을 수 없습니다.")

    if st.button("🎰 호선 번호 뽑기 시작!"):
        # 버튼 누르면 움짤로 교체
        image_place.image("image/gacha.gif", use_container_width=True)
        time.sleep(2)
        image_place.empty() # 움짤 끝난 후 비우기
        
        # 1~9호선 중 무작위 선택
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
    
    # 이미지 전용 빈 박스 생성
    image_place = st.empty()
    try:
        image_place.image("image/gacha2.png", use_container_width=True)
    except:
        pass

    if st.button(f"🎲 {line} 역 번호 추첨하기!"):
        # 버튼 누르면 움짤로 교체
        image_place.image("image/gacha.gif", use_container_width=True)
        time.sleep(2)
        image_place.empty() # 비우기
        
        if total_count > 0:
            lucky_idx = random.randint(0, total_count - 1)
            final_station = stations.iloc[lucky_idx]
            
            #st.balloons() #벌룬
            let_it_snow() #폭죽 효과
            st.markdown(f"""
                <div class="result-card">
                    <h2 style="color: #FFDD59;">🎉 {lucky_idx + 1}번 역 당첨!</h2>
                    <h1 style="font-size: 60px; margin: 10px 0;">{final_station['전철역명']}</h1>
                    <p style="font-size: 20px; color: #BDC3C7;">({final_station['전철명명(영문)']})</p>
                </div>
            """, unsafe_allow_html=True)
            
            # 맛집 검색 링크 버튼
            search_query = f"{final_station['전철역명']} 맛집"
            map_url = f"https://map.naver.com/v5/search/{search_query}"
            st.link_button(f"🍴 {final_station['전철역명']} 맛집 검색", map_url)
        
    if st.button("🔄 처음부터 다시 하기"):
        st.session_state.step = 1
        st.rerun()

import json
import os

# 1. 조회수 저장용 파일 경로
counter_file = "view_count.json"

# 2. 기존 조회수 읽어오기 (파일이 없으면 0부터 시작)
if os.path.exists(counter_file):
    with open(counter_file, "r") as f:
        try:
            data = json.load(f)
            current_views = data.get("views", 0)
        except:
            current_views = 0
else:
    current_views = 0

# 3. 조회수 1 증가 
if 'is_counted' not in st.session_state:
    current_views += 1
    st.session_state.is_counted = True
    # 파일에 새 숫자 저장
    with open(counter_file, "w") as f:
        json.dump({"views": current_views}, f)

# 4. 오른쪽 하단 출력 
st.markdown(
    f"""
    <div style="text-align: right; color: gray; font-size: 0.8rem; margin-top: 50px;">
        누적 조회수: {current_views}
    </div>
    """, 
    unsafe_allow_html=True
)

#업데이트 확인
