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
                files: []
            },
            resetDialog: false,
            general_files: [],
            tasks: [],
            contestants: [],
            scores: [],
            internalScores: {},
            totalScores: {},
            generalFileDialogs: {},
            selectedTaskFileDialogs: {},
            websocket: null,
            websocketConnected: false,
            ranks: {},
            scrollOptions: {
                duration: 200,
                offset: 0,
                easing: 'easeInOutCubic'
            }
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
        resetInternalScores() {
            for (tIndex in this.tasks) {
                var task = this.tasks[tIndex]
                if (!this.internalScores[task.id]) {
                    this.$set(this.internalScores, task.id, {})
                }
                for (cIndex in this.contestants) {
                    var contestant = this.contestants[cIndex]
                    if (!this.internalScores[task.id][contestant.id]) {
                        this.$set(this.internalScores[task.id], contestant.id, 0)
                    }
                }
            }
            this.updateInternalScores()
        },
        updateInternalScores() {
            this.scores.forEach(score => {
                if (this.internalScores[score.taskId]) {
                    this.$set(this.internalScores[score.taskId], score.contestantId, score.score)
                }
            })
            this.updateTotalScore()
        },
        updateTotalScore() {
            this.totalScores = {}

            this.contestants.forEach(contestant => {
                this.$set(this.totalScores, contestant.id, 0)
            })

            for (var taskId in this.internalScores) {
                for (var contestantId in this.internalScores[taskId]) {
                    this.totalScores[contestantId] += parseFloat(this.internalScores[taskId][contestantId])
                    this.totalScores[contestantId] = (this.totalScores[contestantId].toFixed(3) * 1)
                }
            }
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
                this.scores = []
                this.internalScores = {}
                this.resetInternalScores()
                this.sendMessage("resetScores")
            })
        },
        loadTasks() {
            axios
            .get('/data/tasks')
            .then(response => {
                if (!_.isEqual(response.data, this.tasks)) {
                    console.log("Change in tasks detected")
                    this.tasks = response.data
                    this.selectTask(this.selectedTask.id)
                }
            })
            .catch(e => {})
            .then(() => {
                setTimeout(() => this.loadTasks(), 1000)
            })
        },
        selectTask(taskId) {
            var newSelectedTask = this.tasks.filter(t => t.id == taskId)
            if (newSelectedTask.length === 0) {
                this.selectedTask = {
                    id: -1,
                    name: "-",
                    files: []
                }
            } else {
                this.selectedTask = JSON.parse(JSON.stringify(newSelectedTask[0]))
                this.selectedTaskFileDialogs = {}

                this.selectedTask.files.forEach(f => { if (f.file_type == "note") { this.$set(this.selectedTaskFileDialogs, f.name, false) }})
            }
        },
        loadContestants() {
            axios.get("/data/contestants")
            .then(response => {
                if (!_.isEqual(response.data, this.contestants)) {
                    console.log("Change in contestants detected")
                    this.contestants = response.data
                }
            })
            .catch(e => {})
            .then(() => {
                setTimeout(() => this.loadContestants(), 1000)
            })
        },
        loadGeneralFiles() {
            axios.get("/data/general_files")
            .then(response => {

                if (!_.isEqual(response.data, this.general_files)) {
                    console.log("Change in general files detected")
                    this.general_files = response.data
                    this.general_files.forEach(f => { if (f.file_type == "note") { this.$set(this.generalFileDialogs, f.name, false) }})
                }
            })
            .catch(e => {})
            .then(() => {
                setTimeout(() => this.loadGeneralFiles(), 1000)
            })
        },
        loadScores() {
            axios.get("/data/scores")
            .then(response => {

                if (!_.isEqual(response.data, this.scores)) {
                    console.log("Change in scores detected")
                    this.scores = response.data
                }
            })
            .catch(e => {})
            .then(() => {})
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
        },
        closeGeneralFileDialog(filename) {
            this.$set(this.generalFileDialogs, filename, false)
        },
        closeSelectedTaskFileDialog(filename) {
            this.$set(this.selectedTaskFileDialogs, filename, false)
        }
    },
    beforeMount() {
        this.loadTasks()
        this.loadContestants()
        this.loadGeneralFiles()
        this.loadScores()
        this.connectToWebsocket()
    },
    watch: {
        darkMode(val) {
            this.$vuetify.theme.dark = val
        },
        tasks() {            
            this.resetInternalScores()
        },
        contestants() {            
            this.resetInternalScores()
        },
        scores() {
            this.resetInternalScores()
        }
    },
    computed: {
        target () {
            const value = this['element']
            if (!isNaN(value)) return Number(value)
            else return value
        },
        filteredGeneralFiles() {
            return this.general_files.filter(file => file.name.toLowerCase() != "taskmaster")
        },
        sortedGeneralFiles() {
            var result = [...this.filteredGeneralFiles]
            return result.sort((a, b) => a.name.localeCompare(b.name))
        },
        sortedTasks() {
            var result = [...this.tasks]
            return result.sort((a, b) => a.name.localeCompare(b.name))
        },
        sortedContestants() {
            var result = [...this.contestants]
            return result.sort((a, b) => a.name.localeCompare(b.name))
        }
    }
})