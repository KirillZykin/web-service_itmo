async function deleteChat(chatId) {
    const response = await fetch(`/delete-chat/${chatId}`, {
        method: "DELETE"
    });
    if (response.ok) {
        document.getElementById(`room_chat_${chatId}`).remove()
        alert("Чат успешно удалён")
    } else
        alert("Ошибка при удалении чата")
}

async function searchChats(event) {
    event.preventDefault();  // Останавливаем стандартное отправление формы
    const searchQuery = document.getElementById("searchQuery").value;
    const foundChatsList = document.getElementById("foundChats");

    if (searchQuery.length < 6) {
        alert("Введите более 5 символов для поиска.");
        foundChatsList.innerHTML = "";
        return;
    }

    try {
        const response = await fetch(`/search-chats?query=${encodeURIComponent(searchQuery)}`);
        const result = await response.json();
        foundChatsList.innerHTML = "";  // Очищаем предыдущие результаты поиска

        if (result.chats.length > 0) {
            result.chats.forEach(chat => {
                const chatItem = document.createElement("li");
                chatItem.onclick = () => enterChatAndGetToken(chat.name);
                chatItem.className = "chat-item";
                chatItem.textContent = chat.name;
                foundChatsList.appendChild(chatItem);
            });
        } else {
            const chatItem = document.createElement("li");
            chatItem.className = "chat-item";
            chatItem.textContent = "Ничего не найдено";
            foundChatsList.appendChild(chatItem);
        }
    } catch (error) {
        alert("Ошибка при выполнении поиска:" + error)
    }
}

// функция перехода в чат
async function enterChatAndGetToken(chatName) {
    try {
        const response = await fetch('/get_token_chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ "chat_name": chatName }),
        });

        const data = await response.json();
        if (response.ok) {
            const token = data.access_token;
            localStorage.setItem("token", token);
            window.location.href = "/chat/";
        } else {
            console.error('Error getting token:', data.detail);
        }
    } catch (error) {
        console.error('Request failed', error);
    }
}

function logout() {
    // Удаляем токен из localStorage
    localStorage.removeItem("token");
    window.location.href = "/logout";
}