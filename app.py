from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import pymongo

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploaded_files'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MongoDB Connection
MONGO_URI = os.getenv('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI)
db = client['abhijeets_notes_db']
notes_collection = db['notes']

# Helper function for file type validation
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home_page():
    logo_url = os.getenv('TELEGRAPH_LOGO_URL', '')  # Get logo URL from environment variable
    return render_template('index.html', logo_url=logo_url)

@app.route('/upload')
def upload_page():
    logo_url = os.getenv('TELEGRAPH_LOGO_URL', '')
    return render_template('upload.html', logo_url=logo_url)

@app.route('/notes')
def notes_page():
    logo_url = os.getenv('TELEGRAPH_LOGO_URL', '')
    files = list(notes_collection.find({}, {"_id": 0, "filename": 1}))
    return render_template('notes.html', files=[f['filename'] for f in files], logo_url=logo_url)

@app.route('/api/upload-file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        notes_collection.insert_one({"filename": filename})  # Save the file metadata to MongoDB
        return jsonify({"success": True, "message": "File uploaded successfully", "filename": filename})

    return jsonify({"success": False, "message": "Invalid file type"}), 400

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Get the port from environment variable or use 5000 as default
    app.run(host='0.0.0.0', port=port)
