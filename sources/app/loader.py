import os
import json
import helper

all_files = {
    "contestants": [],
    "tasks": [],
    "special_images": [],
    "ip_address": ""
}


def generate_file(root, data, filename):
    print("found changes in " + filename +
          ", generating " + filename + ".js...")
    output = "var " + filename + " = " + json.dumps(data)
    all_files[filename] = data
    f = open(root + "/sources/frontend/js/" + filename + ".js", "w")
    f.write(output)
    f.close()


def generate_contestants(root: str):
    files = [f for f in os.listdir(
        root + "/data/contestants") if f.endswith((".jpg", ".png", ".jpeg"))]

    contestants = [{
        "name": file.rsplit(".", 1)[0],
        "filename": file,
        "newScore": 0,
        "score": 0
    } for file in files]

    if all_files["contestants"] != contestants:
        generate_file(root, contestants, "contestants")


def generate_tasks(root: str):
    files = [f.rsplit(".", 1)[0] for f in os.listdir(
        root + "/data/tasks")]

    tasks = [{
        "name": task,
        "images": [
            img for img in os.listdir(root + "/data/tasks/" + task) if img.endswith((".png", ".jpg", ".jpeg"))
        ],
        "videos": [
            video for video in os.listdir(root + "/data/tasks/" + task) if video.endswith(".mp4")
        ]
    } for task in files]

    if all_files["tasks"] != tasks:
        generate_file(root, tasks, "tasks")


def generate_special_images(root: str):
    files = [f for f in os.listdir(
        root + "/data") if f.endswith((".jpg", ".png", ".jpeg"))]

    special_images = [{
        "name": img.rsplit(".", 1)[0].capitalize(),
        "filename": img
    } for img in files]

    if all_files["special_images"] != special_images:
        generate_file(root, special_images, "special_images")


def generate_ip_address(root: str):
    ip_address = helper.get_ip()

    if ip_address != all_files["ip_address"]:
        generate_file(root, ip_address, "ip_address")


def generate_files():
    root = helper.find_root()
    if root is None:
        print("error - could not find root directory which includes 'data' directory!")
    else:
        generate_contestants(root)
        generate_tasks(root)
        generate_special_images(root)
        generate_ip_address(root)


if __name__ == "__main__":
    generate_files()
