import streamlit as st
import pandas as pd
import random
import time
import json
import os
import streamlit.components.v1 as components

# 1. 조회수 저장 로직 (파일 기반)
counter_file = "view_count.json"

# 세션 상태 초기화 (중복 카운트 방지)
if 'view_count_now' not in st.session_state:
    st.session_state.view_count_now = 0

if 'is_counted' not in st.session_state:
    # 파일이 있으면 읽고, 없으면 0부터 시작
    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            try:
                data = json.load(f)
                current_views = data.get("views", 0)
            except:
                current_views = 0
    else:
        current_views = 0

    # 조회수 1 증가 및 파일 저장
    current_views += 1
    try:
        with open(counter_file, "w") as f:
            json.dump({"views": current_views}, f)
    except:
        pass # 서버 권한 문제 대비
    
    st.session_state.view_count_now = current_views
    st.session_state.is_counted = True
else:
    # 이미 카운트했다면 세션에 저장된 값 사용
    current_views = st.session_state.view_count_now

# 2. 페이지 설정
st.set_page_config(page_title="메트로 가챠", page_icon="🚇", layout="centered")

# 3. 디자인 CSS (라이트 모드 가시성 해결 포함)
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    .main-title { color: #FFDD59; text-align: center; font-size: 40px; font-weight: bold; margin-bottom: 20px; }
    .step-box { background-color: #1E1E1E; padding: 20px; border-radius: 15px; border: 2px solid #333; margin-bottom: 20px; text-align: center; }
    .result-card { background-color: #2D3436; padding: 30px; border-radius: 20px; border: 3px solid #FFDD59; text-align: center; }
    
    /* 버튼 스타일 강제 고정 */
    div.stButton > button {
        background-color: #FFDD59 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        width: 100% !important;
        height: 50px !important;
    }
    
    /* 링크 버튼 스타일 */
    .stLinkButton a {
        background-color: #FFDD59 !important;
        color: #000000 !important;
        font-weight: bold !important;
        text-decoration: none !important;
        display: block !important;
        text-align: center !important;
        padding: 10px !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. 데이터 로드
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
    except Exception as e:
        st.error(f"데이터 읽기 오류: {e}")
        return None

df = load_data()
if df is None:
    st.stop()

st.markdown('<div class="main-title">🚇 메트로 가챠</div>', unsafe_allow_html=True)

# 세션 관리 (단계별 화면)
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.selected_line = None

# --- 1단계: 시작 화면 및 호선 뽑기 ---
if st.session_state.step == 1:
    st.markdown('<div class="step-box"><h3>🗺️ 오늘의 여행지는 어디?</h3></div>', unsafe_allow_html=True)
    
    image_place = st.empty()
    image_place.image("image/gacha2.png", use_container_width=True)

    if st.button("🎰 호선 번호 뽑기 시작!"):
        image_place.image("image/gacha.gif", use_container_width=True)
        time.sleep(2)
        image_place.empty()
        
        lucky_line_num = random.randint(1, 9)
        st.session_state.selected_line = f"{lucky_line_num}호선"
        st.session_state.step = 2
        st.rerun()

# --- 2단계: 호선 당첨 및 역 뽑기 ---
elif st.session_state.step == 2:
    line = st.session_state.selected_line
    stations = df[df['호선_정리'] == line].reset_index(drop=True)
    total_count = len(stations)
    
    st.markdown(f'<div class="step-box"><h3>✅ {line} 당첨!</h3><p>총 <b>{total_count}</b>개의 역 중에서 운명의 장소를 골라보세요.</p></div>', unsafe_allow_html=True)
    
    image_place = st.empty()
    image_place.image("image/gacha2.png", use_container_width=True)

    if st.button(f"🎲 {line} 역 번호 추첨하기!"):
        image_place.image("image/gacha.gif", use_container_width=True)
        time.sleep(2)
        image_place.empty()
        
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

# --- 5. 하단 조회수 출력 (오른쪽 정렬 회색 글씨) ---
st.markdown(
    f"""
    <div style="text-align: right; color: gray; font-size: 0.8rem; margin-top: 50px; padding-bottom: 20px;">
        누적 조회수: {current_views}
    </div>
    """,
    unsafe_allow_html=True
)

# --- 💬 Giscus 댓글창 (수정 버전) ---
st.write("---")

# html 함수 안에 들어가는 내용은 f-string 대신 일반 문자열로 넣는 게 안전
giscus_script = """
<script src="https://giscus.app/client.js"
        data-repo="sojeong-cloud/seoul_subway_gacha"
        data-repo-id="R_kgDORu1prA"
        data-category="Announcements"
        data-category-id="DIC_kwDORu1prM4C5UQp"
        data-mapping="pathname"
        data-strict="0"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="top"
        data-theme="dark"
        data-lang="ko"
        crossorigin="anonymous"
        async>
</script>
"""

components.html(giscus_script, height=600, scrolling=True)
