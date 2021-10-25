


var ws = new WebSocket("ws://" + window.location.host + "/ws")
// $('.custom-switch').bootstrapSwitch()

var scores = []
var contestants = []
var tasks = []

function getTasks() {
    var xhttp = new XMLHttpRequest()
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            tasks = JSON.parse(this.responseText)
            tasks.sort((a, b) => a.name.localeCompare(b.name))
        }
    }
    xhttp.open("GET", "/data/tasks", false)
    xhttp.send()
}

function getContestants() {
    var xhttp = new XMLHttpRequest()
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            contestants = JSON.parse(this.responseText)
            contestants.sort((a, b) => a.name.localeCompare(b.name))
        }
    }
    xhttp.open("GET", "/data/contestants", false)
    xhttp.send()
}

function getSpecialImages() {
    var xhttp = new XMLHttpRequest()
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            special_images = JSON.parse(this.responseText)
        }
    }
    xhttp.open("GET", "/data/special_images", false)
    xhttp.send()
}

function resetScores() {
    var xhttp = new XMLHttpRequest()
    xhttp.onreadystatechange = function() {
        window.location.reload(true)
    }
    xhttp.open("DELETE", "/data/scores", false)
    xhttp.send()
}

getSpecialImages()
getTasks()
getContestants()

function selectTask(id) {
    $("#selected-task").text("Selected Task: " + tasks[id - 1].name)
    $(".task-divs").hide()
    $("#task-div-" + id).show()
}


function setup() {

    special_images.forEach(img => {
        if (img.name.toLowerCase() != "taskmaster") {
            $("#div-basic-controls").append(" ").append('<button class="btn btn-primary special-button" onclick="showImage(event)" data-root="./data/' + img.img_source + '">Show ' + img.name + '</button>')
        }
    })


    var thead = $('<thead/>').appendTo($("#task-table"))
    var trow = $('<tr/>').appendTo(thead)
    $("#task-table").append(thead)
    var th1 = $("<th>Task</th>")
    trow.append(th1)
    var taskTableBody = $("<tbody/>")
    $("#task-table").append(taskTableBody)

    contestants.forEach(contestant => {
        trow.append("<th>" + contestant.name + "</th>")
    })


    tasks.forEach(task => {
        var taskRow = $("<tr/>")
        taskTableBody.append(taskRow)
        taskRow.append("<th scope='row'>" + task.name + "<br><button class='btn btn-primary btn-sm' type='button' onclick='selectTask(" + task["id"] + ")'>Media</button></th>")

        contestants.forEach(contestant => {
            var taskScore = contestant["scores"].find(s => s.taskId == task["id"])
            if (typeof taskScore === "undefined") {
                taskScore = 0
            } else {
                taskScore = taskScore["score"]
            }
            taskRow.append("<td class='text-center'><input type='number' id='score-" 
            + task["id"] + "-" + contestant["id"] + "' value='" + taskScore + "' onchange='updateScore(" + task["id"] + ", " + contestant["id"] + ")' style='width: 50px'/><br><span id='buttons-" + task["id"] + "-" + contestant["id"] + "' class='buttons-span'></span></td>")
            for (var i = 1; i <= contestants.length; i++) {
                $("#buttons-" + task["id"] + "-" + contestant["id"]).append("<button class='btn btn-outline-primary quick-score-button' style='width: auto' onclick='setScore(" + task["id"] + ", " + contestant["id"] + ", " + i + ")'>" + i + "</button>")
            }
        })
    })


    $('<tfoot><tr id="table-footer"><td>Total</td></tr></tfoot>').appendTo($("#task-table"))

    contestants.forEach(contestant => {
        $("#table-footer").append("<td id='total-score-" + contestant["id"] + "'>" + contestant["total_score"] + "</td>")
    })

    tasks.forEach(task => {
        $("#task-selection").append("<div id='task-div-" + task["id"] + "' class='task-divs'></div>")
        task.images.forEach(img => {
            $("#task-div-" + task["id"]).append(" ").append("<image src='./data/tasks/" + task.name + "/" + img + "' data-root='./data/tasks/" + task.name + "/" + img + "' style='width: 192px; height: 108px; cursor: pointer'  class='img-thumbnail' onclick='showImage(event)'></image>")
        })
        task.videos.forEach(video => {
            $("#task-div-" + task["id"]).append(" ").append("<button class='btn btn-primary' onclick='showVideo(event)' data-root='./data/tasks/" + task.name + "/" + video + "'>Video: " + video + "</button>")
        })
    })
    $(".task-divs").hide()

}

function showImage(event) {
    sendMessage("showImage+++" + event.target.getAttribute("data-root"))
}

function showVideo(event) {
    sendMessage("showVideo+++" + event.target.getAttribute("data-root"))
}

function sendMessage(data) {
    ws.send(data)
}

ws.onmessage = function(event) {
    console.log("received msg: " + event.data)
}

ws.onopen = function(event) {
}

function play(event) {
    sendMessage("play")
}

function setScore(taskId, playerId, score) {
    $("#score-" + taskId + "-" + playerId).val(score)
    updateScore(taskId, playerId)
}

function updateScore(taskId, playerId) {
    var score = $("#score-" + taskId + "-" + playerId).val()
    if (score == "") {
        $("#score-" + taskId + "-" + playerId).val(0)
        score = 0
    }
    var newScore = 0
    tasks.forEach(task => {
        newScore += parseFloat(document.getElementById("score-" + task["id"] + "-" + (playerId)).value)
    })
    scores[playerId - 1] = newScore
    document.getElementById("total-score-" + playerId).innerText = newScore
    sendMessage("setScore+++" + taskId + "+++" + playerId + "+++" + score + "+++" + newScore)
}

setup()