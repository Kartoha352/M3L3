from logic import DB_Manager
from config import *
from functions import *
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telebot import types

bot = TeleBot(TOKEN)
hideBoard = types.ReplyKeyboardRemove() 


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, """Привет! Я бот-менеджер проектов
Помогу тебе сохранить твои проекты и информацию о них!) 
""")
    info(message)
    
@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id,
"""
Вот команды которые могут тебе помочь:

/new_project - используй для добавления нового проекта
/projects - используй для отображения всех проектов
/update_projects - используй для изменения данных о проекте
/skills - используй для привязки навыков к проекту
/delete - используй для удаления проекта

Также ты можешь ввести название проекта и узнать информацию о нем!""")
    

@bot.message_handler(commands=['new_project'])
def addtask_command(message):
    bot.send_message(message.chat.id, "Введите название проекта:")
    bot.register_next_step_handler(message, name_project, bot=bot)


@bot.message_handler(commands=['skills'])
def skill_handler(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, 'Выбери проект для которого нужно выбрать навык', reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, skill_project, projects=projects, bot=bot)
    else:
        no_projects(message, bot)


@bot.message_handler(commands=['projects'])
def get_projects(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        text = "\n".join([f"Название проекта: *{x[2]}*\nСсылка: *{x[4]}*\n" for x in projects])
        bot.send_message(message.chat.id, text, reply_markup=gen_inline_markup([x[2] for x in projects]), parse_mode="Markdown")
    else:
        no_projects(bot, message)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if "Удалить|" not in call.data:
        project_name = call.data
        info_project(call.message, call.from_user.id, project_name, bot)
    else:
        user_id = call.from_user.id
        project_name = call.message.text.split("\n")[0].split(": ")[1]
        project_id = manager.get_project_id(project_name, user_id)
        manager.delete_project(user_id, project_id)
        
        bot.send_message(call.message.chat.id, f"Проект *{project_name}* удалён!", parse_mode="Markdown")
        bot.delete_message(call.message.chat.id, call.message.message_id)

        projects = manager.get_projects(user_id)
        if projects:
            text = "\n".join([f"Название проекта: *{x[2]}*\nСсылка: *{x[4]}*\n" for x in projects])
        else:
            text = 'У тебя пока нет проектов!\nМожешь добавить их с помошью команды /new_project'
        bot.edit_message_text(text,call.message.chat.id, message_id=int(call.data.split("|")[1]), reply_markup=gen_inline_markup([x[2] for x in projects]), parse_mode="Markdown")


@bot.message_handler(commands=['delete'])
def delete_handler(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        text = "\n".join([f"Название проекта: *{x[2]}*\nСсылка: *{x[4]}*\n" for x in projects])
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, text, reply_markup=gen_markup(projects), parse_mode="Markdown")
        bot.register_next_step_handler(message, delete_project, projects=projects, bot=bot)
    else:
        no_projects(bot, message)

@bot.message_handler(commands=['update_projects'])
def update_project(message):
    user_id = message.from_user.id
    projects = manager.get_projects(user_id)
    if projects:
        projects = [x[2] for x in projects]
        bot.send_message(message.chat.id, "Выбери проект, который хочешь изменить", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, update_project_step_2, projects=projects, bot=bot)
    else:
        no_projects(bot, message)


@bot.message_handler(func=lambda message: True)
def text_handler(message):
    user_id = message.from_user.id
    projects =[ x[2] for x in manager.get_projects(user_id)]
    project = message.text
    if project in projects:
        info_project(message, user_id, project)
        return
    bot.reply_to(message, "Тебе нужна помощь?")
    info(message)

    
if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    bot.infinity_polling()
