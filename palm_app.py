import google.generativeai as palm
import streamlit as st

from constants import ASSISTANT_ROLE_NAME, USER_ROLE_NAME, SAFETY_SETTINGS, INPUT_PROMPT_TEMPLATE


# App title
st.set_page_config(page_title="🌴💬 PaLM 2 Chatbot")

# Replicate Credentials
with st.sidebar:
    st.title('LGAI490 - Copyright Infringement in Generative Text Outputs')
    st.write('This chatbot is created using the PaLM 2 LLM model from Google.')
    st.success('Proceed to entering your prompt message!', icon='👉')

    st.subheader('Models and parameters')
    palm_api_key = st.text_input('PaLM API Key')
    temperature = st.sidebar.slider('temperature', min_value=0.00, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    # max_length = st.sidebar.slider('max_length', min_value=32, max_value=1024, value=1024, step=8)


if palm_api_key is not None:
    palm.configure(api_key=palm_api_key)

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


# TODO: extract the explanation and return it
def get_input_plagiarism_level():
    input_prompt = INPUT_PROMPT_TEMPLATE.format(st.session_state.messages[-1]["content"])
    output = palm.generate_text(prompt=input_prompt,
                                temperature=0.0,
                                safety_settings=SAFETY_SETTINGS)
    print(output.filters)
    output_text = output.candidates[0]["output"]
    print(output_text)
    if '"confidenceLevel": 0' in output_text:
        return 0
    if '"confidenceLevel": 1' in output_text:
        return 1
    if '"confidenceLevel": 2' in output_text:
        return 2
    return 0


# Function for generating PaLM response.
def generate_palm_chat_response():
    message_history = []
    for dict_message in st.session_state.messages:
        if dict_message["role"] == USER_ROLE_NAME:
            message_history.append("User: " + dict_message["content"])
        else:
            message_history.append("Assistant: " + dict_message["content"] + "\n\n")
    output = palm.chat(messages=message_history, temperature=temperature, top_p=top_p)
    print(output.filters)
    return output.last


# User-provided prompt
if prompt := st.chat_input(disabled=not palm_api_key):
    st.session_state.messages.append({"role": USER_ROLE_NAME, "content": prompt})
    with st.chat_message(USER_ROLE_NAME):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != ASSISTANT_ROLE_NAME:

    with st.chat_message(ASSISTANT_ROLE_NAME):
        with st.spinner("Thinking..."):
            request_plagiarism_level = get_input_plagiarism_level()
            if request_plagiarism_level < 2:
                response = generate_palm_chat_response()
                if response is None:
                    response = "Sorry, the prompt was blocked. Try asking differently"
                copyright_msg = "\n\nYour request may have requested copyrighted material" if request_plagiarism_level == 1 else ""
                response += copyright_msg
            else:
                response = "You have requested copyrighted material, please try again"
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)

    message = {"role": ASSISTANT_ROLE_NAME, "content": full_response}

    st.session_state.messages.append(message)
