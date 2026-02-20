// Инициализация Telegram WebApp
let tg = window.Telegram.WebApp;

// Расширяем приложение на весь экран
tg.expand();

// Получаем информацию о пользователе
const user = tg.initDataUnsafe?.user;

// Отображаем информацию о пользователе
function displayUserInfo() {
    const userInfoDiv = document.getElementById('userInfo');
    
    if (user) {
        userInfoDiv.innerHTML = `
            <h3>👤 Информация о пользователе</h3>
            <p><strong>ID:</strong> ${user.id}</p>
            <p><strong>Имя:</strong> ${user.first_name} ${user.last_name || ''}</p>
            <p><strong>Username:</strong> ${user.username ? '@' + user.username : 'не указан'}</p>
            <p><strong>Язык:</strong> ${user.language_code || 'ru'}</p>
        `;
    } else {
        userInfoDiv.innerHTML = '<p>Информация о пользователе недоступна</p>';
    }
}

// Сохранение настроек
function saveSettings() {
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const notifications = document.getElementById('notifications').checked;
    
    if (!name || !email) {
        tg.showAlert('Пожалуйста, заполните все поля!');
        return;
    }
    
    if (!validateEmail(email)) {
        tg.showAlert('Пожалуйста, введите корректный email!');
        return;
    }
    
    const settings = {
        action: 'save_settings',
        settings: {
            name: name,
            email: email,
            notifications: notifications
        }
    };
    
    // Отправляем данные в бота
    tg.sendData(JSON.stringify(settings));
    
    tg.showAlert('Настройки сохранены!');
}

// Отправка сообщения
function sendMessage() {
    const message = prompt('Введите сообщение для отправки в бота:');
    
    if (message) {
        const data = {
            action: 'send_message',
            message: message
        };
        
        tg.sendData(JSON.stringify(data));
        tg.showAlert('Сообщение отправлено!');
    }
}

// Закрытие приложения
function closeApp() {
    if (confirm('Закрыть приложение?')) {
        tg.close();
    }
}

// Валидация email
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Загрузка сохраненных настроек (если есть)
function loadSavedSettings() {
    // В реальном проекте здесь можно загрузить настройки из Telegram Cloud Storage
    // или из бота через специальный запрос
    
    // Пример заполнения полей из initData
    if (user) {
        document.getElementById('name').value = user.first_name || '';
    }
}

// Обработка основной кнопки Telegram
tg.MainButton.setText('Готово').onClick(() => {
    saveSettings();
});

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    displayUserInfo();
    loadSavedSettings();
    
    // Настраиваем тему
    document.body.style.backgroundColor = tg.themeParams.bg_color || '#f5f5f5';
    document.body.style.color = tg.themeParams.text_color || '#222222';
});

// Обработка ошибок
window.onerror = function(msg, url, line) {
    tg.showAlert(`Ошибка: ${msg}`);
    return false;
};