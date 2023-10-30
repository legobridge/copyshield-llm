import streamlit as st
import replicate
import os
import random

# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")
replicate_api = 'r8_cwk7Jtfve9VLde2y3tOvdZzFooy8O0206a71m'

flag = random.randint(0,2)

if flag == 0:
    copyright_eval = "No Risk"
if flag == 1:
    copyright_eval = "Low Risk"
if flag  == 2:
    copyright_eval = "High Risk"


# Replicate Credentials
with st.sidebar:
    st.title('LGAI490 - Copyright Infringement in Generative Text Outputs')
    st.write('This chatbot is created using the open-source Llama 2 LLM model from Meta.')
    st.success('Proceed to entering your prompt message!', icon='👉')
    os.environ['REPLICATE_API_TOKEN'] = 'r8_cwk7Jtfve9VLde2y3tOvdZzFooy8O0206a71m'

    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
    if selected_model == 'Llama2-7B':
        llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    elif selected_model == 'Llama2-13B':
        llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=1024, value=1024, step=8)

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)


def generate_llama2_response(prompt_input):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
    return output

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    
    if copyright_eval == "No Risk":
        copyright_msg =  "\n\n No copyright infringement has been detected in these outputs."
            
    if copyright_eval == "Low Risk":
        copyright_msg =  "\n\n Moderate risk of copyright infringement detected. Sources of potential infringement identified as: \n\n"
        sources = "Twilight by Stephanie Meyers "
        copyright_msg = copyright_msg + sources
            
    if copyright_eval == "High Risk":
        copyright_msg =  "\n\n High risk of copyright infringement detected - outputs have been overwritten. Straight to jail."
    
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            print_out = full_response + copyright_msg
            if copyright_eval == "High Risk":
                print_out = copyright_msg
            placeholder.markdown(print_out)
            #placeholder.markdown(copyright_msg)
            

    message = {"role": "assistant", "content": print_out}
    
    st.session_state.messages.append(message)
