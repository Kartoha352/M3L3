from logic import DB_Manager
from config import *
from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telebot import types

manager = DB_Manager(DATABASE)
hideBoard = types.ReplyKeyboardRemove() 

# Функция для отмены выбора
cancel_button = "Отмена 🚫"
def cancel(message, bot):
    bot.send_message(message.chat.id, "Чтобы посмотреть команды, используй - /info", reply_markup=hideBoard)
  
# Функция для ответа в случае отсутствия проектов
def no_projects(bot, message):
    bot.send_message(message.chat.id, 'У тебя пока нет проектов!\nМожешь добавить их с помошью команды /new_project')

# Функция для генерации инлайн-клавиатуры
def gen_inline_markup(rows, data = None):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    if data == None:
        for row in rows:
            markup.add(InlineKeyboardButton(row, callback_data=row))
    else:
        for row, i in zip(rows, data):
            markup.add(InlineKeyboardButton(row, callback_data=i))
    return markup


# Функция для генерации обычной клавиатуры
def gen_markup(rows):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.row_width = 1
    for row in rows:
        markup.add(KeyboardButton(row))
    markup.add(KeyboardButton(cancel_button))
    return markup

# Словарь с атрибутами проектов и соответствующими текстами
attributes_of_projects = {'Название проекта' : ["Введите новое название проекта", "project_name"],
                          "Описание" : ["Введите новое описание проекта", "description"],
                          "Ссылка" : ["Введите новую ссылку на проект", "url"],
                          "Статус" : ["Выберите новый статус задачи", "status_id"]}

# Функция для отображения информации о проекте
def info_project(message, user_id, project_name, bot):
    info = manager.get_project_info(user_id, project_name)[0]
    skills = manager.get_project_skills(project_name)
    if not skills:
        skills = 'Навыки пока не добавлены'
    bot.send_message(message.chat.id, f"Название проекта: *{info[0]}*\nОписание: *{info[1]}*\nСсылка: *{info[2]}*\nТекущий статус: *{info[3]}*\nСкиллы: *{skills}*",reply_markup=gen_inline_markup(["Удалить"],["Удалить|"+str(message.message_id)]), parse_mode="Markdown")
    
# Функция для выбора проекта для обновления
def update_project_step_2(message, projects, bot):
    project_name = message.text
    if message.text == cancel_button:
        cancel(message, bot)
        return
    if project_name not in projects:
        bot.send_message(message.chat.id, "Что-то пошло не так!) Выбери проект, который хочешь изменить еще раз:", reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, update_project_step_2, projects=projects, bot=bot)
        return
    bot.send_message(message.chat.id, "Выбери, что требуется изменить в проекте", reply_markup=gen_markup(attributes_of_projects.keys()))
    bot.register_next_step_handler(message, update_project_step_3, project_name=project_name, bot=bot)

# Функция для выбора атрибута проекта для обновления
def update_project_step_3(message, project_name, bot):
    attribute = message.text
    reply_markup = None 
    if message.text == cancel_button:
        cancel(message, bot)
        return
    if attribute not in attributes_of_projects.keys():
        bot.send_message(message.chat.id, "Кажется, ты ошибся, попробуй еще раз!)", reply_markup=gen_markup(attributes_of_projects.keys()))
        bot.register_next_step_handler(message, update_project_step_3, project_name=project_name, bot=bot)
        return
    elif attribute == "Статус":
        rows = manager.get_statuses()
        reply_markup = gen_markup([x[0] for x in rows])
    bot.send_message(message.chat.id, attributes_of_projects[attribute][0], reply_markup=reply_markup)
    bot.register_next_step_handler(message, update_project_step_4, project_name=project_name, attribute=attributes_of_projects[attribute][1], bot=bot)

