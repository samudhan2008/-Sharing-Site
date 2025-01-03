from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__, template_folder="templates")
CORS(app)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "your-default-mongodb-connection-string")
client = MongoClient(MONGO_URI)
db = client["notes_db"]
notes_collection = db["notes"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/notes", methods=["GET"])
def get_notes():
    try:
        notes = list(notes_collection.find({}, {"_id": 0}))
        return jsonify({"success": True, "notes": notes}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/notes", methods=["POST"])
def upload_note():
    try:
        note_data = request.json
        title = note_data.get("title")
        content = note_data.get("content")

        if not title or not content:
            return jsonify({"success": False, "message": "Title and content are required."}), 400

        note = {"title": title, "content": content}
        notes_collection.insert_one(note)

        return jsonify({"success": True, "message": "Note uploaded successfully."}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/upload")
def upload_page():
    return render_template("upload.html")

@app.route("/notes")
def notes_page():
    return render_template("notes.html")
        

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
