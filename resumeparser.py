# import libraries

import os
from ollama import Client, ResponseError
import yaml

CONFIG_PATH = r"config.yaml"
OLLAMA_HOST = "https://ollama.com"
MODELS = ["gpt-oss:120b", "gpt-oss:20b", "gemma4:31b"]

# On Vercel the key comes from an environment variable; locally from config.yaml
api_key = os.environ.get('OLLAMA_API_KEY')

if not api_key and os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH) as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        api_key = data['OLLAMA_API_KEY']

def ats_extractor(resume_data):

    prompt = '''
    You are an AI bot designed to act as a professional for parsing resumes. You are given with resume and your job is to extract the following information from the resume:
    1. full name
    2. email id
    3. github portfolio
    4. linkedin id
    5. employment details
    6. technical skills
    7. soft skills
    Give the extracted information in json format only
    '''

    ollama_client = Client(
        host = OLLAMA_HOST,
        headers = {'Authorization': 'Bearer ' + api_key}
    )

    messages=[
        {"role": "system",
        "content": prompt},
        {"role": "user",
        "content": resume_data}
        ]

    # Free tier models can be busy or rate limited - fall back to the next one
    for model in MODELS:
        try:
            response = ollama_client.chat(
                        model=model,
                        messages=messages,
                        format="json",
                        options={"temperature": 0.0})
            break
        except ResponseError as e:
            last_error = e
    else:
        raise last_error

    data = response.message.content

    #print(data)
    return data
