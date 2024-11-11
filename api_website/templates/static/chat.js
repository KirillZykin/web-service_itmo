const ws = new WebSocket(`ws://127.0.0.1/ws/chat/`);
const token = localStorage.getItem("token");

// Обрабатываем подключение
ws.onopen = () => {
    const authMessage = {
        type: "join",
        token: token
    };
    ws.send(JSON.stringify(authMessage));
};

// Обрабатываем получение сообщений
ws.onmessage = function (event) {
    const messagesContainer = document.getElementById('messages');
    const messageElement = document.createElement('div');
    messageElement.className = 'message';
    messageElement.textContent = event.data;
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
};

// Обработка отправки сообщения
function sendMessage() {
    const input = document.getElementById("messageInput");
    const message = input.value.trim();
    if (message) {
        ws.send(JSON.stringify({ type: "message", content: message }));
        input.value = "";
    }
}

document.getElementById("messageInput").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});