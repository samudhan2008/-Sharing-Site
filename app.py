from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "your-default-mongodb-connection-string")
client = MongoClient(MONGO_URI)
db = client["notes_db"]  # Database name
notes_collection = db["notes"]  # Collection name

@app.route("/")
def index():
    return "Welcome to Abhijeet's Notes Sharing Site!"

@app.route("/api/notes", methods=["GET"])
def get_notes():
    try:
        notes = list(notes_collection.find({}, {"_id": 0}))  # Exclude MongoDB's ObjectId
        return jsonify({"success": True, "notes": notes}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/notes", methods=["POST"])
def upload_note():
    try:
        # Parse the incoming data
        note_data = request.json
        title = note_data.get("title")
        content = note_data.get("content")

        if not title or not content:
            return jsonify({"success": False, "message": "Title and content are required."}), 400

        # Insert note into the database
        note = {"title": title, "content": content}
        notes_collection.insert_one(note)

        return jsonify({"success": True, "message": "Note uploaded successfully."}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    # Run the app, configured for Koyeb's environment
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
