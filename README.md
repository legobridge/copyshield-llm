# Copyshield LLM Chatbot

A chatbot that assesses its input/output for copyright infringement.

The user input is vetted for requests for copyrighted material, before being sent to the primary chat LLM. This is done using a secondary LLM call. 

The generated output is compared (using BM25 search) against an offline text corpus to check for plagiarism. The corpus used here is the top ~4k books on Project Gutenberg.

Any warnings are appended to the response of the LLM. If the user blatantly requests for copyrighted material, the request is denied and no call is made to the primary chat LLM.

The first time you run the app, it will be slow, since it needs to build the BM25 corpus.

## Instructions

Use Python >= 3.9.18

Install the requirements:

```pip install -r requirements.txt```

Export your OpenAI API Key:

```export OPENAI_API_KEY="<>"```

Run the Streamlit app:

```streamlit run copyshield_app.py```
