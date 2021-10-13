import os
import json
import socket


def generate_contestants():
    files = [f for f in os.listdir(
        "../contestants") if f.endswith((".jpg", ".png", ".jpeg"))]

    print("generating contestants.js...")

    contestants = [{
        "name": file.rsplit(".", 1)[0],
        "filename": file,
        "newScore": 0,
        "score": 0
    } for file in files]

    output = "var contestants = " + json.dumps(contestants)

    f = open("../../js/contestants.js", "w")
    f.write(output)
    f.close()


def generate_tasks():
    files = [f.rsplit(".", 1)[0] for f in os.listdir(
        "../tasks")]

    print("generating tasks.js...")

    tasks = [{
        "name": task,
        "images": [
            img for img in os.listdir("../tasks/" + task) if img.endswith((".png", ".jpg", ".jpeg"))
        ],
        "videos": [
            video for video in os.listdir("../tasks/" + task) if video.endswith(".mp4")
        ]
    } for task in files]

    output = "var tasks = " + json.dumps(tasks)

    f = open("../../js/tasks.js", "w")
    f.write(output)
    f.close()


def generate_special_images():
    files = [f for f in os.listdir(
        "../") if f.endswith((".jpg", ".png", ".jpeg"))]

    print("generating special_images.js...")

    images = [{
        "name": img.rsplit(".", 1)[0].capitalize(),
        "filename": img
    } for img in files]

    output = "var special_images = " + json.dumps(images)

    f = open("../../js/special_images.js", "w")
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


def generate_ip_address():
    ip_address = get_ip()

    print("generating ip_address.js...")

    output = "var ip_address = \"" + ip_address + "\""

    f = open("../../js/ip_address.js", "w")
    f.write(output)
    f.close()


if __name__ == "__main__":
    print("starting to generate data files based on task directories and images...")
    generate_contestants()
    generate_tasks()
    generate_special_images()
    generate_ip_address()
    print("finished generating data files...")
    input("press Enter to finish...")
