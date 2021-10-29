new Vue({
    el: '#app',
    vuetify: new Vuetify({
        theme: { dark: true },
    }),        
    data() {
        return {
            darkMode: true,
            selectedTask: {
                id: -1,
                name: "-",
                images: [],
                videos: []
            },
            resetDialog: false,
            special_images: [],
            tasks: [],
            contestants: [],
            scores: [],
            internalScores: {},
            totalScores: {},
            websocket: null,
            websocketConnected: false,
            ranks: {},
            tm: null
        }
    },
    filters: {
        removeExtension(val) {
            return val.replace(/\.[^/.]+$/, "")
        },
        replaceNewLines(val) {
            return val.replaceAll("\n", "<br>")
        }
    },
    methods: {
        showImage(image) {
            this.sendMessage("showImage+++" + image)
        },
        createInternalScores() {
            this.internalScores = {}
            
            this.tasks.forEach(task => {
                this.internalScores[task.id] = {}
                this.contestants.forEach(contestant => {
                    this.internalScores[task.id][contestant.id] = 0
                })
            })
            
            this.scores.forEach(score => {
                this.internalScores[score.taskId][score.contestantId] = score.score
            })

        },
        updateTotalScore() {
            this.totalScores = {}

            this.contestants.forEach(contestant => {
                this.totalScores[contestant.id] = 0
            })

            for (var taskId in this.internalScores) {
                for (var contestantId in this.internalScores[taskId]) {
                    this.totalScores[contestantId] += parseFloat(this.internalScores[taskId][contestantId])
                    this.totalScores[contestantId] = (this.totalScores[contestantId].toFixed(3) * 1)
                }
            }

            // this.ranks = Object.keys(this.totalScores).map(function(key) {
            //     return [key, this.totalScores[key]]
            // })

            // this.ranks.sort(function(first, second) {
            //     return second[1] - first[1]
            // })

            // console.log(this.ranks)
        },
        sendMessage(message) {
            if (this.websocketConnected) {
                console.log(" sending msg: " + message)
                this.websocket.send(message)
            }
        },
        resetScores() {
            axios.delete('/data/scores')
            .then(response => { 
                this.resetDialog = false
                this.loadScores()
            })
        },
        loadTasks() {
            axios
            .get('/data/tasks')
            .then(response => {

                var isEqual = response.data.length === this.tasks.length

                if (isEqual) {
                    for (var i in this.tasks) {
                        var oldTask = this.tasks[i]
                        if (!response.data.some(t => JSON.stringify(t) == JSON.stringify(oldTask))) {
                            isEqual = false
                            break
                        }
                    }
                }

                if (!isEqual) {
                    this.tasks = response.data

                    var newSelectedTask = this.tasks.filter(t => t.id == this.selectedTask.id)
                    if (newSelectedTask.length === 0) {
                        this.selectedTask = {
                            "id": -1,
                            "name": "-",
                            "images": [],
                            "videos": []
                        }
                    } else {
                        this.selectedTask = newSelectedTask[0]
                    }
                }
            })
            .catch(e => {})
            .then(() => {
                setTimeout(() => this.loadTasks(), 1000)
            })
        },
        loadContestants() {
            axios.get("/data/contestants")
            .then(response => {

                var isEqual = response.data.length === this.contestants.length

                if (isEqual) {
                    for (var i in this.contestants) {
                        var oldContestant = this.contestants[i]
                        if (!response.data.some(c => c.id === oldContestant.id)) {
                            isEqual = false
                            break
                        }
                    }
                }

                if (!isEqual) {
                    this.contestants = response.data
                }
            })
            .catch(e => {})
            .then(() => {
                setTimeout(() => this.loadContestants(), 1000)
            })
        },
        loadSpecialImages() {
            axios.get("/data/special_images")
            .then(response => {
                this.special_images = response.data
            })
            .catch(e => {})
            .then(() => {
                setTimeout(() => this.loadSpecialImages(), 1000)
            })
        },
        loadScores() {
            axios.get("/data/scores")
            .then(response => {
                this.scores = response.data
                this.createInternalScores()
                this.updateTotalScore()
            })
            .catch(e => {})
        },
        connectToWebsocket() {
            this.websocket = new ReconnectingWebSocket("ws://" + location.hostname + ":8001/ws")

            this.websocket.onopen = () => {
                console.log('websocket connected')
                this.websocketConnected = true
            }
                
            this.websocket.onclose = (event) => {
                console.log('websocket disconnected')
                this.websocketConnected = false
            }
        },
        ping() {
            this.sendMessage('__ping__');
            this.tm = setTimeout(function () {}, 5000)
        },
        pong() {
            clearTimeout(this.tm)
        },
        selectTask() {

        },
        getScore(taskId, contestantId) {
            var filteredScores = this.scores.filter(s => (s.taskId == taskId) && (s.contestantId == contestantId))
            var score = 0
            if (filteredScores.length != 0) {
                score = filteredScores[0].score
            }
            return score
        },
        setScore(taskId, contestantId, score) {
            this.internalScores[taskId][contestantId] = score
            this.updateScore(taskId, contestantId)
        },
        updateScore(taskId, contestantId) {
            var score = this.internalScores[taskId][contestantId]
            if (score !== '') {
                this.updateTotalScore()
                this.sendMessage("setScore+++" + taskId + "+++" + contestantId + "+++" + score + "+++" + this.totalScores[contestantId])
            }                    
        }
    },
    beforeMount() {
        this.loadTasks()
        this.loadContestants()
        this.loadScores()
        this.loadSpecialImages()
        this.connectToWebsocket()
    },
    watch: {
        darkMode(val) {
            this.$vuetify.theme.dark = val
        },
        tasks() {
            this.createInternalScores()
            this.updateTotalScore()
        },
        contestants() {
            this.createInternalScores()
            this.updateTotalScore()
        }
    },
    computed: {
        filteredSpecialImages() {
            return this.special_images.filter(img => img.name.toLowerCase() != "taskmaster")
        }
    }
})