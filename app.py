from flask import Flask, request, send_file, jsonify
from flask_httpauth import HTTPBasicAuth
import subprocess
import os
import uuid

app = Flask(__name__)
auth = HTTPBasicAuth()

# Hardcoded users (for learning purposes, consider using a secure method in production)
users = {"admin": "password"}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username
    return None

@app.route('/download', methods=['POST'])
@auth.login_required
def download():
    data = request.get_json()
    url = data.get("url")
    
    if not url:
        return jsonify({"error": "Missing URL parameter"}), 400
    
    filename = f"{uuid.uuid4()}.mp3"
    output_path = os.path.join("downloads", filename)
    
    os.makedirs("downloads", exist_ok=True)
    
    command = [
        "yt-dlp", "-x", "--audio-format", "mp3", "--output", output_path, url
    ]
    
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output_log = f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        with open("logs.txt", "a") as log_file:
            log_file.write(output_log + "\n")
    except subprocess.CalledProcessError as e:
        error_log = f"Error running yt-dlp:\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}"
        with open("logs.txt", "a") as log_file:
            log_file.write(error_log + "\n")
        return jsonify({"error": "Failed to download or convert video", "details": e.stderr}), 500
    
    return send_file(output_path, as_attachment=True, mimetype="audio/mpeg")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
