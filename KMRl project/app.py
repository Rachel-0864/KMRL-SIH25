
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract

# Set the Tesseract executable path explicitly - update according to your install location
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Admin\Downloads\tesseract.exe'
import fitz  # PyMuPDF
from flask_cors import CORS

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

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

# Use Sumy LexRank summarization
def make_summary(text, sentence_count=4):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary_sentences = summarizer(parser.document, sentence_count)
    summary = ' '.join(str(sentence) for sentence in summary_sentences)
    return summary

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
    if 'files' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['files']
    extracted_text = extract_text(file)
    summary = make_summary(extracted_text, sentence_count=6)  # Adjust number of sentences as needed
    return jsonify({"summary": summary})

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
    with app.app_context():
        db.create_all()
    app.run(debug=True)