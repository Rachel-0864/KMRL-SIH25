from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pytesseract
from PIL import Image
import io
import os
import csv

app = Flask(__name__)
CORS(app)  # ✅ allows frontend to talk to backend from any origin

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/api/process", methods=["POST"])
def process_document():
    if "files" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    all_text = []
    saved_files = []

    for file in request.files.getlist("files"):
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        saved_files.append(file_path)

        try:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img, lang="eng+mal")
            all_text.append(text)
        except Exception as e:
            all_text.append(f"[Error reading {file.filename}: {e}]")

    combined_text = "\n".join(all_text)

    # 🔹 Very basic summarization (you can replace with NLP model later)
    summary = " ".join(combined_text.split()[:50]) + "..." if len(combined_text) > 50 else combined_text

    # 🔹 Save as CSV (just a single column with text)
    csv_path = os.path.join(UPLOAD_FOLDER, "extracted_text.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Extracted Text"])
        for line in combined_text.splitlines():
            writer.writerow([line])

    return jsonify({
        "summary": summary,
        "csv_url": f"/download/extracted_text.csv"
    })

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
