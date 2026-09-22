# import libraries

import os
import json
from typing import List, Optional
from ollama import Client, ResponseError
from pydantic import BaseModel, Field
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


# Standard output schema - every response has exactly these fields
class Employment(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = Field(None, description="YYYY-MM or YYYY")
    end_date: Optional[str] = Field(None, description="YYYY-MM or YYYY, null if current")
    is_current: bool = False
    description: Optional[str] = None

class Education(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = Field(None, description="YYYY-MM or YYYY")
    end_date: Optional[str] = Field(None, description="YYYY-MM or YYYY")

class Language(BaseModel):
    name: str
    proficiency: Optional[str] = Field(None, description="e.g. native, C1, fluent")

class Resume(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    github: Optional[str] = Field(None, description="Full URL")
    linkedin: Optional[str] = Field(None, description="Full URL")
    employment: List[Employment] = []
    education: List[Education] = []
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    languages: List[Language] = []

RESUME_SCHEMA = Resume.model_json_schema()


def ats_extractor(resume_data):
    """Parse resume text and return a dict matching the Resume schema."""

    if not api_key:
        raise RuntimeError("OLLAMA_API_KEY is not set. Add it in Vercel > Settings > Environment Variables and redeploy.")

    prompt = '''
    You are an AI bot designed to act as a professional for parsing resumes.
    Extract the information from the given resume into the provided JSON schema.
    Rules:
    - Use null for anything not present in the resume; never invent data.
    - Dates as "YYYY-MM" (or "YYYY" if only the year is known).
    - For a current job set end_date to null and is_current to true.
    - github and linkedin as full https:// URLs.
    - Employment and education ordered from most recent to oldest.
    - Use exactly the field names and types from this JSON schema:
    ''' + json.dumps(RESUME_SCHEMA)

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

    # Free tier models can be busy, rate limited or return invalid JSON
    # - fall back to the next one
    for model in MODELS:
        try:
            response = ollama_client.chat(
                        model=model,
                        messages=messages,
                        # Structured output - forces the model to follow the schema
                        format=RESUME_SCHEMA,
                        # Reasoning tokens are billed too - keep them minimal
                        think="low" if model.startswith("gpt-oss") else False,
                        options={"temperature": 0.0})
            resume = Resume.model_validate_json(_strip_fences(response.message.content))
            break
        except (ResponseError, ValueError) as e:
            last_error = e
    else:
        raise last_error

    return resume.model_dump()

def _strip_fences(text):
    # Models sometimes wrap the JSON in ```json fences - keep only the object
    start, end = text.find('{'), text.rfind('}')
    if start == -1 or end == -1:
        raise ValueError("Model returned no JSON")
    return text[start:end + 1]
