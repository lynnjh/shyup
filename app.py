import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 디자인 (GS25 BI 테마)
st.set_page_config(page_title="수도권 경영주협의회 명단", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    h1 { color: #0076BE !important; font-weight: bold; }
    .stButton>button { background-color: #0076BE; color: white; border-radius: 8px; font-weight: bold; }
    /* 검색창 강조 디자인 */
    div[data-baseweb="input"] { border: 2px solid #0076BE !important; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 보안 비밀번호 체크 (5525)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 수도권 경영주협의회 보안 접속")
    st.write("회원 명단 확인을 위해 비밀번호를 입력해주세요.")
    pw = st.text_input("비밀번호", type="password")
    if st.button("접속하기", use_container_width=True):
        if pw == "5525":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    st.stop()

# 3. 데이터 불러오기 (구글 시트 연동)
# 알려주신 새로운 시트 주소입니다.
SHEET_URL = "https://docs.google.com/spreadsheets/d/1VW9K9XR4xK4zfUL-gkFoCj_06YiwezLJj08WzVtIhWE/edit?usp=sharing"
CSV_URL = SHEET_URL.split('/edit')[0] + '/export?format=csv'

@st.cache_data(ttl=60) # 1분마다 최신 데이터를 가져옵니다.
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        # 열 이름 양옆의 공백을 제거하여 오류를 방지합니다.
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return None

df = load_data()

# 4. 메인 화면 구성
st.title("🏙️ 수도권 경영주협의회 회원 명단")
st.write("팀명, 점포명, 경영주명, 비고 등 **아무 키워드나** 입력하여 검색하세요.")

if df is None:
    st.error("⚠️ 구글 시트를 불러오지 못했습니다. 시트의 공유 설정(링크가 있는 모든 사용자)을 확인해주세요.")
else:
    # --- 핵심 기능: 통합 검색창 ---
    search_query = st.text_input("🔍 통합 검색 (키워드를 입력하고 엔터를 치세요)", placeholder="예: 1팀, 이준호, 신규오픈, 010-1234...")

    # 검색 로직 (모든 칸을 뒤져서 키워드가 포함된 줄만 남깁니다)
    if search_query:
        # 모든 컬럼을 문자열로 바꾸고 검색어가 포함되어 있는지 검사
        mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
        filtered_df = df[mask]
    else:
        filtered_df = df

    # --- 결과 출력 ---
    st.write(f"✅ 총 **{len(filtered_df)}** 건의 명단이 확인되었습니다.")
    
    # 표 형식으로 보여주기 (스크롤 가능, 정렬 가능)
    st.dataframe(
        filtered_df, 
        use_container_width=True, 
        hide_index=True
    )

    # --- 추가 기능: 엑셀 다운로드 ---
    st.divider()
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 현재 검색된 명단 다운로드 (엑셀용)",
        data=csv,
        file_name='gs25_member_list.csv',
        mime='text/csv',
    )
