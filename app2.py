from flask import Flask, request, jsonify
import PyPDF2
import os

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "API running", "usage": "/upload (POST pdf file)"})

@app.route("/upload", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty file name"}), 400

    try:
        reader = PyPDF2.PdfReader(file)

        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return jsonify({
            "text": text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
