import json
import os

import streamlit as st
from openai import OpenAI

from bm25 import BM25Scorer
from constants import ASSISTANT_ROLE_NAME, USER_ROLE_NAME, USER_PROMPT_INSPECTION_PROMPT_TEMPLATE


# App title
st.set_page_config(page_title="💬 No-Plagiarism GPT Chatbot")

# Session variables
api_key = os.environ["OPENAI_API_KEY"]
if 'open_ai_client' not in st.session_state:
    st.session_state['open_ai_client'] = OpenAI()
if 'bm25_scorer' not in st.session_state:
    st.session_state['bm25_scorer'] = BM25Scorer()

# Sidebar
with st.sidebar:
    st.title('LGAI490 - Copyright Infringement in Generative Text Outputs')
    st.write('This chatbot is using the GPT LLM model from OpenAI.')
    st.success('Proceed to entering your prompt message!', icon='👉')

    st.subheader('Models and parameters')
    model = st.sidebar.radio('model', options=["gpt-3.5-turbo-1106", "gpt-4-1106-preview"])
    temperature = st.sidebar.slider('temperature', min_value=0.00, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": ASSISTANT_ROLE_NAME, "content": "How may I assist you today?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Clear all messages
def clear_chat_history():
    st.session_state.messages = [{"role": ASSISTANT_ROLE_NAME, "content": "How may I assist you today?"}]


st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


def get_input_plagiarism_report():
    try:
        input_prompt = USER_PROMPT_INSPECTION_PROMPT_TEMPLATE.format(st.session_state.messages[-1]["content"])
        output = st.session_state['open_ai_client'].chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[{"role": "user",
                       "content": input_prompt}],
            temperature=0)
        output_text = output.choices[0].message.content
        print(output_text)
        output_json = json.loads(output_text)
        return output_json
    except BaseException as e:
        print(e)
        return {"explanation": "ERROR", "plagiarismLevel": 0}


# Function for generating GPT response.
def generate_gpt_chat_response():
    output = st.session_state['open_ai_client'].chat.completions.create(
        model=model,
        messages=st.session_state.messages,
        temperature=temperature, top_p=top_p)
    print(output)
    if output.choices[0].finish_reason == "content_filter":
        return None
    return output.choices[0].message.content


# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": USER_ROLE_NAME, "content": prompt})
    with st.chat_message(USER_ROLE_NAME):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != ASSISTANT_ROLE_NAME:

    with st.chat_message(ASSISTANT_ROLE_NAME):
        with st.spinner("Thinking..."):
            request_plagiarism_report = get_input_plagiarism_report()
            request_plagiarism_level = request_plagiarism_report["plagiarismLevel"]
            request_plagiarism_explanation = request_plagiarism_report["explanation"]

            response = ""
            copyright_msg = ""
            sus_source_message = ""

            if request_plagiarism_level == 2:
                # If the request is blatantly asking for copyrighted material, don't bother generating a chat response
                copyright_msg = "You have requested copyrighted material, please try again. " \
                                + request_plagiarism_explanation
            else:
                # Else, generate a response and evaluate it
                response = generate_gpt_chat_response()
                if response is None:
                    copyright_msg = "Sorry, the prompt was blocked by the LLM provider. Try asking differently."
                else:
                    if request_plagiarism_level == 1:
                        copyright_msg = "You may have requested copyrighted material. " \
                                        + request_plagiarism_explanation

                    suspected_source = st.session_state['bm25_scorer'].find_suspected_source_of_response(response)
                    if suspected_source is not None:
                        sus_source_message = f"Note: The generated text bears noticeable similarity to " \
                                             f"{suspected_source.title} by {suspected_source.author}."
            if copyright_msg != "":
                response += "\n\n*" + copyright_msg + "*"
            if sus_source_message != "":
                response += "\n\n*" + sus_source_message + "*"

            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)

    message = {"role": ASSISTANT_ROLE_NAME, "content": full_response}

    st.session_state.messages.append(message)
