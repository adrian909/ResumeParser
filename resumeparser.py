# import libraries

import os
import json
from ollama import Client, ResponseError
import yaml

CONFIG_PATH = r"config.yaml"
OLLAMA_HOST = "https://ollama.com"
# Cheapest first - Ollama Cloud bills per token and larger models cost more
MODELS = ["gpt-oss:20b", "nemotron-3-nano:30b", "gpt-oss:120b"]

# On Vercel the key comes from an environment variable; locally from config.yaml
api_key = os.environ.get('OLLAMA_API_KEY')

if not api_key and os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH) as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
        api_key = data['OLLAMA_API_KEY']

def ats_extractor(resume_data):

    if not api_key:
        raise RuntimeError("OLLAMA_API_KEY is not set. Add it in Vercel > Settings > Environment Variables and redeploy.")

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

    # Free tier models can be busy, rate limited or return empty/invalid JSON
    # - fall back to the next one
    for model in MODELS:
        try:
            response = ollama_client.chat(
                        model=model,
                        messages=messages,
                        format="json",
                        # Reasoning tokens are billed too - keep them minimal
                        think="low" if model.startswith("gpt-oss") else False,
                        options={"temperature": 0.0})
            data = _extract_json(response.message.content)
            break
        except (ResponseError, ValueError) as e:
            last_error = e
    else:
        raise last_error

    #print(data)
    return data

def _extract_json(text):
    # Models sometimes wrap the JSON in ```json fences - keep only the object
    start, end = text.find('{'), text.rfind('}')
    if start == -1 or end == -1:
        raise ValueError("Model returned no JSON")
    data = text[start:end + 1]
    json.loads(data)
    return data
