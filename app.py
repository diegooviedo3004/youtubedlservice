# app.py
import os
import re
import subprocess
import tempfile
from flask import Flask, request, send_file, jsonify, abort

app = Flask(__name__)

# Configuration
API_KEY = os.environ.get('API_KEY', 'default-secure-key')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
YOUTUBE_REGEX = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/')

def require_api_key(view):
    def wrapped(*args, **kwargs):
        if request.headers.get('X-API-KEY') == API_KEY:
            return view(*args, **kwargs)
        abort(401)
    return wrapped

@app.route('/download', methods=['POST'])
@require_api_key
def download():
    # Validate content length
    if request.content_length > MAX_CONTENT_LENGTH:
        abort(413)

    data = request.get_json()
    url = data.get('url')

    if not url or not YOUTUBE_REGEX.match(url):
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_template = os.path.join(tmp_dir, '%(title)s.%(ext)s')
            cmd = [
                'yt-dlp',
                '-x',
                '--audio-format', 'mp3',
                '--audio-quality', '0',
                '--output', output_template,
                url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                app.logger.error(f"yt-dlp error: {result.stderr}")
                return jsonify({'error': 'Failed to process video'}), 500

            files = os.listdir(tmp_dir)
            if not files:
                return jsonify({'error': 'No file created'}), 500

            mp3_path = os.path.join(tmp_dir, files[0])
            return send_file(
                mp3_path,
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name=os.path.basename(mp3_path)
            )

    except subprocess.TimeoutExpired:
        app.logger.error("Download timed out")
        return jsonify({'error': 'Processing timeout'}), 504
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ != '__main__':
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
