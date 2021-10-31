import os
from . import helper
from . import db
import ujson


ALLOWED_IMG_EXTENSIONS = (".jpg", ".png", ".jpeg", ".bmp", ".gif")
ALLOWED_VID_EXTENSIONS = (".mp4",)
ALLOWED_TXT_EXTENSIONS = (".txt",)
ALLOWED_SND_EXTENSIONS = (".mp3",)

ALL_ALLOWED_EXTENSIONS = ALLOWED_VID_EXTENSIONS + ALLOWED_IMG_EXTENSIONS + \
    ALLOWED_TXT_EXTENSIONS + ALLOWED_SND_EXTENSIONS


def get_file_type(filename):
    if filename.endswith(ALLOWED_IMG_EXTENSIONS):
        return "image"
    elif filename.endswith(ALLOWED_VID_EXTENSIONS):
        return "video"
    elif filename.endswith(ALLOWED_TXT_EXTENSIONS):
        return "note"
    elif filename.endswith(ALLOWED_SND_EXTENSIONS):
        return "sound"
    return "unknown"


async def check_for_contestants(root: str):
    files = [f for f in os.listdir(
        root + "/data/contestants") if f.endswith(ALLOWED_IMG_EXTENSIONS)]

    newContestants = [{
        "name": file.rsplit(".", 1)[0],
        "file_source": file
    } for file in files]

    oldContestants = await db.get_raw_contestants()

    for contestant in newContestants:
        if not any(contestant["name"] == oldContestant["name"] for oldContestant in oldContestants):
            await db.add_contestant(contestant["name"], contestant["file_source"])

    for contestant in oldContestants:
        if not any(contestant["name"] == newContestant["name"] for newContestant in newContestants):
            await db.remove_contestant(contestant["name"])


async def check_for_tasks(root: str):
    files = [f.rsplit(".", 1)[0] for f in os.listdir(
        root + "/data/tasks")]

    newTasks = [{
        "name": task,
        "files": [{
            "name": file.rsplit(".", 1)[0],
            "file_source": file,
            "file_type": get_file_type(file)
        } for file in os.listdir(root + "/data/tasks/" + task) if file.endswith(ALLOWED_IMG_EXTENSIONS + ALLOWED_VID_EXTENSIONS + ALLOWED_TXT_EXTENSIONS)]
    } for task in files]

    for task in newTasks:
        for file in task["files"]:
            if file["file_type"] == "note":
                file["text"] = open(root + "/data/tasks/" +
                                    task["name"] + "/" + file["file_source"], "r", encoding='utf8').read()

    oldTasks = await db.get_raw_tasks()

    for task in newTasks:
        if not any(task["name"] == oldTask["name"] for oldTask in oldTasks):
            await db.add_task(task["name"], task["files"])

    for task in oldTasks:
        if not any(task["name"] == newTask["name"] for newTask in newTasks):
            await db.remove_task(task["name"])

    for task in newTasks:
        await db.update_task(task["name"], task["files"])


async def check_for_general_files(root: str):
    files = [f for f in os.listdir(
        root + "/data") if f.endswith(ALLOWED_IMG_EXTENSIONS + ALLOWED_VID_EXTENSIONS + ALLOWED_TXT_EXTENSIONS)]

    newGeneralFiles = [{
        "name": file.rsplit(".", 1)[0],
        "file_source": file,
        "file_type": get_file_type(file)
    } for file in files]

    for file in newGeneralFiles:
        if file["file_type"] == "note":
            file["text"] = open(root + "/data/" +
                                file["file_source"], "r", encoding='utf8').read()
        else:
            file["text"] = ""

    oldGeneralFiles = await db.get_general_files()

    for general_file in newGeneralFiles:
        if not any(general_file["name"] == oldGeneralFile["name"] for oldGeneralFile in oldGeneralFiles):
            await db.add_general_file(
                general_file["name"], general_file["file_source"], general_file["file_type"], general_file["text"])

    for general_file in oldGeneralFiles:
        if not any(general_file["name"] == newGeneralFile["name"] for newGeneralFile in newGeneralFiles):
            await db.remove_general_file(general_file["name"])

    for file in newGeneralFiles:
        if file["file_type"] == "note":
            await db.update_note_text(file["name"], file["text"])


async def generate_files():
    root = helper.find_root()
    if root is None:
        print("error - could not find root directory which includes 'data' directory!")
    else:
        await check_for_contestants(root)
        await check_for_tasks(root)
        await check_for_general_files(root)


if __name__ == "__main__":
    generate_files()
