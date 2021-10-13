
var ws = new WebSocket("ws://" + ip_address + ":8001/ws")
// $('.custom-switch').bootstrapSwitch()

var scores = []


function getTaskRow() {

}

function selectTask(id) {
    $("#selected-task").text("Selected Task: " + tasks[id - 1].name)
    $(".task-divs").hide()
    $("#task-div-" + id).show()
}


function setup() {

    special_images.forEach(img => {
        if (img.name.toLowerCase() != "taskmaster") {
            $("#div-basic-controls").append(" ").append('<button class="btn btn-primary special-button" onclick="showImage(event)" data-root="./data/' + img.filename + '">Show ' + img.name + '</button>')
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


    var iTask = 1
    tasks.forEach(task => {
        var taskRow = $("<tr/>")
        taskTableBody.append(taskRow)
        taskRow.append("<th scope='row'>" + task.name + "<br><button class='btn btn-primary btn-sm' type='button' onclick='selectTask(" + iTask + ")'>Media</button></th>")

        var iContestant = 1
        contestants.forEach(contestant => {
            taskRow.append("<td class='text-center'><input type='number' id='score-" + iTask + "-" + iContestant + "' value='0' onchange='updateScore(" + iContestant + ")' style='width: 50px'/><br><span id='buttons-" + iTask + "-" + iContestant + "' class='buttons-span'></span></td>")
            for (var i = 1; i <= contestants.length; i++) {
                $("#buttons-" + iTask + "-" + iContestant).append("<button class='btn btn-outline-primary quick-score-button' style='width: auto' onclick='setScore(" + i + ", " + iTask + ", " + iContestant + ")'>" + i + "</button>")
            }
            iContestant++
        })


        iTask++
    })


    $('<tfoot><tr id="table-footer"><td>Total</td></tr></tfoot>').appendTo($("#task-table"))

    var iContestant = 1
    contestants.forEach(contestant => {
        $("#table-footer").append("<td id='total-score-" + iContestant + "'>0</td>")
        iContestant++
    })

    var iTask = 1
    tasks.forEach(task => {
        $("#task-selection").append("<div id='task-div-" + iTask + "' class='task-divs'></div>")
        task.images.forEach(img => {
            $("#task-div-" + iTask).append(" ").append("<image src='./data/tasks/" + task.name + "/" + img + "' data-root='./data/tasks/" + task.name + "/" + img + "' style='width: 192px; height: 108px; cursor: pointer'  class='img-thumbnail' onclick='showImage(event)'></image>")
        })
        task.videos.forEach(video => {
            $("#task-div-" + iTask).append(" ").append("<button class='btn btn-primary' onclick='showVideo(event)' data-root='./data/tasks/" + task.name + "/" + video + "'>Video: " + video + "</button>")
        })
        iTask++
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

function setScore(score, taskId, playerId) {
    $("#score-" + taskId + "-" + playerId).val(score)
    updateScore(playerId)
}

function updateScore(playerId) {
    console.log(playerId)
    var newScore = 0
    var iTask = 1
    tasks.forEach(task => {
        newScore += parseFloat(document.getElementById("score-" + iTask + "-" + (playerId)).value)
        iTask++
    })
    scores[playerId - 1] = newScore
    document.getElementById("total-score-" + playerId).innerText = scores[playerId - 1]
    sendMessage("setScore+++" + (playerId - 1) + "+++" + scores[playerId - 1])
}

setup()