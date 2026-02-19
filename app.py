import streamlit as st
from google import genai
import sys
import io

# 1. 시스템 인코딩 강제 설정 (ASCII 코덱 에러 방지)
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

# 2. 페이지 설정 및 테마
st.set_page_config(page_title="AETHER-NET v51.01", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #00ffcc; }
    .stChatInput { border-color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

st.title("💬 AETHER-NET v51.01")
st.caption("Status: Active | Core: Gemini 2.0 Flash | Encoding: UTF-8")

# 3. API 키 설정 (새로 발급받은 키를 여기에 넣으세요)
# 절대로 키를 직접 넣지 마세요! 아래 한 줄로 대체합니다.
API_KEY = st.secrets["GEMINI_API_KEY"]

try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"클라이언트 초기화 실패: {e}")

# 4. 세션 기록 관리
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 메인 대화 로직
if prompt := st.chat_input("Accessing AETHER-NET..."):
    # 유저 메시지 저장 및 출력
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 파트
    with st.chat_message("assistant"):
        try:
            # 2026년 표준 모델인 gemini-2.0-flash 사용
            # 스트리밍 모드로 속도 체감 극대화
            stream = client.models.generate_content_stream(
                model="gemini-2.0-flash",
                config={
                    'system_instruction': '너는 AETHER-NET의 핵심 인공지능이다. 한글로 아주 간결하고 명확하게 답해라.',
                    'temperature': 0.5
                },
                contents=prompt
            )

            # 데이터 실시간 렌더링 함수
            def stream_data():
                for chunk in stream:
                    if chunk.text:
                        yield chunk.text

            # 실시간 타이핑 효과 출력
            full_response = st.write_stream(stream_data())
            
            # 최종 답변 기록
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                st.error("🚨 QUOTA EXHAUSTED: 무료 할당량을 모두 사용했습니다. 1분만 기다려주세요.")
                
            elif "ascii" in error_msg.lower():
                st.error("⚠️ 인코딩 오류: 시스템 환경을 UTF-8로 변경해야 합니다.")
            else:

                st.error(f"⚠️ 시스템 오류: {error_msg}")
