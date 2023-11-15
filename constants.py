import google.generativeai as palm
from google.generativeai.types import SafetySettingDict, HarmCategory, HarmBlockThreshold

SAFETY_SETTINGS = []
for k in HarmCategory:
    SAFETY_SETTINGS.append({"category": k, "threshold": HarmBlockThreshold.BLOCK_NONE})

ASSISTANT_ROLE_NAME = "assistant"
USER_ROLE_NAME = "user"

INPUT_PROMPT_TEMPLATE = """You are a plagiarism detection AI.
Judge whether or not the following request (within triple backticks) to an LLM is asking for copyrighted material.
Request: ```{}```
Format your output as the following JSON object:
{{
    "explanation": "Explanation for why this request might be requesting copyrighted material",
     "plagiarismLevel": 0 if request doesn't request copyrighted material, 1 if it is somewhat likely to request copyrighted or public domain material, 2 only if there is a blatant request for exact replication of material from a certain known copyrighted source
}}
Output only a JSON object and nothing else."""

OUTPUT_PROMPT_TEMPLATE = """You are a plagiarism detection AI.
Judge whether or not the following text within triple backticks has copyrighted or plagiarised material.
Text: ```{}```
Format your output as the following JSON object:
{{
    "explanation": "Explanation for why this might or might not be copyright infringement",
     "levelOfPlagiarism": 0 if no plagiarism, 1 if some plagiarism, 2 if a lot of plagiarism
}}
Output only a JSON object and nothing else."""