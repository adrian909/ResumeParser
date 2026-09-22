# FLASK APP - Run the app using flask --app app.py run
import os, sys
from flask import Flask, request, render_template, jsonify
from pypdf import PdfReader
from resumeparser import ats_extractor

sys.path.insert(0, os.path.abspath(os.getcwd()))


app = Flask(__name__)
app.json.sort_keys = False  # keep fields in schema order

# CORS for browser calls to /api/* - comma separated list, "*" allows any site
ALLOWED_ORIGINS = [o.strip() for o in os.environ.get('ALLOWED_ORIGINS', '*').split(',')]


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    if request.path.startswith('/api/') and origin:
        if '*' in ALLOWED_ORIGINS:
            response.headers['Access-Control-Allow-Origin'] = '*'
        elif origin in ALLOWED_ORIGINS:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Vary'] = 'Origin'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Max-Age'] = '86400'
    return response


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

    return render_template('index.html', data = data)

@app.route("/api/parse", methods=["POST"])
def api_parse():
    """Upload a PDF as multipart field "file" -> standardized resume JSON."""
    doc = request.files.get('file')
    if not doc or not doc.filename:
        return _api_error("Send the resume PDF as multipart/form-data field 'file'.", 400)

    try:
        text = _read_file_from_path(doc.stream)
    except Exception:
        return _api_error("The uploaded file is not a valid PDF.", 400)

    if not text.strip():
        return _api_error("No text found in the PDF (scanned image PDFs are not supported).", 422)

    try:
        data = ats_extractor(text)
    except Exception:
        app.logger.exception("Resume processing failed")
        return _api_error("The AI service failed to parse the resume. Try again later.", 502)

    return jsonify({"success": True, "data": data})

def _api_error(message, status):
    return jsonify({"success": False, "error": message}), status

def _read_file_from_path(path):
    reader = PdfReader(path)
    data = ""

    for page_no in range(len(reader.pages)):
        page = reader.pages[page_no]
        data += page.extract_text()

    return data


if __name__ == "__main__":
    app.run(port=8000, debug=True)
