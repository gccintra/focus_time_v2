const userId = user.user_id
const username = user.username
let usersInFocus = {}; 
let focusTimer = null;


function formatTime(seconds) {
    const h = String(Math.floor(seconds / 3600)).padStart(2, "0");
    const m = String(Math.floor((seconds % 3600) / 60)).padStart(2, "0");
    const s = String(seconds % 60).padStart(2, "0");
    return `${h}:${m}:${s}`;
}

function updateUserInFocus() {
    const userList = document.getElementById("activeUsersList");

    while (userList.children.length > 2) {
        userList.removeChild(userList.lastChild);
    }
    
    const keys = Object.keys(usersInFocus);
    const lastKey = keys[keys.length - 1];

    Object.entries(usersInFocus).forEach(([key, value]) => {
        const startTime = new Date(value.start_time);
        const now = new Date();
        const elapsedSeconds = Math.floor((now - startTime) / 1000);
        const formattedTime = formatTime(elapsedSeconds);

        const userItem = document.createElement("li");
        userItem.innerHTML = `<span class="dropdown-item-text text-start" data-id="${key}"><strong>${value.username}</strong><br><small>${value.task_name} - ${formattedTime }</small></span>`;
        userList.appendChild(userItem);
        
        if (key !== lastKey) {
            const divider = document.createElement("li");
            divider.innerHTML = `<hr class="dropdown-divider">`;
            userList.appendChild(divider);
        }
    });
    }



const socket = io({ query: { user_id: userId, username: username } });

socket.on("connect", () => {
    console.log("Conectado ao servidor WebSocket");

    socket.emit("get_focus_users");
});


socket.on("update_focus_users", (data) => {
    usersInFocus = data.focused_users
    console.log("Usuários em foco agora:", usersInFocus);
});

socket.on("focus_user_joined", (data) => {
    console.log("Usuário entrou em foco agora: ", data);
    Object.entries(data).forEach(([key, value]) => {
        usersInFocus[key] = value;
    });
});

socket.on("focus_user_left", (data) => {
    console.log("Usuário saiu do foco agora: ", data);
    delete usersInFocus[data.user_id];
});


document.getElementById("communityDropdown").addEventListener("show.bs.dropdown", () => {
    updateUserInFocus(); 
    if (!focusTimer) {
        focusTimer = setInterval(updateUserInFocus, 1000);
    }
});

document.getElementById("communityDropdown").addEventListener("hide.bs.dropdown", () => {
    if (focusTimer) {
        clearInterval(focusTimer);
        focusTimer = null;
    }
});