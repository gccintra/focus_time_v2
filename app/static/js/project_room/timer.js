let timerInterval;
let saveInterval;
let elapsedTimeDisplay = parseInt(project_data.today_total_seconds) || 0;
let isRunning = false;
let startTime
let realStartTimeISO
let elapsedTimeSession
const userId = user_data.user_id; 
const username = user_data.username;
const projectName = project_data.project_name
const projectID = project_data.project_id
const socket = io({ query: { user_id: userId, username: username } });

socket.on("connect", () => {
    console.log("Conectado ao servidor WebSocket");
});



document.addEventListener("DOMContentLoaded", function() {

    const startButton = document.querySelector("#timerButton");
    const timerDisplay = document.getElementById("timerDisplay");

    startButton.addEventListener("click", function() {
        if (isRunning) {
            stopTimer()
        } else {
            startTimer()
        }
    });

    function startTimer(){
        let realStartTime = new Date(Date.now())
        realStartTimeISO = getISOString(realStartTime);
        
        elapsedTimeSession = 0;

        //console.log(realStartTime)
        startTime = Date.now() - elapsedTimeDisplay * 1000;
        isRunning = true;
        startButton.textContent = "Stop";

        // mudar taskname no websocket.
        socket.emit("enter_focus", { username: username, user_id: userId, task_name: projectName, start_time: Date.now() });


        timerInterval = setInterval(() => {
            elapsedTimeDisplay = Math.floor((Date.now() - startTime) / 1000)
            elapsedTimeSession = Math.floor((Date.now() - realStartTime.getTime()) / 1000)
            updateTimerDisplay(timerDisplay, elapsedTimeDisplay);
        }, 1000);

        // saveInterval = setInterval(() => {
        //     saveElapsedTime();
        // }, 600000)   // 10 minutes

    }

    function stopTimer(){
        clearInterval(timerInterval);
        clearInterval(saveInterval);
        isRunning = false;
        startButton.textContent = "Start";

        socket.emit("leave_focus", { user_id: userId });

        saveElapsedTime()
    }

    function saveElapsedTime(){
        if (elapsedTimeSession == 0) {
            return;
        }

        fetch(`/focus_session/save`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({started_at: realStartTimeISO, duration_seconds: elapsedTimeSession, project_id: projectID })
        })
        .then(response => response.json())
        .then(({ success, message, data, error }) => {
            if (success){
                console.log(message)
            } else {
                showToast('error', message || 'Erro ao salvar o tempo em foco');
                console.log(error)
            }
        })
        .catch((error) => {
            showToast('error', 'Something went wrong while saving time in focus.');
            console.error("Erro ao salvar ElapsedTime: ", error);
         }); 
    }

    function updateTimerDisplay(timerDisplay, seconds) {
        const hours = String(Math.floor(seconds / 3600)).padStart(2, '0');
        const minutes = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0');
        const secs = String(seconds % 60).padStart(2, '0');
        timerDisplay.textContent = `${hours}:${minutes}:${secs}`;
    }

    window.addEventListener("beforeunload", function () {
        if (isRunning) {
            socket.emit("leave_focus", { user_id: userId });

            clearInterval(timerInterval);
            clearInterval(saveInterval);
            isRunning = false;
            startButton.textContent = "Start";
            
            // request assíncrono e não bloqueante. O request não espera por uma resposta.
            const url = `/focus_session/save`;
            const data = JSON.stringify({started_at: realStartTimeISO, duration_seconds: elapsedTimeSession, project_id: projectID });
            const blob = new Blob([data], { type: "application/json" });
    
            navigator.sendBeacon(url, blob);
        }
    });
});

function getISOString(date) {

    const pad = (num) => String(num).padStart(2, '0');
  
    const year = date.getFullYear();
    const month = pad(date.getMonth() + 1); 
    const day = pad(date.getDate());
    const hours = pad(date.getHours());
    const minutes = pad(date.getMinutes());
    const seconds = pad(date.getSeconds());
    const milliseconds = String(date.getMilliseconds()).padStart(3, '0');
  
  
    return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}.${milliseconds}`;
  
  }
