import streamlit as st
from google import genai

# 1. API 키 설정 (반드시 Secrets 사용)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("Secrets에 GEMINI_API_KEY가 설정되지 않았습니다.")
    st.stop()

# 2. 클라이언트 초기화 (세션에 저장하여 반복 호출 방지)
if "client" not in st.session_state:
    st.session_state.client = genai.Client(api_key=API_KEY)

st.title("💬 AETHER-NET v51.01")

# 3. 메시지 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. 채팅 입력
if prompt := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # 스트리밍 응답
            stream = st.session_state.client.models.generate_content_stream(
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            def get_stream():
                for chunk in stream:
                    if chunk.text:
                        yield chunk.text

            full_response = st.write_stream(get_stream())
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            if "429" in str(e):
                st.warning("⚠️ 구글 서버가 바쁩니다. 1분만 쉬었다가 다시 말을 걸어주세요.")
            else:
                st.error(f"오류 발생: {e}")
