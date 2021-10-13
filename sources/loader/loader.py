import os
import json
import socket


def generate_contestants(root: str):
    files = [f for f in os.listdir(
        root + "/data/contestants") if f.endswith((".jpg", ".png", ".jpeg"))]

    print("generating contestants.js...")

    contestants = [{
        "name": file.rsplit(".", 1)[0],
        "filename": file,
        "newScore": 0,
        "score": 0
    } for file in files]

    output = "var contestants = " + json.dumps(contestants)

    f = open(root + "/sources/frontend/js/contestants.js", "w")
    f.write(output)
    f.close()


def generate_tasks(root: str):
    files = [f.rsplit(".", 1)[0] for f in os.listdir(
        root + "/data/tasks")]

    print("generating tasks.js...")

    tasks = [{
        "name": task,
        "images": [
            img for img in os.listdir(root + "/data/tasks/" + task) if img.endswith((".png", ".jpg", ".jpeg"))
        ],
        "videos": [
            video for video in os.listdir(root + "/data/tasks/" + task) if video.endswith(".mp4")
        ]
    } for task in files]

    output = "var tasks = " + json.dumps(tasks)

    f = open(root + "/sources/frontend/js/tasks.js", "w")
    f.write(output)
    f.close()


def generate_special_images(root: str):
    files = [f for f in os.listdir(
        root + "/data") if f.endswith((".jpg", ".png", ".jpeg"))]

    print("generating special_images.js...")

    images = [{
        "name": img.rsplit(".", 1)[0].capitalize(),
        "filename": img
    } for img in files]

    output = "var special_images = " + json.dumps(images)

    f = open(root + "/sources/frontend/js/special_images.js", "w")
    f.write(output)
    f.close()


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


def generate_ip_address(root: str):
    ip_address = get_ip()

    print("generating ip_address.js...")

    output = "var ip_address = \"" + ip_address + "\""

    f = open(root + "/sources/frontend/js/ip_address.js", "w")
    f.write(output)
    f.close()


def find_root():
    current_root = "."

    for _ in range(0, 5):
        files = [f for f in os.listdir(current_root)]
        if "data" in files:
            return current_root
        else:
            current_root += "/.."


if __name__ == "__main__":
    root = find_root()
    if root is None:
        print("error - could not find root directory which includes 'data' directory!")
    else:
        print("starting to generate data files based on task directories and images...")
        generate_contestants(root)
        generate_tasks(root)
        generate_special_images(root)
        generate_ip_address(root)
        print("finished generating data files...")

input("press Enter to finish...")
