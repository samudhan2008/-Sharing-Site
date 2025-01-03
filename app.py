from flask import Flask, request, jsonify, send_file
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# MongoDB Configuration
MONGO_URI = "your_mongo_connection_string"
client = MongoClient(MONGO_URI)
db = client['notesDB']
notes_collection = db['notes']

# File upload configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for uploading notes
@app.route('/upload', methods=['POST'])
def upload_note():
    if 'file' not in request.files or 'title' not in request.form:
        return jsonify({'error': 'Title and file are required'}), 400

    file = request.files['file']
    title = request.form['title']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Save metadata to MongoDB
        note = {
            'title': title,
            'filename': filename,
            'file_path': file_path
        }
        result = notes_collection.insert_one(note)

        return jsonify({'message': 'Note uploaded successfully', 'note_id': str(result.inserted_id)}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400

# Route to list all notes
@app.route('/notes', methods=['GET'])
def get_notes():
    notes = []
    for note in notes_collection.find():
        notes.append({
            'id': str(note['_id']),
            'title': note['title']
        })
    return jsonify(notes), 200

# Route to download a note
@app.route('/download/<note_id>', methods=['GET'])
def download_note(note_id):
    note = notes_collection.find_one({'_id': ObjectId(note_id)})
    if note:
        return send_file(note['file_path'], as_attachment=True)
    else:
        return jsonify({'error': 'Note not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
