from flask import Flask, render_template, send_file, jsonify, request, redirect
from flask_socketio import SocketIO
import os
from pathlib import Path
import mimetypes
import time
from threading import Thread
import json
from clip_db import get_sessions_from_db, delete_clip_record, get_clip_by_filename
from network_utils import get_wifi_status, connect_wifi, enable_hotspot, forget_network
from file_utils import wait_for_files_written
from datetime import datetime
import subprocess
import uuid

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

BASE_PATH = Path(__file__).parent.parent
CLIPS_DIR = BASE_PATH / "clips"
TRIMMED_DIR = BASE_PATH / "trimmed"

_event_bus = None
_state_machine = None

def get_sessions_with_metadata():
    """Get sessions with metadata for each clip from the database."""
    db_sessions = get_sessions_from_db()
    sessions_with_metadata = []

    for session in db_sessions:
        session_clips = []
        for clip in session:
            file_path = CLIPS_DIR / clip["filename"]
            if file_path.exists():
                session_clips.append({
                    'filename': clip["filename"],
                    'path': str(file_path),
                    'size': file_path.stat().st_size,
                    'created_at': clip["created_at"].isoformat(),
                    'resolution_preset': clip.get("resolution_preset"),
                    'duration': clip.get("duration"),
                })
        if session_clips:
            sessions_with_metadata.append(session_clips)

    return sessions_with_metadata

def monitor_clips_directory():
    """Monitor the clips directory for changes and emit updates via DB."""
    last_state = set()
    while True:
        current_files = set(f.name for f in CLIPS_DIR.glob("*.mp4"))
        if current_files != last_state:
            new_files = current_files - last_state
            wait_for_files_written([str(CLIPS_DIR / f) for f in new_files])
            sessions = get_sessions_with_metadata()
            socketio.emit('clips_update', json.dumps(sessions))
            last_state = current_files
        time.sleep(1)

@app.route('/')
def homepage():
    return render_template('home.html')


@app.route('/api/bot/status')
def bot_status():
    if not _state_machine:
        return jsonify({'state': 'unknown'})
    return jsonify({'state': _state_machine.state.name})


@app.route('/api/bot/action', methods=['POST'])
def bot_action():
    from event_bus import EventType
    if not _event_bus:
        return jsonify({'error': 'Bot not initialized'}), 500

    action = request.json.get('action')
    actions = {
        'start': EventType.SLACK_START,
        'stop': EventType.SLACK_STOP,
        'clip': EventType.SLACK_CLIP,
        'poke': EventType.POKE,
    }
    event_type = actions.get(action)
    if not event_type:
        return jsonify({'error': 'Unknown action'}), 400

    _event_bus.emit(event_type)
    return jsonify({'status': 'ok'})


@app.route('/clips')
def clips_page():
    sessions = get_sessions_with_metadata()
    return render_template('index.html', sessions=sessions)


@app.route('/clips/file/<path:filename>')
def serve_clip(filename):
    return send_file(
        CLIPS_DIR / filename,
        mimetype=mimetypes.guess_type(filename)[0]
    )


@app.route('/api/clips')
def api_clips():
    return jsonify(get_sessions_with_metadata())


