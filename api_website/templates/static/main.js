async function deleteChat(chatId) {
    const response = await fetch(`/delete-chat/${chatId}`, {
        method: "DELETE"
    });
    // TODO сделать доп алёрты
    if (response.ok) {
        document.getElementById(`room_chat_${chatId}`).remove()
        alert("Чат успешно удалён")
    } else
        alert("Ошибка при удалении чата")
}

async function searchChats(event) {
    event.preventDefault();  // Останавливаем стандартное отправление формы
    // TODO проверка на количество символов (>6)
    const searchQuery = document.getElementById("searchQuery").value;

    try {
        const response = await fetch(`/search-chats?query=${encodeURIComponent(searchQuery)}`);
        const result = await response.json();

        const foundChatsList = document.getElementById("foundChats");
        foundChatsList.innerHTML = "";  // Очищаем предыдущие результаты поиска

        if (result.chats) {
            result.chats.forEach(chat => {
                const chatItem = document.createElement("li");
                chatItem.onclick = () => enterChatAndGetToken(chat.name);
                chatItem.textContent = chat.name;
                foundChatsList.appendChild(chatItem);
            });
        } else {
            foundChatsList.innerHTML = "<li>Ничего не найдено</li>";
        //     TODO чтобы появлялась
        }
    } catch (error) {
        console.error("Ошибка при выполнении поиска:", error);
    //     TODO алерт
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