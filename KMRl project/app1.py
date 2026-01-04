import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import subprocess

# Set the Tesseract executable path explicitly - update according to your install location
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Admin\Downloads\tesseract.exe'
import fitz  # PyMuPDF
from flask_cors import CORS

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'files.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)

def extract_text(file_storage):
    filename = file_storage.filename.lower()
    if filename.endswith(".txt"):
        return file_storage.read().decode(errors="ignore")
    elif filename.endswith(('.jpg', '.jpeg', '.png')):
        image = Image.open(file_storage)
        return pytesseract.image_to_string(image)
    elif filename.endswith('.pdf'):
        try:
            tmpfile = os.path.join(UPLOAD_FOLDER, secure_filename(file_storage.filename))
            file_storage.save(tmpfile)
            doc = fitz.open(tmpfile)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()  # Close document to release the file lock
            os.remove(tmpfile)
            return text
        except ImportError:
            return "PDF support not installed."
    else:
        return "No text extracted."

@app.route('/api/process', methods=['POST'])
def process():
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['files']

        print(f"Processing file: {file.filename}")

        extracted_text = extract_text(file)
        print(f"Extracted text length: {len(extracted_text) if extracted_text else 0}")

        if not extracted_text or extracted_text.strip() == "":
            return jsonify({"error": "No extractable text found in file"}), 400

        MAX_PROMPT_LENGTH = 3000  # Limit to first 3000 characters for large files
        limited_text = extracted_text[:MAX_PROMPT_LENGTH]

        prompt = (
            "Provide a concise summary of the following document in exactly two sentences. "
            "Do not include phrases like 'Here is the summary' or similar introductions. "
            "Only output the summary text.\n\n"
            f"{limited_text}\n\nSummary:"
        )

        print("Calling Ollama subprocess (run command)...")

        result = subprocess.run(
            ['ollama', 'run', 'gemma3:1b'],
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=300  # Increased timeout for processing longer docs
        )

        print(f"Ollama subprocess return code: {result.returncode}")
        print(f"Ollama stdout: {result.stdout}")
        print(f"Ollama stderr: {result.stderr}")

        if result.returncode != 0:
            return jsonify({"error": f"Ollama run error: {result.stderr}"}), 500

        summary = result.stdout.strip()
        return jsonify({"summary": summary})
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"Error in /api/process:\n{tb}")
        return jsonify({"error": f"Server error: {str(e)}", "traceback": tb}), 500

@app.route('/api/save', methods=['POST'])
def save():
    if 'files' not in request.files or 'summary' not in request.form:
        return jsonify({"error": "No file or summary part"}), 400
    file = request.files['files']
    summary = request.form['summary']

    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    record = UploadedFile(
        filename=filename,
        file_path=save_path,
        summary=summary,
        upload_time=datetime.utcnow()
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({"message": "Saved!", "id": record.id})

@app.route('/api/files', methods=['GET'])
def list_files():
    records = UploadedFile.query.order_by(UploadedFile.upload_time.desc()).all()
    files = []
    for rec in records:
        files.append({
            "id": rec.id,
            "filename": rec.filename,
            "summary": rec.summary,
            "upload_time": rec.upload_time.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify(files)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)

    with app.app_context():
        db.create_all()
    app.run(debug=False)