import os
from tm_suite import helper
from tm_suite import db
import ujson


def check_for_contestants(root: str):
    files = [f for f in os.listdir(
        root + "/data/contestants") if f.endswith((".jpg", ".png", ".jpeg"))]

    newContestants = [{
        "name": file.rsplit(".", 1)[0],
        "img_source": file
    } for file in files]

    oldContestants = db.get_raw_contestants()

    for contestant in newContestants:
        if not any(contestant["name"] == oldContestant["name"] for oldContestant in oldContestants):
            db.add_contestant(contestant["name"], contestant["img_source"])

    for contestant in oldContestants:
        if not any(contestant["name"] == newContestant["name"] for newContestant in newContestants):
            db.remove_contestant(contestant["name"])


def check_for_tasks(root: str):
    files = [f.rsplit(".", 1)[0] for f in os.listdir(
        root + "/data/tasks")]

    newTasks = [{
        "name": task,
        "images": [
            img for img in os.listdir(root + "/data/tasks/" + task) if img.endswith((".png", ".jpg", ".jpeg"))
        ],
        "videos": [
            video for video in os.listdir(root + "/data/tasks/" + task) if video.endswith(".mp4")
        ]
    } for task in files]

    oldTasks = db.get_raw_tasks()

    for task in newTasks:
        if not any(task["name"] == oldTask["name"] for oldTask in oldTasks):
            db.add_task(task["name"], task["images"], task["videos"])

    for task in oldTasks:
        if not any(task["name"] == newTask["name"] for newTask in newTasks):
            db.remove_task(task["name"])

    for task in newTasks:
        db.update_task(task["name"], task["images"], task["videos"])


def check_for_special_images(root: str):
    files = [f for f in os.listdir(
        root + "/data") if f.endswith((".jpg", ".png", ".jpeg"))]

    newSpecialImages = [{
        "name": img.rsplit(".", 1)[0].capitalize(),
        "img_source": img
    } for img in files]

    oldSpecialImages = db.get_special_images()

    for special_image in newSpecialImages:
        if not any(special_image["name"] == oldSpecialImage["name"] for oldSpecialImage in oldSpecialImages):
            db.add_special_image(
                special_image["name"], special_image["img_source"])

    for special_image in oldSpecialImages:
        if not any(special_image["name"] == newSpecialImage["name"] for newSpecialImage in newSpecialImages):
            db.remove_special_image(special_image["name"])


def generate_files():
    root = helper.find_root()
    if root is None:
        print("error - could not find root directory which includes 'data' directory!")
    else:
        check_for_contestants(root)
        check_for_tasks(root)
        check_for_special_images(root)


if __name__ == "__main__":
    generate_files()
