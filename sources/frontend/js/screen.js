/*
 * Yes, this code isn't great, but it's small and works even in IE10.
 * I wasn't configuring babel/webpack for a one off fun project.
 */

(function() {
	var contestantsList = []

	// var main = document.querySelector("#div-scoreboard")

	function addContestant(imagePath, id, score) {
		var contestant = {}

		contestant.image = imagePath
		contestant.score = score
		contestant.oldScore = score
        contestant.id = id

		contestantsList.push(contestant)

		return contestantsList.length
	}

	function createContestantEl(con, id) {
		var el = document.createElement("div")
		el.classList.add("contestant")

		var frameScaler = document.createElement("div")
		frameScaler.classList.add("frame-scaler")

		var frameContainer = document.createElement("div")
		frameContainer.classList.add("frame-container")
		frameContainer.style.webkitAnimationDelay = -id * 1.25 + "s"
		frameContainer.style.animationDelay = -id * 1.25 + "s"

		var fill = document.createElement("div")
		fill.classList.add("fill")
		fill.style.backgroundImage = "url('" + con.image + "')"

		var shadow = document.createElement("div")
		shadow.classList.add("shadow")

		var frame = document.createElement("img")
		frame.src = "./data/backgrounds/contestant_frame.png"
		frame.classList.add("frame")
		frame.removeAttribute("width")
		frame.removeAttribute("height")

		fill.appendChild(shadow)
		frameContainer.appendChild(fill)
		frameContainer.appendChild(frame)

		frameScaler.appendChild(frameContainer)

		var scoreContainer = document.createElement("div")
		scoreContainer.classList.add("score-container")

		var seal = document.createElement("img")
		seal.classList.add("seal")
		seal.src = "./data/backgrounds/seal.png"
		seal.removeAttribute("width")
		seal.removeAttribute("height")

		var score = document.createElement("h1")
		score.classList.add("score")
		score.innerText = con.oldScore

		scoreContainer.appendChild(seal)
		scoreContainer.appendChild(score)
		
		el.appendChild(frameScaler)
		el.appendChild(scoreContainer)

		return el;
	}

	function transformContestants() {

		contestantsList = contestantsList.sort(function(first, second) {
            return first.score - second.score
		})

		var maxScore = contestantsList[contestantsList.length - 1].score
		var maxCount = 1

		for (var i = contestantsList.length - 1; i > 0; --i) {
			var con = contestantsList[i-1]
			if (con.score == maxScore) {
				++maxCount
			}
		}

		for (var i = 0, l = contestantsList.length; i < l; ++i) {
			var con = contestantsList[i]

			con.el.style.msTransform = "translateX(" + (275 * i + 30) + "px)"
			con.el.style.transform = "translateX(" + (275 * i + 30) + "px)"

			if (con.score == maxScore) {
				if (maxCount > 2) {
					con.el.children[0].classList.remove("larger")
					con.el.children[0].classList.add("large")
				} else {
					con.el.children[0].classList.remove("large")
					con.el.children[0].classList.add("larger")
				}
			} else {
				con.el.children[0].classList.remove("large")
				con.el.children[0].classList.remove("larger")
			}
		}
	}

	function refreshContestants() {
        var innerScoreboard = document.querySelector("#inner-scoreboard")
        
        innerScoreboard.innerHTML = ""

		for (var i = contestantsList.length; i > 0; --i) {
			var con = contestantsList[i-1]

			var cEl = createContestantEl(con, i)
			con.el = cEl
		}

		if (contestantsList.length > 0) transformContestants();
		
		for (var i = contestantsList.length; i > 0; --i) {
			var con = contestantsList[i-1]
			innerScoreboard.appendChild(con.el)
		}

        innerScoreboard.style.width = 275 * contestantsList.length + "px"

	}

	function ease(t, a, b) {
		var eased = t < .5 ? 2 * t * t : -1 + (4 - 2 * t) * t
		return (b - a) * eased + a
	}

	function play() {

		setTimeout(function() {
			var start = 0;
			var loop = function(dt) {
				if (start == 0) {
					start = dt
				}
	
				for (var i = 0, l = contestantsList.length; i < l; ++i) {
					var con = contestantsList[i]
	
					var startRemainder = con.oldScore - Math.floor(con.oldScore)
					var endRemainder = con.score - Math.floor(con.score)
	
					var scoreEl = con.el.querySelector(".score")
	
					var score = Math.round(ease(Math.min((dt - start) / 2000, 1), Math.floor(con.oldScore), Math.floor(con.score)))
	
					if (dt - start < 1000) {
						score += startRemainder
					} else {
						score += endRemainder
					}
	
					scoreEl.innerText = (score.toFixed(3) * 1)
				}
	
				if (dt - start < 2000) {
					window.requestAnimationFrame(loop)
				} else {
					for (var i = 0, l = contestantsList.length; i < l; ++i) {
						var con = contestantsList[i]
						con.oldScore = con.score
					}
				}
			};
	
			window.requestAnimationFrame(loop)
			transformContestants()
		}, 10)
	}

    var contestants = []

    function getContestants() {
        var xhttp = new XMLHttpRequest()
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                contestants = JSON.parse(this.responseText)
                contestants.sort((a, b) => a.name.localeCompare(b.name))
                contestants.sort((a, b) => b["total_score"] - a["total_score"])
                contestants.forEach(contestant => {
                    addContestant("./data/contestants/" + contestant["file_source"], contestant["id"], contestant["total_score"])
                })
            
                refreshContestants()
            }
        }
        xhttp.open("GET", "/data/contestants_with_total_score", false)
        xhttp.send()
    }

    function getGeneralFiles() {
        var xhttp = new XMLHttpRequest()
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                general_files = JSON.parse(this.responseText)
            }
        }
        xhttp.open("GET", "/data/general_files", false)
        xhttp.send()
    }
    
    getContestants()
    getGeneralFiles()

    document.querySelector("#image-taskmaster").src = "./data/" + general_files.find(file => {
        return file.name.toLowerCase() == "taskmaster"
    }).file_source

    function showDiv(name) {
        document.querySelector("#div-" + name).style.display = "block"
        document.querySelectorAll(".div-containers").forEach(cont => {
            if (!cont.id.includes(name) && !cont.id.includes("taskmaster")) {
                cont.style.display = "none"
            }
        })
        if (name != "video") {
            document.querySelector("#video").pause()
        }
    }

    var ws = new ReconnectingWebSocket("ws://" + window.location.host + "/ws")
    ws.onmessage = function(event) {
        console.log("received msg '" + event.data + "'")
        var content = event.data.split("+++")
        var action = content[0]
        if (action == "play") {
            play()
        } else if (action == "setScore") {
            contestantsList.find(c => c.id == content[2]).score = content[4]
        } else if (action == "showImage") {
            document.querySelector("#image").src = content[1]
            showDiv("image")
        } else if (action == "showScoreboard") {
            showDiv("scoreboard")
        } else if (action == "showVideo") {

            document.querySelector("#video-src").setAttribute('src', content[1])

            document.querySelector("#video").load()
            document.querySelector("#video").currentTime = 0
            document.querySelector("#video").play()

            document.getElementById('video').addEventListener('ended', function(e) {
                showDiv("taskmaster")
            }, false)

            document.getElementById('video').addEventListener('playing', function(e) {
                showDiv("video")
            }, false)
            
        } else if (action == "showTaskmaster") {
            showDiv("taskmaster")
        }
    }

    function resize() {
        var divScoreboard2 = document.querySelector("#div-scoreboard-2")
        var divTaskmaster = document.querySelector("#inner-taskmaster")
		var w = window.innerWidth
		var h = window.innerHeight

		var wm = 1400 * ((contestants.length + (0.25)) / 5)

		var m = Math.min(w / wm, h / 1080)
        var m2 = h / 1080 * 1.25

		divScoreboard2.style.msTransform = "scale(" + m + ")"
		divScoreboard2.style.transform = "scale(" + m + ")"

        divTaskmaster.style.transform = "scale(" + m2 + ")"
        divTaskmaster.style.msTransform = "scale(" + m2 + ")"
	}

	window.addEventListener("resize", resize)
	resize()
})()