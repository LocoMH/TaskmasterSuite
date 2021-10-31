from tinydb import TinyDB, Query
from tm_suite import helper
import ujson

contestants = TinyDB(helper.find_root() + "/sources/db/contestants.json")
tasks = TinyDB(helper.find_root() + "/sources/db/tasks.json")
scores = TinyDB(helper.find_root() + "/sources/db/scores.json")
general_files = TinyDB(helper.find_root() + "/sources/db/general_files.json")


async def add_general_file(name: str, file_source: str, file_type: str, text: str):

    general_file = {
        "name": name,
        "file_source": file_source,
        "file_type": file_type
    }

    if text != "":
        general_file["text"] = text

    return general_files.insert(general_file)


async def remove_general_file(name: str):
    general_files.remove(Query().name == name)


async def get_scores():
    return scores.all()


async def get_general_files():
    return general_files.all()


async def add_contestant(name: str, file_source: str):
    return contestants.insert({
        "name": name,
        "file_source": file_source
    })


async def remove_contestant(name: str):
    id = contestants.search(Query().name == name)[0].doc_id
    contestants.remove(Query().name == name)
    scores.remove(Query().contestantId == id)


async def remove_task(name: str):
    id = tasks.search(Query().name == name)[0].doc_id
    tasks.remove(Query().name == name)
    scores.remove(Query().taskId == id)


async def get_scores_by_contestant_id(contestantId):
    result = scores.search(Query().contestantId == contestantId)
    return result


async def get_tasks():
    result = [{
        "id": t.doc_id,
        "name": t["name"],
        "files": t["files"]
    } for t in tasks]
    return result


async def get_raw_tasks():
    return tasks.all()


async def get_raw_contestants():
    return contestants.all()


async def get_contestants():
    result = [{
        "id": c.doc_id,
        "name": c["name"],
        "file_source": c["file_source"]
    } for c in contestants]
    return result


async def get_contestants_with_total_score():
    result = [{
        "id": c.doc_id,
        "name": c["name"],
        "file_source": c["file_source"],
        "total_score": await get_total_score(c.doc_id)
    } for c in contestants]
    return result


async def get_total_score(contestantId):
    return sum(score["score"] for score in scores.all()
               if score["contestantId"] == contestantId)


async def add_task(name, files):
    return tasks.insert({
        "name": name,
        "files": files
    })


async def update_task(name, files):
    tasks.update({
        "files": files
    }, Query().name == name)


async def update_note_text(name, text):
    general_files.update({
        "text": text
    }, Query().name == name)


async def get_task_by_id(id):
    return tasks.get(doc_id=id)


async def add_score(taskId, contestantId, score):

    contestantId = int(contestantId)
    taskId = int(taskId)
    score = float(score)

    scores.upsert({
        "taskId": taskId,
        "contestantId": contestantId,
        "score": score
    }, (Query().taskId == taskId) & (Query().contestantId == contestantId))


async def clear_tasks():
    await clear_scores()
    tasks.truncate()


async def clear_contestants():
    await clear_scores()
    contestants.truncate()


async def clear_scores():
    scores.truncate()
