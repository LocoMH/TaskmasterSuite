import socket
import os


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def find_root():
    current_root = "."

    for _ in range(0, 5):
        files = [f for f in os.listdir(current_root)]
        if "data" in files:
            return current_root
        else:
            current_root += "/.."
