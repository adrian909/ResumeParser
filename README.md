# Resume Parser App (Gen AI + Flask)

### Objective

Creating a resume parser app using Flask is a great way to help job seekers test the ATS (Applicant Tracking System) friendliness of their resumes. The app allows users to upload their resumes in PDF format, which are then parsed to extract various pieces of information such as full name, email ID, GitHub portfolio, LinkedIn ID, employment details, technical skills, and soft skills. The extracted information is then presented in JSON format, providing users with valuable insights into the effectiveness of their resumes.

To build such an app, you can leverage various tools and libraries, including Python, Flask, Pyresparser, pdfminer.six, docx2txt, and NLP (natural language processing) libraries such as nltk and spacy. These tools enable the extraction of essential information from resumes in PDF and DOCx formats, making the process automated and efficient.

The app's functionality aligns with the growing need for streamlined recruitment processes and the increasing reliance on technology to evaluate and process job applications. By providing users with a detailed analysis of their resumes, the app empowers job seekers to optimize their resumes for better visibility and compatibility with ATS.

### Sneak Peak of the App
![image](https://github.com/pik1989/Resume-Parser-OpenAI/assets/34673684/5d206207-1b25-4dbe-8e11-add701b632e7)

#### Overview: 
This App is created for job seekers to test whether their resumes are ATS friendly or not, if our App is able to parse your details and show it, then assume that everything is good.

#### Features: 
Ability to extract specific information from resumes, the use of JSON format for presenting the extracted data, and the integration of various libraries and tools for parsing resumes.

#### Installation: 
Run the pip install requirements.txt to install and set up the app, including any dependencies and prerequisites.

#### Usage: 
Just upload your resume in pdf format, and see for yourself :)


##### Running the program

1. Clone the repository to your local machine
2. Navigate to the project directory
3. Install all the required libraries (just run pip install -r /path/to/requirements.txt)
4. Provide your Ollama Cloud API key (https://ollama.com/settings/keys) in `config.yaml` as `OLLAMA_API_KEY`, or set the `OLLAMA_API_KEY` environment variable
5. Run the following command to start the chatbot -

    ```
    python app.py
    ```

    ```
    Go to: https://localhost:8000
    ```

### API

`POST /api/parse` — send the resume PDF as the multipart field `file`.

```
curl -F "file=@resume.pdf" https://<your-app>/api/parse
```

From the browser (CORS is enabled for `/api/*`):

```js
const form = new FormData();
form.append("file", fileInput.files[0]);

const res = await fetch("https://<your-app>/api/parse", { method: "POST", body: form });
const json = await res.json();
if (json.success) console.log(json.data);
else console.error(json.error);
```

By default any website may call the API. To restrict it, set the `ALLOWED_ORIGINS` environment variable to a comma separated list, e.g. `https://mysite.com,http://localhost:3000`.

Success (`200`):

```json
{
  "success": true,
  "data": {
    "full_name": "Maria Popescu",
    "email": "maria.popescu@example.com",
    "phone": "+40 721 123 456",
    "location": "Cluj-Napoca, Romania",
    "github": "https://github.com/mpopescu",
    "linkedin": "https://linkedin.com/in/maria-popescu",
    "employment": [
      {
        "company": "Endava",
        "position": "Senior Backend Developer",
        "location": "Cluj",
        "start_date": "2022-03",
        "end_date": null,
        "is_current": true,
        "description": "Built payment microservices in Python and FastAPI."
      }
    ],
    "education": [
      {
        "institution": "Babes-Bolyai University",
        "degree": "BSc",
        "field_of_study": "Computer Science",
        "start_date": "2015",
        "end_date": "2019"
      }
    ],
    "technical_skills": ["Python", "FastAPI", "PostgreSQL"],
    "soft_skills": ["leadership", "communication"],
    "languages": [{ "name": "English", "proficiency": "C1" }]
  }
}
```

Every field is always present. Missing values are `null` (or `[]` for lists). Dates are `YYYY-MM` or `YYYY`.

Errors return `{"success": false, "error": "<message>"}` with status:

| Status | Meaning |
|--------|---------|
| 400 | No `file` field, or the file is not a valid PDF |
| 422 | The PDF has no extractable text (e.g. a scanned image) |
| 502 | The AI service failed; retry later |
    
Overall, the development of a resume parser app using Flask represents a significant advancement in leveraging technology to support job seekers in optimizing their resumes for the modern recruitment landscape. This app aligns with the increasing demand for efficient and technology-driven solutions in the job application process, ultimately benefiting both job seekers and recruiters.
