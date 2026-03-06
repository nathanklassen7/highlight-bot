import json
import shutil
from video_utils import reinitialize_camera

CONFIG_FILE = "camera_config.json"
DEFAULT_CONFIG_FILE = "default_camera_config.json"

EDITABLE_FIELDS = {
    "fps": {"label": "FPS", "type": "int"},
    "bitrate": {"label": "Bitrate", "type": "int"},
    "buffer_duration": {"label": "Buffer Duration (s)", "type": "int"},
    "ExposureTime": {"label": "Exposure Time (µs)", "type": "int", "control": True},
    "AnalogueGain": {"label": "Analogue Gain", "type": "float", "control": True},
    "AeEnable": {"label": "Auto Exposure", "type": "bool", "control": True},
}


def read_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def write_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)
        f.write("\n")


def reset_config():
    shutil.copy(DEFAULT_CONFIG_FILE, CONFIG_FILE)
    reinitialize_camera()
    return read_config()


def update_field(key, value):
    cfg = read_config()
    field = EDITABLE_FIELDS[key]

    if field["type"] == "int":
        value = int(value)
    elif field["type"] == "float":
        value = float(value)
    elif field["type"] == "bool":
        value = value.lower() in ("true", "1", "yes", "on")

    if field.get("control"):
        cfg.setdefault("controls", {})[key] = value
    else:
        cfg[key] = value
        if key == "fps":
            cfg.setdefault("controls", {})["FrameRate"] = value

    write_config(cfg)
    reinitialize_camera()
    return cfg


def _get_field_value(cfg, key):
    field = EDITABLE_FIELDS[key]
    if field.get("control"):
        return cfg.get("controls", {}).get(key)
    return cfg.get(key)


def build_config_blocks():
    cfg = read_config()
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Camera Configuration"}
        }
    ]

    for key, field in EDITABLE_FIELDS.items():
        value = _get_field_value(cfg, key)
        display = str(value) if value is not None else "not set"
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{field['label']}*\n`{display}`"
            },
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "Edit"},
                "action_id": f"config-edit-{key}",
                "value": key,
            }
        })

    blocks.append({"type": "divider"})
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Reset to Defaults"},
                "action_id": "config-reset",
                "style": "danger",
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Dismiss"},
                "action_id": "config-dismiss",
            }
        ]
    })

    return blocks
