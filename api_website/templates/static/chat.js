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
    // const messageData = JSON.parse(event.data);
    console.log(event.data)
    const messagesContainer = document.getElementById('messages');

    // Создание нового элемента для сообщения
    const messageElement = document.createElement('div');
    messageElement.className = 'message'; // Можно использовать для стилизации

    // Установка текста сообщения
    messageElement.textContent = event.data;

    // Добавление нового сообщения в контейнер
    messagesContainer.appendChild(messageElement);

    // Прокрутка контейнера к последнему сообщению
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