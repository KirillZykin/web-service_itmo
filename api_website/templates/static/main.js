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