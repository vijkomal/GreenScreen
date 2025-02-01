import google.generativeai as genai
import json
import dataclasses
import typing_extensions as typing
import os
import time
from time import sleep
from tqdm import tqdm

# progress bar 
for i in tqdm(range(10)):
    sleep(3)

# config genAI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# upload sample file
sample_file = genai.upload_file(path="GreenScreen/data/IPCC_SPM_2019.pdf", display_name="Sample Paper")
file = genai.get_file(name=sample_file.name)

# config model 
model = genai.GenerativeModel("gemini-2.0-flash-exp", generation_config={"response_mime_type": "application/json"})
prompt = """List 70 very specific multiple choice questions (with three answers) and the answer itself (where the answer is the number corresponding to the option choice) based on this file's contents. 
Ask questions that are directly relevant to the overall message of the file. They should be relevant to the topic and related to climate change. Someone should learn something useful and relevant from 
this question. Do not ask about the authors at all or about particular page numbers. We want questions about the actual content related to climate change. For example, 
"what would Deep,  rapid,  and  sustained  reductions  in  greenhouse  gas  emissions lead to?" Ensure that the answer is an integer. 
Use this JSON schema: Make sure every string is enclosed in quotes properly. 

QA = {'question': str, 'option_1': str, 'option_2': str, 'option_3': str, 'answer': int}
Return: list[QA]"""

# save as json file and create QA bank 
raw_response = model.generate_content([prompt, sample_file])
response = json.loads(raw_response.text)
output_file_title = 'QA_bank_2018_v2.json'
print("Creating QA bank file. . .\n")
with open(output_file_title, 'w') as f:
    json.dump(response, f, indent=4)

# open and read json file 
with open(output_file_title, 'r') as f:
    # file_contents = f.read()
    data = json.load(f)