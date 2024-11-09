// Подключаем WebSocket к микросервису chat
const ws = new WebSocket("ws://localhost:8000/chat"); // замените на ваш адрес сервера

const messagesContainer = document.getElementById("messages");

// Обрабатываем подключение
ws.onopen = () => {
    console.log("Connected to chat server");
};

// Обрабатываем получение сообщений
ws.onmessage = (event) => {
    const messageData = JSON.parse(event.data);
    const messageElement = document.createElement("div");

    if (messageData.type === "join") {
        // Уведомление о подключении пользователя
        messageElement.classList.add("user-join");
        messageElement.textContent = `${messageData.user} присоединился к чату.`;
    } else if (messageData.type === "message") {
        // Сообщение от пользователя
        messageElement.classList.add("message");
        messageElement.textContent = `${messageData.user}: ${messageData.content}`;
    }

    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight; // Скроллим вниз
};

// Обработка отправки сообщения
function sendMessage() {
    const input = document.getElementById("messageInput");
    const message = input.value.trim();
    if (message) {
        ws.send(JSON.stringify({ type: "message", content: message }));
        input.value = ""; // Очищаем поле ввода
    }
}