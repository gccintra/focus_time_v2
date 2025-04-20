let timerInterval;
let saveInterval;
let elapsedTime = parseInt(task_data.today_total_seconds) || 0;
let isRunning = false;
let startTime
const userId = user_data.user_id; 
const username = user_data.username;
const taskName = task_data.task_name

const socket = io({ query: { user_id: userId, username: username } });

socket.on("connect", () => {
    console.log("Conectado ao servidor WebSocket");
});



document.addEventListener("DOMContentLoaded", function() {

    const startButton = document.querySelector("#timerButton");
    const timerDisplay = document.getElementById("timerDisplay");
    const taskId = task_data.task_id; 

    startButton.addEventListener("click", function() {
        if (isRunning) {
            stopTimer()
        } else {
            startTimer()
        }
    });

    function startTimer(){
        startTime = Date.now() - elapsedTime * 1000;
        isRunning = true;
        startButton.textContent = "Stop";

        // user_id: userId, username: username 
        socket.emit("enter_focus", { username: username, user_id: userId, task_name: taskName, start_time: Date.now() });


        timerInterval = setInterval(() => {
            elapsedTime = Math.floor((Date.now() - startTime) / 1000);
            updateTimerDisplay(timerDisplay, elapsedTime);
        }, 1000);

        saveInterval = setInterval(() => {
            saveElapsedTime();
        }, 600000)   // 10 minutes

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
        fetch(`/task/update_task_time/${taskId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ elapsed_seconds: elapsedTime })
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
            
            // envia um request assíncrono e não bloqueante para um servidor web. O request não espera por uma resposta.
            const url = `/task/update_task_time/${taskId}`;
            const data = JSON.stringify({ elapsed_seconds: elapsedTime });
            const blob = new Blob([data], { type: "application/json" });
    
            navigator.sendBeacon(url, blob);
        }
    });
});


