from openai import OpenAI
import streamlit as st
import requests
import uuid
import json
import openai
client = OpenAI()

st.title("Mocero AI")
# Add the logo to the sidebar

st.markdown(
        """
        <style>
      .st-emotion-cache-6qob1r {
        background-color :#000000;
    }
        .st-emotion-cache-13ejsyy{
        background-color : Transparent;
        color:white;
        white-space: nowrap; 
        width : 80%;
        overflow: hidden;
        text-overflow: ellipsis; 
        justify-content : start;
        border :None;
        }
        </style>
        """, unsafe_allow_html=True)
openai.api_key = st.secrets["OPENAI_API_KEY"]

url_params = st.experimental_get_query_params()
url_assistant_id = url_params.get('Id', [None])[0]
url_thread_id = url_params.get('ThreadId', [None])[0]

def generate_thread_id():
    return "Mocero_" + str(uuid.uuid4())

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"
    
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'thread_id' not in st.session_state:
    st.session_state.thread_id = url_thread_id or generate_thread_id()

if st.sidebar.button("### New Chat &nbsp; 💬"):
    st.session_state.thread_id = generate_thread_id()
    st.session_state.messages = []
    st.experimental_set_query_params(Id=url_assistant_id, ThreadId=st.session_state.thread_id)
# st.sidebar.write("Thread ID:", st.session_state.thread_id)
    

def load_and_display_history(url_assistant_id):
    side_binding_data = {"ChatAssistanceId": url_assistant_id, "DML_Indicator": "LD"}
    data_response = requests.post("https://spandanvideo.convenientcare.life/api/ChatGptThread/ManageThreadDetails", data=side_binding_data)
    if data_response.status_code == 200:
        try:
            history_response = data_response.json()
            sorted_table = sorted(history_response["data"]["Table"], key=lambda x: x["Created_on"], reverse=True)
            for data in sorted_table:
                if st.sidebar.button(data["Details"], key=data["Thread_Id"]):
                    handle_thread_click(data["Thread_Id"])
        except json.JSONDecodeError:
            st.sidebar.error("Error decoding JSON response.")
    # else:
    #     st.sidebar.error("Error fetching data: HTTP Status " + str(data_response.status_code))

def handle_thread_click(thread_id):
    st.experimental_set_query_params(Id=url_assistant_id, ThreadId=thread_id)
    api_request_data = {
        "Thread_Id": thread_id,
        "Dml_Indicator": "DS"
    }
    response = requests.post("https://spandanvideo.convenientcare.life/api/ChatGptThread/ManageThreadDetails", data=api_request_data)
    if response.status_code == 200:
        try:
            response_data = response.json()
            for data in response_data["data"]["Table"]:
                if data["Role"] == 0:
                    with st.chat_message("user"):
                        st.markdown(data["Details"])
                elif data["Role"] == 1:
                    with st.chat_message("assistant"):
                        st.markdown(data["Details"])
        except json.JSONDecodeError:
            st.error("Error decoding JSON response.")
    else:
        st.error("Error making API request: HTTP Status " + str(response.status_code))

load_and_display_history(url_assistant_id)

if prompt := st.chat_input("What is up?"):
    st.experimental_set_query_params(Id=url_assistant_id, ThreadId=url_thread_id)
    api_request_data = {
        "Thread_Id": url_thread_id,
        "Dml_Indicator": "DS"
    }
    response = requests.post("https://spandanvideo.convenientcare.life/api/ChatGptThread/ManageThreadDetails", data=api_request_data)
    if response.status_code == 200:
        try:
            response_data = response.json()
            for data in response_data["data"]["Table"]:
                if data["Role"] == 0:
                    with st.chat_message("user"):
                        st.markdown(data["Details"])
                elif data["Role"] == 1:
                    with st.chat_message("assistant"):
                        st.markdown(data["Details"])
        except json.JSONDecodeError:
            st.error("Error decoding JSON response.")
    # else:
    #     st.error("Error making API request: HTTP Status " + str(response.status_code))

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    if url_thread_id:
        user_data = {"DML_Indicator": "DI","Thread_Id": url_thread_id,"Thread": "Sample Thread","Details": prompt,"Role": 0,'ChatAssistanceId':url_assistant_id}
    else:
        user_data = {"DML_Indicator": "DI","Thread_Id": st.session_state.thread_id,"Thread": "Sample Thread","Details": prompt,"Role": 0,'ChatAssistanceId':url_assistant_id}
    requests.post("https://spandanvideo.convenientcare.life/api/ChatGptThread/ManageThreadDetails", data=user_data)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            chunk = response.choices[0].delta.content
            if chunk is not None:
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    if url_thread_id:
        assistant_data = {"DML_Indicator": "DI","Thread_Id": url_thread_id,"Thread": "Sample Thread","Details": full_response,"Role": 1,'ChatAssistanceId':url_assistant_id}
    else:
        assistant_data = {"DML_Indicator": "DI","Thread_Id": st.session_state.thread_id,"Thread": "Sample Thread","Details": full_response,"Role": 1,'ChatAssistanceId':url_assistant_id}
    print("assistant_data :",assistant_data)
    requests.post("https://spandanvideo.convenientcare.life/api/ChatGptThread/ManageThreadDetails", data=assistant_data)

    
# for message in reversed(st.session_state.messages):
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])