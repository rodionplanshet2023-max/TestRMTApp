# type: ignore
import logging
import json
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ContextTypes, 
    filters
)

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
# URL вашего веб-приложения (замените на свой после деплоя)
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://your-domain.com')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    try:
        # Проверяем, что сообщение существует
        if not update.message:
            logger.warning("Получен start без сообщения")
            return
            
        user = update.effective_user
        user_name = user.first_name if user else "пользователь"
        
        # Создаем клавиатуру с кнопкой для открытия WebApp
        keyboard = [
            [InlineKeyboardButton(
                "Открыть мини-приложение 🚀",
                web_app=WebAppInfo(url=f"{WEBAPP_URL}/webapp/index.html")
            )],
            [InlineKeyboardButton("ℹ️ О боте", callback_data="info")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"👋 Привет, {user_name}!\n\n"
            f"Я бот с мини-приложением. Нажми кнопку ниже, чтобы открыть приложение:",
            reply_markup=reply_markup
        )
        logger.info(f"Команда /start от пользователя {user_name}")
    except Exception as e:
        logger.error(f"Ошибка в start: {e}")

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка данных из WebApp"""
    try:
        # Проверяем наличие данных
        if not update.effective_message:
            logger.warning("Получены web_app_data без сообщения")
            return
            
        if not update.effective_message.web_app_data:
            logger.warning("Получено сообщение без web_app_data")
            return
        
        # Получаем данные из WebApp
        web_app_data = update.effective_message.web_app_data
        data_str = web_app_data.data
        
        # Парсим JSON
        data: Dict[str, Any] = json.loads(data_str)
        logger.info(f"Получены данные из WebApp: {data}")
        
        # Получаем действие из данных
        action = data.get('action')
        
        if action == 'save_settings':
            settings = data.get('settings', {})
            user_id = update.effective_user.id if update.effective_user else None
            
            if user_id:
                # Сохраняем настройки пользователя
                if not context.user_data:
                    context.user_data = {}
                context.user_data['settings'] = settings
                logger.info(f"Сохранены настройки для пользователя {user_id}")
            
            # Формируем ответ
            name = settings.get('name', 'Не указано')
            email = settings.get('email', 'Не указано')
            notifications = settings.get('notifications', False)
            notifications_status = '✅' if notifications else '❌'
            
            await update.effective_message.reply_text(
                f"✅ Настройки сохранены!\n"
                f"Имя: {name}\n"
                f"Email: {email}\n"
                f"Уведомления: {notifications_status}"
            )
        
        elif action == 'send_message':
            message_text = data.get('message', '')
            await update.effective_message.reply_text(
                f"📝 Сообщение из мини-приложения:\n{message_text}"
            )
        else:
            await update.effective_message.reply_text(
                f"✅ Данные получены: {data}"
            )
            
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON: {e}")
        if update.effective_message:
            await update.effective_message.reply_text("❌ Ошибка при обработке данных")
    except Exception as e:
        logger.error(f"Ошибка в web_app_data: {e}")
        if update.effective_message:
            await update.effective_message.reply_text("❌ Произошла ошибка")

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать текущие настройки пользователя"""
    try:
        # Проверяем наличие сообщения
        if not update.message:
            logger.warning("Команда settings без сообщения")
            return
        
        # Безопасно получаем настройки из user_data
        user_data = context.user_data
        settings = {}
        
        if user_data and 'settings' in user_data:
            settings = user_data['settings']
        
        if not settings:
            await update.message.reply_text(
                "У вас пока нет сохраненных настроек. "
                "Откройте мини-приложение, чтобы настроить профиль."
            )
            return
        
        # Безопасно получаем значения с проверкой на None
        name = settings.get('name', 'Не указано')
        email = settings.get('email', 'Не указано')
        notifications = settings.get('notifications', False)
        notifications_status = 'Вкл' if notifications else 'Выкл'
        
        settings_text = "📋 Ваши настройки:\n\n"
        settings_text += f"👤 Имя: {name}\n"
        settings_text += f"📧 Email: {email}\n"
        settings_text += f"🔔 Уведомления: {notifications_status}"
        
        await update.message.reply_text(settings_text)
        logger.info(f"Показаны настройки для пользователя")
        
    except Exception as e:
        logger.error(f"Ошибка в settings_command: {e}")
        if update.message:
            await update.message.reply_text("❌ Произошла ошибка при получении настроек")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на инлайн кнопки"""
    try:
        if not update.callback_query:
            logger.warning("Получен callback без query")
            return
            
        query = update.callback_query
        await query.answer()
        
        if query.data == "info":
            info_text = (
                "ℹ️ О боте:\n\n"
                "Этот бот демонстрирует работу Telegram Mini Apps.\n"
                "Возможности:\n"
                "• Открытие мини-приложения\n"
                "• Обмен данными между ботом и приложением\n"
                "• Сохранение настроек пользователя\n\n"
                "Используйте команду /start, чтобы открыть приложение."
            )
            
            # Пытаемся отредактировать сообщение
            try:
                await query.edit_message_text(info_text)
            except Exception as e:
                logger.error(f"Ошибка при edit_message_text: {e}")
                # Если не получается отредактировать, отправляем новое сообщение
                if query.message:
                    await query.message.reply_text(info_text)
                    
    except Exception as e:
        logger.error(f"Ошибка в button_callback: {e}")

def main():
    """Запуск бота"""
    # Проверяем наличие токена
    if not BOT_TOKEN:
        logger.error("❌ Не указан BOT_TOKEN в .env файле")
        logger.info("Создайте файл .env с содержимым: BOT_TOKEN=ваш_токен_бота")
        return
    
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("settings", settings_command))
        
        # Обработчик данных из WebApp
        application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
        
        # Обработчик инлайн кнопок
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Запускаем бота
        logger.info("🚀 Бот успешно запущен...")
        logger.info(f"📱 WebApp URL: {WEBAPP_URL}/webapp/index.html")
        
        # Запускаем polling
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при запуске бота: {e}")

if __name__ == '__main__':
    main()