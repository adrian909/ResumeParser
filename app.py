# FLASK APP - Run the app using flask --app app.py run
import os, sys
from flask import Flask, request, render_template
from pypdf import PdfReader 
import json
from resumeparser import ats_extractor

sys.path.insert(0, os.path.abspath(os.getcwd()))


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route("/process", methods=["POST"])
def ats():
    doc = request.files.get('pdf_doc')
    if not doc or not doc.filename:
        return render_template('index.html', error = "Choose a PDF file first.")

    try:
        # Read the PDF in memory - Vercel's filesystem is read-only
        data = _read_file_from_path(doc.stream)
        data = ats_extractor(data)
    except Exception as e:
        app.logger.exception("Resume processing failed")
        return render_template('index.html', error = str(e)), 500

    return render_template('index.html', data = json.loads(data))

def _read_file_from_path(path):
    reader = PdfReader(path)
    data = ""

    for page_no in range(len(reader.pages)):
        page = reader.pages[page_no] 
        data += page.extract_text()

    return data 


if __name__ == "__main__":
    app.run(port=8000, debug=True)

