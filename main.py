"Gemini Credits Needed"

import google.generativeai as genai
import json
import dataclasses
import typing_extensions as typing
import os

# config genAI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# upload sample file
sample_file = genai.upload_file(path="GreenScreen/IPCC_AR6_SYR_SPM.pdf", display_name="Sample Paper")
file = genai.get_file(name=sample_file.name)

"""
This function's aim is to filter the generated questions by groundedness, relevance, and standalone qualities.
"""
def filter_question(question, context, prompt_type):
    # Define the prompt based on the type
    if prompt_type == 'groundedness':
        prompt = f"""
        You will be given a context and a question.
        Your task is to score how well the question can be answered with the given context.
        Give your answer on a scale of 1 to 5, where 1 means not answerable at all and 5 means clearly answerable.

        Question: {question}
        Context: {context}
        Answer:::
        """
    elif prompt_type == 'relevance':
        prompt = f"""
        You will be given a question.
        Your task is to rate how useful this question is for someone trying to understand the underlying message of the paper.
        Rate it from 1 to 5.

        Question: {question}
        Answer:::
        """
    elif prompt_type == 'standalone':
        prompt = f"""
        You will be given a question.
        Rate how independent this question is, meaning if it makes sense without additional context.
        Rate from 1 to 5.

        Question: {question}
        Answer:::
        """

    # Call the model
    model = genai.GenerativeModel("gemini-2.0-flash-exp", generation_config={"response_mime_type": "text/plain"})
    response = model.generate_content(prompt)
    return response.text


# # config model 
# model = genai.GenerativeModel("gemini-2.0-flash-exp", generation_config={"response_mime_type": "application/json"})
# prompt = """List 100 very specific question answer pairs based on this file's contents using this JSON schema:

# QA = {'Question': str, 'Answer': str}
# Return: list[QA]"""

# perform filteration using separate model

# save as json file 
# raw_response = model.generate_content([prompt, sample_file])
# response = json.loads(raw_response.text)
# print("Creating QA bank file. . .\n")
# with open('QA_bank.json', 'w') as f:
#     json.dump(response, f, indent=4)
with open('QA_bank.json', 'r') as f:
    # file_contents = f.read()
    data = json.load(f)
counter = 0

# parse and filter questions
for item in data: 
    question = item['Question']
    prompt_type = 'groundedness'
    print(filter_question(question, file, prompt_type))
    counter += 1
    if counter == 5: break
    


