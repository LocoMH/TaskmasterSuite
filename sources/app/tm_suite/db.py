from tinydb import TinyDB, Query
from tm_suite import helper
import ujson

contestants = TinyDB(helper.find_root() + "/sources/db/contestants.json")
tasks = TinyDB(helper.find_root() + "/sources/db/tasks.json")
scores = TinyDB(helper.find_root() + "/sources/db/scores.json")
special_images = TinyDB(helper.find_root() + "/sources/db/special_images.json")


async def add_special_image(name: str, img_source: str):
    return special_images.insert({
        "name": name,
        "img_source": img_source
    })


async def remove_special_image(name: str):
    special_images.remove(Query().name == name)


async def get_scores():
    return scores.all()


async def get_special_images():
    return special_images.all()


async def add_contestant(name: str, img_source: str):
    return contestants.insert({
        "name": name,
        "img_source": img_source,
        "total_score": 0
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
        "images": t["images"],
        "videos": t["videos"]
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
        "total_score": c["total_score"],
        "img_source": c["img_source"],
        "scores": await get_scores_by_contestant_id(c.doc_id)
    } for c in contestants]
    return result


async def add_task(name, images, videos):
    return tasks.insert({
        "name": name,
        "images": images,
        "videos": videos
    })


async def update_task(name, images, videos):
    tasks.update({
        "images": images,
        "videos": videos
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

    contestants.update({
        "total_score": sum([score["score"] for score in scores.search(Query().contestantId == contestantId)])
    }, doc_ids=[contestantId])


async def get_total_score(contestantId):
    return contestants.get(doc_id=contestantId)["total_score"]


async def clear_tasks():
    await clear_scores()
    tasks.truncate()


async def clear_contestants():
    await clear_scores()
    contestants.truncate()


async def clear_scores():
    scores.truncate()
    contestants.update({"total_score": 0})
