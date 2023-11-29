ASSISTANT_ROLE_NAME = "assistant"
USER_ROLE_NAME = "user"

USER_PROMPT_INSPECTION_PROMPT_TEMPLATE = """You are a plagiarism detection AI.
Judge whether or not the following request (within triple backticks) to an LLM is asking for copyrighted material.
Request: ```{}```
Format your output as the following JSON object:
{{
    "explanation": "Explanation for why this request might be requesting copyrighted material",
     "plagiarismLevel": 0 if request doesn't request copyrighted material, 1 if it is somewhat likely to request copyrighted or public domain material, 2 only if there is a blatant request for exact replication of material from a certain known copyrighted source
}}
Output only a JSON object and nothing else."""