from flask import Flask, render_template, send_file, jsonify, request
from flask_socketio import SocketIO
import os
from pathlib import Path
import mimetypes
import time
from threading import Thread
import json
from file_management.get_sessions import get_sessions
from network_utils import get_wifi_status, connect_wifi, enable_hotspot, forget_network
from datetime import datetime
import subprocess
import uuid

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

BASE_PATH = Path(__file__).parent.parent
CLIPS_DIR = BASE_PATH / "clips"
TRIMMED_DIR = BASE_PATH / "trimmed"

def get_clips():
    """Get list of video clips with their metadata."""
    clips = []
    print(f"Clips directory: {CLIPS_DIR.absolute()}")
    for file in CLIPS_DIR.glob("*.mp4"):
        clips.append({
            'filename': file.name,
            'path': str(file),
            'size': file.stat().st_size,
            'modified': file.stat().st_mtime
        })
    return sorted(clips, key=lambda x: x['modified'], reverse=True)

def get_sessions_with_metadata():
    """Get sessions with metadata for each clip."""
    sessions = get_sessions()
    sessions_with_metadata = []
    
    for session in sessions:
        session_clips = []
        for filename in session:
            file_path = CLIPS_DIR / filename
            if file_path.exists():
                session_clips.append({
                    'filename': filename,
                    'path': str(file_path),
                    'size': file_path.stat().st_size,
                    'modified': file_path.stat().st_mtime
                })
        if session_clips:  # Only add non-empty sessions
            sessions_with_metadata.append(session_clips)
    
    return sessions_with_metadata

def monitor_clips_directory():
    """Monitor the clips directory for changes and emit updates."""
    last_state = set()
    while True:
        current_files = set(f.name for f in CLIPS_DIR.glob("*.mp4"))
        if current_files != last_state:
            sessions = get_sessions_with_metadata()
            socketio.emit('clips_update', json.dumps(sessions))
            last_state = current_files
        time.sleep(1)  # Check every second

@app.route('/')
def index():
    """Render the main page with the list of clips."""
    sessions = get_sessions_with_metadata()
    return render_template('index.html', sessions=sessions)

@app.route('/clips/<path:filename>')
def serve_clip(filename):
    """Serve a video clip file."""
    return send_file(
        CLIPS_DIR / filename,
        mimetype=mimetypes.guess_type(filename)[0]
    )

@app.route('/api/clips')
def api_clips():
    """API endpoint to get list of clips."""
    return jsonify(get_sessions_with_metadata())

@app.route('/view/<path:filename>')
def view_clip(filename):
    """View a specific video clip with details."""
    file_path = CLIPS_DIR / filename
    if not file_path.exists():
        return "Video not found", 404
        
    # Get file metadata
    stats = file_path.stat()
    modified_time = datetime.fromtimestamp(stats.st_mtime)
    
    # Find which session this clip belongs to
    sessions = get_sessions_with_metadata()
    current_session = None
    session_index = None
    
    for i, session in enumerate(sessions):
        if any(clip['filename'] == filename for clip in session):
            current_session = session
            session_index = i
            break
    
    return render_template('view.html', 
                         filename=filename,
                         size=stats.st_size,
                         modified=modified_time,
                         session=current_session,
                         session_index=session_index)

@app.route('/trim/<path:filename>', methods=['POST'])
def trim_video(filename):
    """Trim a video file and return the trimmed version."""
    try:
        data = request.json
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if start_time is None or end_time is None or start_time >= end_time:
            return jsonify({'error': 'invalid start or end time'}), 400
        # Ensure trimmed directory exists
        TRIMMED_DIR.mkdir(exist_ok=True)
        
        # Generate unique filename for trimmed video
        trimmed_filename = f"temp_{filename}"
        input_path = CLIPS_DIR / filename
        output_path = CLIPS_DIR / trimmed_filename

        print(trimmed_filename)
        
        # Use ffmpeg to trim the video
        duration = end_time - start_time
        command = [
            'ffmpeg', '-y',
            '-i', str(input_path),
            '-ss', str(start_time),
            '-t', str(duration),
            '-c', 'copy',  # Copy streams without re-encoding
            str(output_path)
        ]
        
        subprocess.run(command, check=True, capture_output=True)

        # Delete original file and rename trimmed file to original name
        input_path.unlink()  # Delete the original file
        output_path.rename(input_path)  # Rename trimmed file to original name
        
        return jsonify({
            'download_url': f'/clips/{filename}'
        })
        
    except Exception as e:
        print(f"Error trimming video: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/clips/trimmed/<path:filename>')
def serve_trimmed_clip(filename):
    """Serve a trimmed video clip file."""
    return send_file(
        TRIMMED_DIR / filename,
        mimetype=mimetypes.guess_type(filename)[0]
    )


@app.route('/wifi')
def wifi_page():
    return render_template('wifi.html')


@app.route('/api/wifi/status')
def wifi_status():
    try:
        return jsonify(get_wifi_status())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/wifi/connect', methods=['POST'])
def wifi_connect():
    data = request.json
    ssid = data.get('ssid', '').strip()
    password = data.get('password', '').strip()

    if not ssid:
        return jsonify({'error': 'SSID is required'}), 400

    Thread(target=connect_wifi, args=(ssid, password), daemon=True).start()
    return jsonify({'status': 'connecting'})


@app.route('/api/wifi/hotspot', methods=['POST'])
def wifi_hotspot():
    try:
        enable_hotspot()
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/wifi/forget', methods=['POST'])
def wifi_forget():
    data = request.json
    ssid = data.get('ssid', '').strip()
    if not ssid or ssid == 'Hotspot':
        return jsonify({'error': 'Invalid network'}), 400
    try:
        forget_network(ssid)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def init_web_server():
    """Initialize and run the web server."""
    # Start the directory monitoring thread
    monitor_thread = Thread(target=monitor_clips_directory, daemon=True)
    monitor_thread.start()
    
    # Run the Flask app with SocketIO
    socketio.run(app, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    init_web_server() 