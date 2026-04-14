# step 1 - setup UI with Streamlit(where we send inputs from UI- model provider, model, system_prompt, query,allow search)

import streamlit as st
import requests
st.set_page_config(page_title="LangGraph Agent UI", layout="centered")
st.title("AI Chatbot Agents")
st.write("Interact with AI Agents built by Shruthi!")

system_prompt = st.text_area("Define your AI Agents: ", height=70,
                             placeholder="""Type your system prompt here how should Agent Act like. For Example: Act as Data Analayst,etc..
                             """)


MODEL_NAMES_GROQ = ["llama-3.3-70b-versatile",
                    "meta-llama/llama-prompt-guard-2-22m"]
MODEL_NAMES_OPENAI = ["gpt-4o-mini"]

provider = st.radio("Select Provider:", ("Groq", "OpenAI"))

if provider == "Groq":
    selected_model = st.selectbox("Select Groq Model:", MODEL_NAMES_GROQ)
elif provider == "OpenAI":
    selected_model = st.selectbox("Select OpenAI Model:", MODEL_NAMES_OPENAI)

allow_web_search = st.checkbox("Allow Internet Search")  # stores True or False

user_query = st.text_area("Enter Your Query: ",
                          height=150,
                          placeholder="Ask Anything!")

API_URL = "http://127.0.0.1:9999/chat"
if st.button("Ask Agent!"):

    def call_api(provider_name, model_name):

        payload = {
            "model_name": model_name,
            "model_provider": provider_name,
            "system_prompt": system_prompt,
            "messages": [user_query],
            "allow_search": allow_web_search
        }

        return requests.post(API_URL, json=payload, timeout=60)

    try:
        # 1️⃣ PRIMARY CALL (user selection)
        response = call_api(provider, selected_model)

        if response.status_code == 200:
            data = response.json()

            if "error" not in data:
                st.subheader(f"AI Response:")
                st.write(data)
                st.stop()

        # 2️⃣ FALLBACK LOGIC (dynamic switch)
        st.warning(
            f"{provider} limit reached → switching fallback🔄 to use other provider")

        # decide fallback provider dynamically
        fallback_provider = "Groq" if provider == "OpenAI" else "OpenAI"

        # choose fallback model dynamically
        if fallback_provider == "Groq":
            fallback_model = MODEL_NAMES_GROQ[0]
        else:
            fallback_model = MODEL_NAMES_OPENAI[0]

        response = call_api(fallback_provider, fallback_model)

        if response.status_code == 200:
            data = response.json()

            st.subheader(f"Response from ({fallback_provider})")
            st.write(data)

        else:
            st.error("Both providers failed")
            st.write(response.text)

    except Exception as e:
        st.error(f"Request failed: {e}")
