from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
from database import CategoryRepository, ContactRepository

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token, db):
        self.token = token
        self.db = db
        self.category_repo = CategoryRepository(db)
        self.contact_repo = ContactRepository(db)
        self.application = Application.builder().token(token).build()

    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("menu", self.menu_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_text = """
        👋 Добро пожаловать в бот контактов!

        Используйте команду /menu для просмотра категорий контактов.
        """
        await update.message.reply_text(welcome_text)

    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /menu - показывает категории"""
        try:
            categories = self.category_repo.get_all_categories()

            if not categories:
                await update.message.reply_text("Категории не найдены")
                return

            # Создаем кнопки для каждой категории
            keyboard = []
            for category in categories:
                button = InlineKeyboardButton(
                    text=category['name'],
                    callback_data=f"category_{category['id']}"
                )
                keyboard.append([button])

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "📁 Выберите категорию:",
                reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error in menu command: {e}")
            await update.message.reply_text("❌ Ошибка при получении категорий")

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()

        callback_data = query.data

        if callback_data.startswith("category_"):
            try:
                category_id = int(callback_data.split("_")[1])
                await self.show_contacts(query, category_id)
            except (ValueError, IndexError) as e:
                logger.error(f"Invalid callback data: {callback_data}")
                await query.edit_message_text("❌ Ошибка: неверный формат данных")

    async def show_contacts(self, query, category_id):
        """Показать контакты выбранной категории"""
        try:
            contacts = self.contact_repo.get_contacts_by_category(category_id)

            if not contacts:
                await query.edit_message_text("📭 В этой категории нет контактов")
                return

            # Получаем информацию о категории
            category_info = self.category_repo.get_category_by_id(category_id)
            category_name = category_info[0]['name'] if category_info else "Неизвестная категория"

            # Формируем сообщение с контактами
            message = f"📋 Контакты категории: {category_name}\n\n"

            for contact in contacts:
                message += f"👤 {contact['name']}\n"
                message += f"📞 {contact['number']}\n"
                message += "─" * 20 + "\n"

            # Создаем кнопку для возврата к меню
            keyboard = [[InlineKeyboardButton("🔙 Назад к категориям", callback_data="back_to_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                message,
                reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error showing contacts: {e}")
            await query.edit_message_text("❌ Ошибка при получении контактов")

    def run(self):
        """Запуск бота"""
        self.setup_handlers()
        logger.info("Bot is running...")
        self.application.run_polling()