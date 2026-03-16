import subprocess
import time


HOTSPOT_NAME = 'Hotspot'


def get_wifi_status():
    result = subprocess.run(
        ['nmcli', '-t', '-f', 'NAME,TYPE,DEVICE', 'connection', 'show', '--active'],
        capture_output=True, text=True, timeout=5
    )
    connections = []
    for line in result.stdout.strip().split('\n'):
        if line:
            parts = line.split(':')
            if len(parts) >= 3:
                connections.append({'name': parts[0], 'type': parts[1], 'device': parts[2]})

    wifi_conn = next((c for c in connections if c['type'] == '802-11-wireless'), None)
    is_hotspot = wifi_conn and wifi_conn['name'] == HOTSPOT_NAME

    return {
        'mode': 'hotspot' if is_hotspot else ('connected' if wifi_conn else 'disconnected'),
        'ssid': wifi_conn['name'] if wifi_conn and not is_hotspot else None
    }


def connect_wifi(ssid, password=''):
    try:
        subprocess.run(
            ['sudo', 'nmcli', 'connection', 'down', HOTSPOT_NAME],
            capture_output=True, timeout=10
        )
        time.sleep(1)

        cmd = ['sudo', 'nmcli', 'device', 'wifi', 'connect', ssid]
        if password:
            cmd += ['password', password]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            enable_hotspot()
            return

        time.sleep(10)
        check = subprocess.run(
            ['nmcli', '-t', '-f', 'NAME,TYPE', 'connection', 'show', '--active'],
            capture_output=True, text=True, timeout=5
        )
        connected = any(
            ssid in line and '802-11-wireless' in line
            for line in check.stdout.strip().split('\n')
        )

        if not connected:
            enable_hotspot()

    except Exception:
        enable_hotspot()


def enable_hotspot():
    subprocess.run(
        ['sudo', 'nmcli', 'connection', 'up', HOTSPOT_NAME],
        capture_output=True, timeout=10
    )


def forget_network(ssid):
    subprocess.run(
        ['sudo', 'nmcli', 'connection', 'delete', ssid],
        capture_output=True, text=True, timeout=10
    )