@app.route('/api/clips/<path:filename>', methods=['DELETE'])
def api_delete_clip(filename):
    file_path = CLIPS_DIR / filename
    if not file_path.exists() and not get_clip_by_filename(filename):
        return jsonify({'error': 'File not found'}), 404
    try:
        if file_path.exists():
            file_path.unlink()
        delete_clip_record(filename)
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/clips/view/<path:filename>')
def view_clip(filename):
    """View a specific video clip with details."""
    file_path = CLIPS_DIR / filename
    if not file_path.exists():
        return "Video not found", 404

    clip = get_clip_by_filename(filename)
    created = clip["created_at"] if clip else datetime.fromtimestamp(file_path.stat().st_mtime)
    size = file_path.stat().st_size

    sessions = get_sessions_with_metadata()
    current_session = None
    session_index = None

    for i, session in enumerate(sessions):
        if any(c['filename'] == filename for c in session):
            current_session = session
            session_index = i
            break

    return render_template('view.html',
                         filename=filename,
                         size=size,
                         modified=created,
                         resolution_preset=clip.get("resolution_preset") if clip else None,
                         duration=clip.get("duration") if clip else None,
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
            'download_url': f'/clips/file/{filename}'
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


@app.route('/api/snapshot', methods=['POST'])
def api_snapshot():
    from video_utils import capture_frame
    try:
        capture_frame()
        return jsonify({'status': 'ok', 'ts': time.time()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/snapshot')
def serve_snapshot():
    snapshot = BASE_PATH / 'snapshot.jpg'
    if not snapshot.exists():
        return 'No snapshot', 404
    return send_file(snapshot, mimetype='image/jpeg')


@app.route('/config')
def config_page():
    return render_template('config.html')


@app.route('/api/config')
def api_config_get():
    from camera_config import read_config, EDITABLE_FIELDS, _get_field_value, PRESETS, get_current_preset
    cfg = read_config()
    fields = []
    for key, field in EDITABLE_FIELDS.items():
        fields.append({
            'key': key,
            'label': field['label'],
            'type': field['type'],
            'value': _get_field_value(cfg, key),
        })
    timeout_hours = _state_machine.inactivity_timeout / 3600 if _state_machine else None
    return jsonify({
        'fields': fields,
        'presets': list(PRESETS.keys()),
        'current_preset': get_current_preset(cfg),
        'timeout_hours': timeout_hours,
    })


@app.route('/api/config/preset', methods=['POST'])
def api_config_preset():
    from camera_config import apply_preset
    from event_bus import State
    if _state_machine and _state_machine.state != State.IDLE:
        return jsonify({'error': 'Stop recording before changing preset.'}), 400

    data = request.json
    name = data.get('preset', '')
    try:
        apply_preset(name)
        return jsonify({'status': 'ok'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/config', methods=['POST'])
def api_config_update():
    from camera_config import update_field, EDITABLE_FIELDS
    from event_bus import State
    if _state_machine and _state_machine.state != State.IDLE:
        return jsonify({'error': 'Stop recording before editing config.'}), 400

    data = request.json
    key = data.get('key', '')
    value = data.get('value', '')

    if key not in EDITABLE_FIELDS:
        return jsonify({'error': f'Unknown config key: {key}'}), 400

    try:
        update_field(key, str(value))
        return jsonify({'status': 'ok'})
    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/config/timeout', methods=['POST'])
def api_config_timeout():
    data = request.json
    try:
        hours = float(data.get('value', ''))
        if hours <= 0:
            return jsonify({'error': 'Timeout must be positive.'}), 400
        if _state_machine:
            _state_machine.inactivity_timeout = hours * 3600
            _state_machine.save_timeout()
        return jsonify({'status': 'ok'})
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid value.'}), 400


@app.route('/api/config/reset', methods=['POST'])
def api_config_reset():
    from camera_config import reset_config
    from event_bus import State
    if _state_machine and _state_machine.state != State.IDLE:
        return jsonify({'error': 'Stop recording before resetting config.'}), 400

    reset_config()
    return jsonify({'status': 'ok'})


@app.route('/api/temperature')
def api_temperature():
    try:
        result = subprocess.run(
            ['vcgencmd', 'measure_temp'],
            capture_output=True, text=True, timeout=5
        )
        temp = result.stdout.strip().replace("temp=", "").replace("'C", "")
        return jsonify({'temp': float(temp)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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


@app.route('/cert')
def download_cert():
    cert = BASE_PATH / "cert.pem"
    if cert.exists():
        return send_file(cert, download_name='highlight-bot.pem', as_attachment=True)
    return 'No certificate configured', 404


def init_web_server(event_bus=None, state_machine=None):
    global _event_bus, _state_machine
    _event_bus = event_bus
    _state_machine = state_machine

    monitor_thread = Thread(target=monitor_clips_directory, daemon=True)
    monitor_thread.start()

    ssl_ctx = None
    cert = BASE_PATH / "cert.pem"
    key = BASE_PATH / "key.pem"
    if cert.exists() and key.exists():
        ssl_ctx = (str(cert), str(key))

    socketio.run(app, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True, ssl_context=ssl_ctx)

if __name__ == "__main__":
    init_web_server() 