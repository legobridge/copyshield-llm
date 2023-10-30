import google.generativeai as palm
import streamlit as st

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
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Clear all messages
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]


st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


# Function for generating PaLM response.
def generate_palm_response():
    message_history = []
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            message_history.append("User: " + dict_message["content"])
        else:
            message_history.append("Assistant: " + dict_message["content"] + "\n\n")
    output = palm.chat(messages=message_history, temperature=temperature, top_p=top_p)
    print(output.filters)
    return output.last


# User-provided prompt
if prompt := st.chat_input(disabled=not palm_api_key):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_palm_response()
            if response is None:
                response = "Sorry, try asking differently"
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            print_out = full_response
            placeholder.markdown(print_out)
            # placeholder.markdown(copyright_msg)

    message = {"role": "assistant", "content": full_response}

    st.session_state.messages.append(message)
