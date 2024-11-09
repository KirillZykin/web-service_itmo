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