# Функция для обновления выбранного атрибута проекта
def update_project_step_4(message, project_name, attribute, bot): 
    update_info = message.text
    if attribute == "status_id":
        rows = manager.get_statuses()
        if update_info in [x[0] for x in rows]:
            update_info = manager.get_status_id(update_info)
        elif update_info == cancel_button:
            cancel(message, bot)
        else:
            bot.send_message(message.chat.id, "Был выбран неверный статус, попробуй еще раз!)", reply_markup=gen_markup([x[0] for x in rows]))
            bot.register_next_step_handler(message, update_project_step_4, project_name=project_name, attribute=attribute)
            return
    user_id = message.from_user.id
    data = [(update_info, project_name, user_id)]
    manager.update_projects(attribute, data)
    bot.send_message(message.chat.id, "Готово! Обновления внесены!)")

# Функция для удаления проекта
def delete_project(message, projects, bot):
    project = message.text
    user_id = message.from_user.id

    if message.text == cancel_button:
        cancel(message, bot)
        return
    if project not in projects:
        bot.send_message(message.chat.id, 'У тебя нет такого проекта, попробуй выбрать еще раз!', reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, delete_project, projects=projects, bot=bot)
        return
    project_id = manager.get_project_id(project, user_id)
    manager.delete_project(user_id, project_id)
    bot.send_message(message.chat.id, f'Проект *{project}* удален!', parse_mode="Markdown")

# Функция для выбора проекта, к которому нужно добавить навык
def skill_project(message, projects, bot):
    project_name = message.text
    if message.text == cancel_button:
        cancel(message, bot)
        return
        
    if project_name not in projects:
        bot.send_message(message.chat.id, 'У тебя нет такого проекта, попробуй еще раз!) Выбери проект для которого нужно выбрать навык', reply_markup=gen_markup(projects))
        bot.register_next_step_handler(message, skill_project, projects=projects, bot=bot)
    else:
        skills = [x[1] for x in manager.get_skills()]
        bot.send_message(message.chat.id, 'Выбери навык', reply_markup=gen_markup(skills))
        bot.register_next_step_handler(message, set_skill, project_name=project_name, skills=skills, bot=bot)

# Функция для добавления навыка к проекту
def set_skill(message, project_name, skills, bot):
    skill = message.text
    user_id = message.from_user.id
    if message.text == cancel_button:
        cancel(message, bot)
        return
        
    if skill not in skills:
        bot.send_message(message.chat.id, 'Видимо, ты выбрал навык не из списка, попробуй еще раз!) Выбери навык', reply_markup=gen_markup(skills))
        bot.register_next_step_handler(message, set_skill, project_name=project_name, skills=skills, bot=bot)
        return
    manager.insert_skill(user_id, project_name, skill)
    bot.send_message(message.chat.id, f'Навык {skill} добавлен проекту {project_name}')

# Функция для ввода имени проекта
def name_project(message, bot):
    name = message.text
    user_id = message.from_user.id
    data = [user_id, name]
    bot.send_message(message.chat.id, f"Название проекта: *{data[1]}*\nВведите ссылку на проект: ",parse_mode='Markdown')
    bot.register_next_step_handler(message, link_project, data=data, bot=bot)

# Функция для ввода ссылки на проект
def link_project(message, data, bot):
    data.append(message.text)
    statuses = [x[0] for x in manager.get_statuses()]
    bot.send_message(message.chat.id, f"Название проекта: *{data[1]}*\nCсылка на проект: *{data[2]}*\nВведите текущий статус проекта: ", reply_markup=gen_markup(statuses),parse_mode='Markdown')
    bot.register_next_step_handler(message, callback_project, data=data, statuses=statuses, bot=bot)

# Функция для завершения добавления проекта
def callback_project(message, data, statuses, bot):
    status = message.text
    if message.text == cancel_button:
        cancel(message, bot)
        return
    if status not in statuses:
        bot.send_message(message.chat.id, "Ты выбрал статус не из списка, попробуй еще раз!)", reply_markup=gen_markup(statuses))
        bot.register_next_step_handler(message, callback_project, data=data, statuses=statuses, bot=bot)
        return
    status_id = manager.get_status_id(status)
    data.append(status_id)
    manager.insert_project([tuple(data)])
    bot.send_message(message.chat.id, f"\nНазвание проекта: *{data[1]}*\nCсылка на проект: *{data[2]}*\nТекущий статус проекта: *{status}*\n\nПроект сохранен!",parse_mode='Markdown')