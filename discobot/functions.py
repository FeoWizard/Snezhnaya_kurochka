import asyncio
import datetime
import gc
import itertools
import os
import random
import re
import traceback
import smtplib
import ssl
from ssl             import SSLContext
from email.mime.text import MIMEText
from email.header    import Header

import discord
from   discord import ChannelType
import discobot.bot_config
from discobot.bot_config import kurologger

allowed_list           = []  # Список объектов типа "Channel"
channel_semaphore_list = []  # Список Channel.id типа "int"
grappling_flag         = False
message_buffer         = []  # Список сообщений, НЕ занесённых в базу, будем пытаться записать их при удобном случае

# ========================================== АСИНХРОННЫЕ И НЕ ОЧЕНЬ ФУНКЦИИ ========================================= #


def init(BOT_NAME: str, DATE_STRING: str, SEND_MESSAGE_SIGN: bool, CHANNEL_GRAPPLE_SIGN: bool):

    LOG_FILENAME                          = BOT_NAME + "_" + DATE_STRING + ".txt"
    DATABASE_FILENAME                     = BOT_NAME + "_base.db"
    discobot.bot_config.DATABASE_PATH    += DATABASE_FILENAME
    discobot.bot_config.LOGS_PATH        += BOT_NAME + "/"

    if (not os.path.exists(discobot.bot_config.LOGS_PATH)):
        os.mkdir(discobot.bot_config.LOGS_PATH)

    discobot.bot_config.LOGS_PATH        += LOG_FILENAME
    discobot.bot_config.SEND_MESSAGE_SIGN = SEND_MESSAGE_SIGN
    discobot.functions.grappling_flag     = not CHANNEL_GRAPPLE_SIGN
    # Устанавливаем флаг в конфигурационном модуле, чтобы не отправлять сообщения
    # Ставлю, чтобы не писать перед каждым признаком (общаемся мы много здесь), чтобы не писать "discobot.bot_config."
    # Я "известил" все остальные модули, что не хочу отправлять сообщения,
    # т.к. во всех модулях лежат ссылки на SEND_MESS...
    return discobot.bot_config.LOGS_PATH, discobot.bot_config.DATABASE_PATH


def coin_toss():
    rand_int = random.randint(0, 1)

    if (rand_int):
        return "Orel!"
    else:
        return "Reshka!"


async def ava_search(message):
    if (len(message.mentions) > 0):
        user = message.mentions[0]
        if discobot.bot_config.SEND_MESSAGE_SIGN:
            avatar_url_string = str(user.avatar_url_as(format = None, static_format = 'png', size = 128))[:-9]
            await message.channel.send("Done!\nAvatar: " + avatar_url_string)

    else:

        try:
            user_to_find = message.content.split(" ", maxsplit = 1)[1]
        except Exception:
            if discobot.bot_config.SEND_MESSAGE_SIGN:
                await message.channel.send("invalid username <:itai:485529311353241640>")
        else:
            user = message.guild.get_member_named(user_to_find)

            if discobot.bot_config.SEND_MESSAGE_SIGN and user:
                avatar_url_string = str(user.avatar_url_as(format = None, static_format = 'png', size = 128))[:-9]
                await message.channel.send("Done!\nAvatar: " + avatar_url_string)
            else:
                if discobot.bot_config.SEND_MESSAGE_SIGN:
                    await message.channel.send("User not found <:itai:485529311353241640>")


async def find_last_online(message):
    # TODO: Доделать расчёт разницы в датах
    #  текущая - прошлая => <x> дней, <х> часов, <х> минут

    if (len(message.mentions) > 0):
        # Достаём пользователя из упоминаний
        user = message.mentions[0]

    else:
        # Если используется не упоминание пользователя, а просто ник
        try:
            user_to_find = message.content.split(" ", maxsplit = 1)[1]
        except BaseException:
            # Если входная строка неверна
            if discobot.bot_config.SEND_MESSAGE_SIGN:
                await message.channel.send("Invalid username <:itai:485529311353241640>")
            return
        else:
            user = message.guild.get_member_named(user_to_find)

            # Если пользователя не нашли на сервере - оповещаем и выходим
            if (user is None):
                if discobot.bot_config.SEND_MESSAGE_SIGN:
                    await message.channel.send("User not found <:itai:485529311353241640>")
                return

    if (user.status != discobot.bot_config.discord.Status.offline):
        if discobot.bot_config.SEND_MESSAGE_SIGN:
            await message.channel.send("User {} is now online! <:ningyo:513676059124957186>".format(get_username(user)))
        return

    # По сути, предыдущие if-ы используются, чтобы найти объект user
    # Ищем запись с пользователем в базе
    result = await get_user_from_connections_table(message, user)
    if (result is None):
        if discobot.bot_config.SEND_MESSAGE_SIGN:
            await message.channel.send("User not found <:itai:485529311353241640>")

    # Если пользователь найден - выводим имя/дату, когда он последний раз вышел из сети
    else:
        # TODO: Что, если пользователь определён/найден, но в поле last_seen таблицы Connected_Users стоит NULL???
        #  - сделать поиск по последнему сообщению
        #  - искать этого пользователя по всем серверам

        if (result[3] is None):
            if discobot.bot_config.SEND_MESSAGE_SIGN:
                await message.channel.send("It is unknown, when the user {} was last online".format(result[1]))
            return

        if discobot.bot_config.SEND_MESSAGE_SIGN:
            await message.channel.send("User {} was last online {}".format(result[1], result[3]))


async def get_user_from_connections_table(message, user):
    try:
        discobot.bot_config.cursor.execute("""
        SELECT UserID, Username, is_connected, last_seen
        FROM Connected_Users
        WHERE UserID = ?
        """, [user.id])
        return discobot.bot_config.cursor.fetchone()

    except BaseException as databaseErr:
        # В случае ошибки чтения из базы оповещаем + логгируем и выходим
        create_database_error_record(databaseErr)
        if discobot.bot_config.SEND_MESSAGE_SIGN:
            await message.channel.send(
                "Error occured! <:itai:485529311353241640>\nError reading service tables, "
                "please write to <@!125159119622635520>")
        return None


def get_time_string():
    return datetime.datetime.now().strftime("Date: %d/%m/%Y, Time: %H:%M:%S.%f")[:-3]


def get_basetime_string():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def get_username(user):
    return "@" + user.name + "#" + user.discriminator


def get_int_rand_number(arg: int):

    if (arg >= 0):
        return random.randint(0, arg)
    else:
        return None


async def send_rand_number(message: str, channel, user):

    arg = message.split(" ")  # Делаем из строки массив
    if (len(arg) > 1):
        arg = arg[1]  # Берём ВТОРОЙ элемент (это - сам аргумент команды)
    else:
        if discobot.bot_config.SEND_MESSAGE_SIGN:
            await channel.send("Invalid argument! <:itai:485529311353241640>")
        return

    try:
        arg = int(arg)  # Если юзер пожрал несвежего и отправил аргументом СТРОКУ вместо числа, то шлём его
    except ValueError:
        if discobot.bot_config.SEND_MESSAGE_SIGN:
            await channel.send("Invalid argument, it must be INT <:itai:485529311353241640>")
        return

    result = get_int_rand_number(arg)
    if (result is not None):
        if discobot.bot_config.SEND_MESSAGE_SIGN:
            await channel.send(user.mention + ", Your rand number: " + str(result))
    else:
        if discobot.bot_config.SEND_MESSAGE_SIGN:
            await channel.send("Invalid argument, it must be positive (>=0) <:itai:485529311353241640>")
        return


async def create_log_record(event: str, *args):
    log_string = str(event)
    if (len(args) != 0):
        log_string += " args: " + str(args)

    kurologger.info(msg = log_string)


def create_database_error_record(databaseErr: BaseException):
    kurologger.error(msg = f"Database error!\n", exc_info = databaseErr)


async def get_connections_table_state(entity: str):

    SQL_QUERY = """
    SELECT {}ID
    FROM Connected_{}""".format(entity.capitalize(), entity.capitalize() + "s")

    try:
        discobot.bot_config.cursor.execute(SQL_QUERY)

    except BaseException as databaseErr:
        create_database_error_record(databaseErr)

    else:
        result      = discobot.bot_config.cursor.fetchall()  # Возвращает list of tuples вида [(x,), (y,), (z,)]
        result_list = list(itertools.chain.from_iterable(result))
        return result_list  # разворачиваем лист из кортежей в просто лист и выдаём


async def update_connections_list(reason: str):

    IS_CONNECTED = 1
    last_seen    = None

    serversID  = await get_connections_table_state("server")
    channelsID = await get_connections_table_state("channel")
    usersID    = await get_connections_table_state("user")

    try:
        discobot.bot_config.cursor.executescript("""
        UPDATE Connected_Channels
        SET is_connected = 0;
        UPDATE Connected_Servers
        SET is_connected = 0;
        UPDATE Connected_Users
        SET is_connected = 0;
        """)
        discobot.bot_config.connection.commit()
    except BaseException as databaseErr:
        create_database_error_record(databaseErr)

    data_update_list = []
    data_insert_list = []

    try:

        for server in discobot.bot_config.client.guilds:

            if (server.id in serversID):
                data_tuple = (server.name, IS_CONNECTED, last_seen, server.id)
                data_update_list.append(data_tuple)
            else:
                data_tuple = (server.id, server.name, IS_CONNECTED, last_seen)
                data_insert_list.append(data_tuple)

        if (len(data_insert_list) > 0):
            discobot.bot_config.cursor.executemany("INSERT INTO Connected_Servers "
                                                   "VALUES (?, ?, ?, ?)", data_insert_list)
        if (len(data_update_list) > 0):
            discobot.bot_config.cursor.executemany("UPDATE Connected_Servers "
                                                   "SET ServerName     = ?,"
                                                   "    is_connected   = ?,"
                                                   "    last_seen      = ?"
                                                   "WHERE ServerID     = ?", data_update_list)
        discobot.bot_config.connection.commit()
    except BaseException as databaseErr:
        create_database_error_record(databaseErr)
        kurologger.error(msg = "Error in Connected_Servers transaction")

    del serversID
    data_update_list = []
    data_insert_list = []
    allowed_channels = []

    try:
        for channel in discobot.bot_config.client.get_all_channels():  # Берёт только каналы от серверов - без приватных

            permissions        = channel.permissions_for(member = channel.guild.me)
            is_read_allowed    = permissions.read_messages
            is_history_allowed = permissions.read_message_history

            if (channel.id in channelsID):
                data_tuple = (channel.guild.id, channel.name, str(channel.type), is_read_allowed,
                              is_history_allowed, IS_CONNECTED, last_seen, channel.id)
                data_update_list.append(data_tuple)
            else:
                data_tuple = (channel.guild.id, channel.id, channel.name, str(channel.type),
                              is_read_allowed, is_history_allowed, IS_CONNECTED, last_seen)
                data_insert_list.append(data_tuple)

            # Если у канала открыта история - берём его в список разрешённых для грапплера
            if (is_history_allowed):
                allowed_channels.append(channel)

        for channel in discobot.bot_config.client.private_channels:

            channel_name       = str(channel)[:14]  # 14 - Величина строки "Direct Message" #
            permissions        = channel.permissions_for(None)
            is_read_allowed    = permissions.read_messages
            is_history_allowed = permissions.read_message_history

            if (channel.id in channelsID):

                data_tuple = (None, channel_name, str(channel.type), is_read_allowed,
                              is_history_allowed, IS_CONNECTED, last_seen, channel.id)
                data_update_list.append(data_tuple)
            else:

                data_tuple = (None, channel.id, channel_name, str(channel.type),
                              is_read_allowed, is_history_allowed, IS_CONNECTED, last_seen)
                data_insert_list.append(data_tuple)

            # Если у канала открыта история - берём его в список разрешённых для грапплера
            if (is_history_allowed):
                allowed_channels.append(channel)

        if (len(data_insert_list) > 0):
            discobot.bot_config.cursor.executemany("INSERT INTO Connected_Channels "
                                                   "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data_insert_list)

        if (len(data_update_list) > 0):
            discobot.bot_config.cursor.executemany("UPDATE Connected_Channels "
                                                   "SET ServerID           = ?,"
                                                   "    ChannelName        = ?,"
                                                   "    ChannelType        = ?,"
                                                   "    is_read_allowed    = ?,"
                                                   "    is_history_allowed = ?,"
                                                   "    is_connected       = ?,"
                                                   "    last_seen          = ? "
                                                   "WHERE ChannelID        = ?", data_update_list)
        discobot.bot_config.connection.commit()

    except BaseException as databaseErr:
        create_database_error_record(databaseErr)
        kurologger.error(msg = "Error in Connected_Channels transaction")

    del channelsID
    data_update_list = []
    data_insert_list = []

    try:
        for user in discobot.bot_config.client.users:
            username = get_username(user)

            if(user.id in usersID):
                data_tuple = (username, IS_CONNECTED, user.id)
                data_update_list.append(data_tuple)
            else:
                data_tuple = (user.id, username, IS_CONNECTED, None)
                data_insert_list.append(data_tuple)

        if (len(data_insert_list) > 0):
            discobot.bot_config.cursor.executemany("INSERT INTO Connected_Users VALUES (?, ?, ?, ?)",
                                                   data_insert_list)

        if (len(data_update_list) > 0):
            discobot.bot_config.cursor.executemany("UPDATE Connected_Users "
                                                   "SET Username     = ?,"
                                                   "is_connected     = ? "
                                                   "WHERE UserID     = ?", data_update_list)
        discobot.bot_config.connection.commit()
    except BaseException as databaseErr:
        create_database_error_record(databaseErr)
        kurologger.error(msg = "Error in Connected_Users transaction")

    await create_log_record("Update connections complete, reason: " + reason)
    return allowed_channels


async def database_message_log_write(message_data_list):
    try:
        discobot.bot_config.cursor.execute("INSERT INTO Messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                           message_data_list)
        discobot.bot_config.connection.commit()
    except BaseException as databaseErr:
        discobot.functions.message_buffer.append(tuple(message_data_list))
        create_database_error_record(databaseErr)
        await create_log_record("The message was not recorded to the database, " +
                                str(len(discobot.functions.message_buffer)) + " messages in message buffer")


async def message_buffer_flush():
    if ( len(discobot.functions.message_buffer) > 0):
        try:
            discobot.bot_config.cursor.executemany("INSERT INTO Messages VALUES "
                                                   "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", message_buffer)
            discobot.bot_config.connection.commit()
            discobot.functions.message_buffer = []  # Очищаем буфер сообщений при удачной записи в базу
            await create_log_record("Messages were recorded to the database, buffer flushed")

        except BaseException as databaseErr:
            kurologger.error(msg = "Database error", exc_info = databaseErr)


def message_buffer_counter():
    return len(discobot.functions.message_buffer)


async def database_user_log_write(data_list):
    """data_list = [None, Date, UserID, Username_old, Username_new, ServerID, Server,
                          User_nickname_old, User_nickname_new, User_event]"""

    try:
        discobot.bot_config.cursor.execute("INSERT INTO User_Logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data_list)
        discobot.bot_config.connection.commit()
    except BaseException as databaseErr:
        create_database_error_record(databaseErr)


async def database_channel_log_write(data_list):
    """data_list = [None, Date, ServerID, Server, ChannelID,
                    Old_Channel_Name, New_Channel_Name, Channel_event]"""

    try:
        discobot.bot_config.cursor.execute("INSERT INTO Channel_Logs VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data_list)
        discobot.bot_config.connection.commit()
    except BaseException as databaseErr:
        create_database_error_record(databaseErr)


async def database_server_log_write(data_list):
    """data_list = [None, Date, ServerID, Old_server_name, New_server_name, Server_event]"""

    try:
        discobot.bot_config.cursor.execute("INSERT INTO Server_Logs VALUES (?, ?, ?, ?, ?, ?)", data_list)
        discobot.bot_config.connection.commit()
    except BaseException as databaseErr:
        create_database_error_record(databaseErr)


async def get_new_year_time(message):

    now = datetime.datetime.today()
    NY  = datetime.datetime(now.year + 1, 1, 1)
    d   = NY - now
    mm, ss = divmod(d.seconds, 60)
    hh, mm = divmod(mm, 60)

    NY_string = ":snowflake: Do Novogo Goda: "

    if (d.days % 10 == 1):

        if (d.days % 100 == 11):
            NY_string += "{} dney ".format(d.days)
        else:
            NY_string += "{} den' ".format(d.days)

    elif ((d.days % 10 > 1) and (d.days < 5)):
        NY_string += "{} dnya ".format(d.days)
    else:
        NY_string += "{} dney ".format(d.days)

    if (hh == 1 % 10):
        if (d.days % 100 == 11):
            NY_string += "{} chasov ".format(d.days)
        else:
            NY_string += "{} chas ".format(hh)

    elif ((hh > 1 % 10) and (hh % 10 < 5)):
        NY_string += "{} chasa ".format(hh)
    else:
        NY_string += "{} chasov ".format(hh)

    if (mm % 10 == 1):
        if (d.days % 100 == 11):
            NY_string += "{} minut ".format(d.days)
        else:
            NY_string += "{} minuta ".format(mm)

    elif ((mm % 10 > 1) and (mm % 10 < 5)):
        NY_string += "{} minuty ".format(mm)
    else:
        NY_string += "{} minut ".format(mm)

    if (ss % 10 == 1):
        if (d.days % 100 == 11):
            NY_string += "{} sekund ".format(d.days)
        else:
            NY_string += "{} sekunda :snowflake:".format(ss)

    elif ((ss % 10 > 1) and (ss % 10 < 5)):
        NY_string += "{} sekundy :snowflake:".format(ss)
    else:
        NY_string += "{} sekund :snowflake:".format(ss)

    if discobot.bot_config.SEND_MESSAGE_SIGN:
        await message.channel.send(NY_string)


# Общего назначения ================================================================================================= #

async def get_nitro_status(message):

    nitro_message = ""

    if (len(message.guild.premium_subscribers) == 0):
        if (message.guild.premium_subscription_count == 0):
            nitro_message += "Server nikto ne bustil :expressionless: "
        else:
            nitro_message += "Server bustili, no etih lyudey ne vidno! <:snuggle_right:699274633207218187>"

    else:
        count = 0
        for member in message.guild.premium_subscribers:
            count += 1
            user_string = str(count) + ") Polzovatel: " + get_username(member) + ";"

            if (member.nick is not None):
                user_string += " Nickname: " + member.nick + ";"

            nitro_message += user_string + " zabustil server: " + str(member.premium_since)[:-7] + "\n"

    nitro_message += "\n"
    nitro_message += "Total boosts: " + str(message.guild.premium_subscription_count) + "\n"
    nitro_message += "Server boost level: " + str(message.guild.premium_tier)
    if discobot.bot_config.SEND_MESSAGE_SIGN:
        await message.channel.send(nitro_message)


def check_base_record(sql_text: str, data_list: list):

    try:
        discobot.bot_config.cursor.execute(sql_text, data_list)
    except BaseException as databaseErr:
        create_database_error_record(databaseErr)
        return None

    if(len(discobot.bot_config.cursor.fetchall()) != 0):
        return False

    return True


# ======================================== Notifications processing ========================================= #
async def set_notification_channel(server_id: int, message_channel, role: str, message: str):

    channel_id: int = message_string_for_channel_id(message_channel.id, message)  # Берём из сообщения айди канала

    result = await find_notification_duplicate_string(server_id, channel_id, role)
    # Проверяем, что в базе нет такой записи (Чтобы не плодить дубликаты)

    if (result):
        # Если такая строка в базе есть - то ничего не делаем
        # (Можем сказать пользователю, что такой канал в такой роли уже установлен)
        if discobot.bot_config.SEND_MESSAGE_SIGN:
            await message_channel.send("Error! This channel is already set for this role!"
                                       " <:kanna_peer:498068170339385354>")

        return

    try:  # Если проверка прошла успешно
        discobot.bot_config.cursor.execute("""
        INSERT INTO Notification_Settings VALUES (?, ?, ?, ?, ?)
        """, [None, server_id, channel_id, role, None])
        discobot.bot_config.connection.commit()

        if discobot.bot_config.SEND_MESSAGE_SIGN:
            await message_channel.send("Done! <:suave:497478213002592279>")

    except BaseException as databaseErr:
        create_database_error_record(databaseErr)
        if discobot.bot_config.SEND_MESSAGE_SIGN:
            await message_channel.send("Error occured! <:itai:485529311353241640>")


def message_string_for_channel_id(message_channel_id: int, message_string: str):
    # Варианты приходящих строк:
    # !set_join_channel
    # !set_leave_channel <#415854407188611075>
    # !set_welcome_channel Это вроде как текст приветствия
    # !set_welcome_channel <#415854407188611075> Это вроде как текст приветствия

    result = message_string.split(" ", maxsplit = 2)
    if (len(result) == 1):
        return message_channel_id
    else:
        regexp_result = re.findall(r"<#\d+>", result[1])

        if (regexp_result):
            regexp_result = regexp_result[0].strip("<>#")  # Если шаблон ссылки на канал найден - возвращаем его
            return int(regexp_result)  # Превратив его в число, разумеется
        else:
            return message_channel_id


async def find_notification_duplicate_string(server_id: int, channel_id: int, role: str):

    try:
        discobot.bot_config.cursor.execute("""
        SELECT *
        FROM Notification_Settings
        WHERE 1=1
        AND ServerID  = ?
        AND ChannelID = ?
        AND Notification_Role = ?""", [server_id, channel_id, role])

        result = discobot.bot_config.cursor.fetchone()

        if (result is None):
            return False
        else:
            return result[0]

    except BaseException as databaseErr:
        create_database_error_record(databaseErr)
        return None


async def get_notification_channels(server_id: int, role: str):

    try:
        discobot.bot_config.cursor.execute("""
        SELECT Notification_Settings.ChannelID, 
               Notification_Settings.Notification_Role,
               Notification_Settings.Notification_Message
        FROM Notification_Settings
        WHERE 1=1
        AND ServerID  = ?
        AND Notification_Role = ?
        ORDER BY Notification_Settings.ID ASC""", [server_id, role])

        return discobot.bot_config.cursor.fetchall()  # Вернуть все каналы ЭТОГО сервера с ЭТОЙ ролью
        # Отдаётся список кортежей. (List of tuples) Если результата нет - возвратится пустой список.

    except BaseException as databaseErr:
        create_database_error_record(databaseErr)
        return False


# Это требуется для обработки on_member_join и on_member_remove
async def get_channels_for_server(server_id: int):

    try:
        discobot.bot_config.cursor.execute("""
        SELECT Notification_Settings.ChannelID, 
               Notification_Settings.Notification_Role 
        FROM Notification_Settings
        WHERE ServerID = ?
        ORDER BY Notification_Role
        """, [server_id])
    except BaseException as databaseErr:
        create_database_error_record(databaseErr)
        return False

    result = discobot.bot_config.cursor.fetchall()  # returns all the rows as a list of tuples

    if (result is None):
        return False
    else:
        return result


async def show_notification_channels(server_id: int, channel, role: str, mode: str):
    message_string = ""

    if (mode == "all"):
        result = await get_channels_for_server(server_id)

        if (result):
            # channel_id, notification_role
            for db_string in result:
                # channel = discobot.bot_config.client.get_channel(db_string[2])
                message_string = message_string + "<#" + str(db_string[0]) + "> Role: " + db_string[1] + "\n"
            await channel.send(message_string)

        else:
            if discobot.bot_config.SEND_MESSAGE_SIGN:
                await channel.send("Notification channels for this server is not set.")

    elif (mode == "one_role"):
        result = await get_notification_channels(server_id, role)

        if (result):
            # channel_id, notification_role, notification_message
            for db_string in result:
                message_string = message_string + "<#" + str(db_string[0]) + "> Role: " + db_string[1] + "\n"
            await channel.send(message_string)

        else:
            if discobot.bot_config.SEND_MESSAGE_SIGN:
                await channel.send("This type of channels is not set for this server.")


async def del_notification_channel(server_id: int, message_channel, role: str, message: str):

    channel_id: int = message_string_for_channel_id(message_channel.id, message)

    try:
        discobot.bot_config.cursor.execute("""
        DELETE FROM Notification_Settings 
        WHERE ServerID = ?
        AND ChannelID = ? 
        AND Notification_Role = ?
        """, [server_id, channel_id, role])
        discobot.bot_config.connection.commit()

    except BaseException as databaseErr:
        create_database_error_record(databaseErr)

        if discobot.bot_config.SEND_MESSAGE_SIGN:
            await message_channel.send("Error occured! <:itai:485529311353241640>")


# Это требуется для обработки on_member_join и on_member_remove
async def get_notification_channel_id(server_id):

    try:
        discobot.bot_config.cursor.execute("""
        SELECT Notification_Settings.ChannelID
        FROM Notification_Settings
        WHERE ServerID = ?
        """, [server_id])
    except BaseException as databaseErr:
        create_database_error_record(databaseErr)
        return None

    result = discobot.bot_config.cursor.fetchone()

    if (result is None):
        return False

    channel_id = result[0]

    return channel_id


# Это требуется для обработки on_member_join и on_member_remove
async def send_notification(member, event: str, event_string: str, server = None):

    if (server is None):
        server_id = member.guild.id
    else:
        server_id = server.id

    username = get_username(member)
    notification_string = "Polzovatel {} {}".format(username, event_string)

    # Обработка множества каналов для уведомлений #
    notification_channels = await get_notification_channels(server_id, event)

    if (notification_channels):
        # channel_id, notification_role, notification_message
        for db_string in notification_channels:
            channel = discobot.bot_config.client.get_channel(db_string[0])
            if discobot.bot_config.SEND_MESSAGE_SIGN:
                await channel.send(notification_string)
    else:
        return
    # Обработка множества каналов для уведомлений #


async def send_welcome_message(new_guild_member):
    # Обработка множества каналов для уведомлений #

    notification_channels = await get_notification_channels(new_guild_member.guild.id, "welcome")

    if (notification_channels):
        # channel_id, notification_role, notification_message
        for db_string in notification_channels:

            if (db_string[2] is None):
                continue

            channel = discobot.bot_config.client.get_channel(db_string[0])
            if discobot.bot_config.SEND_MESSAGE_SIGN:
                # Шаблон будет %username%, этот шаблон будем искать в строке
                # и заменять его на mention нового пользователя

                # <@!125159119622635520> -> <@!user_id>
                welcome_string = db_string[2].replace("%username%", new_guild_member.mention)

                await channel.send(welcome_string)
    else:
        return
    # Обработка множества каналов для уведомлений #


async def set_welcome_message(server_id: int, message_channel, message: str):
    # message - это текст приветственного сообщения

    # Получаем список welcome-каналов
    welcome_channels_list = await get_notification_channels(server_id, "welcome")

    if (welcome_channels_list):

        if (len(welcome_channels_list) == 1):
            # Если канал для приветствий один
            # Нужен UPDATE записи для канала в базе

            # Проверим корректность входных данных
            welcome_string = message.split(" ", maxsplit=1)
            if (len(welcome_string) == 1):
                if discobot.bot_config.SEND_MESSAGE_SIGN:
                    await message_channel.send("Invalid arguments! <:itai:485529311353241640>\n"
                                               "Must be: ```!set_welcome_message <welcome text>```")
                return
            else:
                welcome_string = welcome_string[1]

            # Извлекаем из ответа базы айдишник канала приветствий
            welcome_channel_id = welcome_channels_list[0][0]

            try:
                discobot.bot_config.cursor.execute("""
                    UPDATE Notification_Settings
                    SET Notification_Message = ?
                    WHERE 1=1
                    AND ServerID  = ?
                    AND ChannelID = ?
                    AND Notification_Role = 'welcome'""", [welcome_string, server_id, welcome_channel_id])

                discobot.bot_config.connection.commit()

            except BaseException as databaseErr:
                create_database_error_record(databaseErr)

            if discobot.bot_config.SEND_MESSAGE_SIGN:
                await message_channel.send("Done! <:suave:497478213002592279>")

        else:
            # Если каналов много (>1)
            # Проверим корректность входных данных
            # !set_welcome_message <номер канала> <текст приветствия>

            # Должно соблюдаться три условия:
            # 1) Строка разбивается на три части пробелами
            # 2) Вторая часть - число
            # 3) Вторая часть меньше или равна количеству строк из ответа базы -> welcome_channels_list
            # т.к. если она больше, то это неверный аргумент

            welcome_string = message.split(" ", maxsplit = 2)
            if (len(welcome_string) == 3) \
                    and (welcome_string[1].isdigit()) \
                    and (int(welcome_string[1]) <= len(welcome_channels_list)) \
                    and (int(welcome_string[1]) >= 0):

                # Второй аргумент - это нужный нам индекс
                index = int(welcome_string[1]) - 1
                # Вычитаем еденицу, т.к. пользователь ведёт счёт с еденицы, а мы - с НУЛЯ.

                welcome_channel_id = welcome_channels_list[index][0]
                welcome_string     = welcome_string[2]

                try:
                    discobot.bot_config.cursor.execute("""
                        UPDATE Notification_Settings
                        SET Notification_Message = ?
                        WHERE 1=1
                        AND ServerID  = ?
                        AND ChannelID = ?
                        AND Notification_Role = 'welcome'""", [welcome_string, server_id, welcome_channel_id])

                    discobot.bot_config.connection.commit()

                except BaseException as databaseErr:
                    create_database_error_record(databaseErr)

                if discobot.bot_config.SEND_MESSAGE_SIGN:
                    await message_channel.send("Done! <:suave:497478213002592279>")

            else:

                if discobot.bot_config.SEND_MESSAGE_SIGN:
                    await message_channel.send("Invalid arguments! <:itai:485529311353241640>\n"
                                               "Must be: ```!set_welcome_message "
                                               "<welcome channel number> <welcome text>```")

    else:
        if discobot.bot_config.SEND_MESSAGE_SIGN:
            await message_channel.send("\"Welcome\" channels are not set for this server.")

# ======================================== Notifications processing ========================================= #


# Грапплинг (граббинг, но первый вариант мне на слух нравится больше, поэтому вот так) каналов ====================== #
async def channel_grappler(channel, last_date: datetime = None):
    messages_list = []
    data_list     = []

    if (last_date is not None):
        shift      = -3    # Это нужно, чтобы выводилась строка даты, но без последних трёх символов
        last_date -= datetime.timedelta(hours = 3)  # Вычитаем разницу между UTC+0 и UTC+3
    else:
        shift      = None  # Неочевидное говнецо, да. Это для вывода,чтобы, если даты нет, то выводился "None", a ne "N"
        last_date  = None

    if (channel.type == ChannelType.private):
        channel_name = str(channel)[:14]
        guild        = None
    else:
        channel_name = channel.name
        guild        = channel.guild

    info_string = f"Server: {guild}; Channel: {channel_name}"
    kurologger.info(msg = f"{info_string} grappling begin! last date (UTC+0): " + str(last_date)[:shift])


    #  Сбор сообщений из канала # =================================================================================== #

    while (True):  # Бесконечный цикл для того, чтобы при неудаче грапплер повторял попытку захвата канала
        # Возможно, стоит сделать ограничение на количество попыток?
        try:
            kurologger.info(msg = "Try to grapple the channel!")
            if (last_date is not None):
                messages_list = await channel.history(limit = None, after = last_date, oldest_first = True).flatten()
            elif (last_date is None):
                messages_list = await channel.history(limit = None, oldest_first = True).flatten()

        except BaseException as error:
            kurologger.error(msg = f"Channel: {channel_name}; Server: {guild}; Error: {error}", exc_info = error)
            kurologger.info(msg  = "Retry to grapple the channel..")

        else:
            break  # Если ошибок не было, прерваем бесконечный цикл, и загружаем данные канала в базу

    #  Завершение сбора сообщений из канала # ======================================================================= #

    discobot.functions.channel_semaphore_list.append(channel.id)  # Добавляем Айдишник в список-семафор сразу
    # после завершения сбора сообщений с сервера (т.к. больше мы не соберём, а это значит, что с этого момента
    # можно логгировать этот канал со спокойной душой)

    if ( len(messages_list) == 0 ):
        await discobot.functions.create_log_record(info_string + "; no grappled messages")
        return

    await discobot.functions.create_log_record(info_string + "; grappled message count: " + str(len(messages_list)))
    await discobot.functions.create_log_record(info_string + " grappling complete, inserting in database")

    #  Подготовка списка данных для транзакции в базу # ============================================================= #

    if (channel.type == ChannelType.private):
        for mess in messages_list:
            time_string  = mess.created_at + datetime.timedelta(hours = 3)  # Прибавляем разницу между UTC+0 и UTC+3
            time_string  = datetime.datetime.strftime(time_string, "%Y-%m-%d %H:%M:%S.%f")[:-3]  # Приводим к формату

            username     = discobot.functions.get_username(mess.author)
            att_list     = mess.attachments
            mess_string  = mess.content
            user_id      = mess.author.id
            mess_id      = mess.id
            channel_id   = mess.channel.id
            is_deleted   = 0
            is_edited    = 0
            server_id    = None
            server_name  = ""
            channel_name = str(mess.channel)[:14]

            data_tuple = (None, time_string, server_name, server_id, channel_name, channel_id, username, user_id,
                          mess_string, mess_id, str(att_list), is_deleted, is_edited)
            data_list.append(data_tuple)
    else:
        for mess in messages_list:
            time_string  = mess.created_at + datetime.timedelta(hours = 3)  # Прибавляем разницу между UTC+0 и UTC+3
            time_string  = datetime.datetime.strftime(time_string, "%Y-%m-%d %H:%M:%S.%f")[:-3]  # Приводим к формату

            username     = discobot.functions.get_username(mess.author)  # Прибавляем разницу между UTC+0 и UTC+3
            att_list     = mess.attachments
            mess_string  = mess.content
            user_id      = mess.author.id
            mess_id      = mess.id
            channel_id   = mess.channel.id
            is_deleted   = 0
            is_edited    = 0
            server_id    = mess.guild.id
            server_name  = mess.guild.name
            channel_name = mess.channel.name

            data_tuple = (None, time_string, server_name, server_id, channel_name, channel_id, username, user_id,
                          mess_string, mess_id, str(att_list), is_deleted, is_edited)
            data_list.append(data_tuple)

    del messages_list  # всё слито в дата_лист с нужными полями, список сообщений больше не нужен

    #  Подготовка списка данных для транзакции в базу # ============================================================= #

    while (True):
        try:
            discobot.bot_config.cursor.executemany("INSERT INTO Messages VALUES"
                                                   " (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                                   data_list)
            discobot.bot_config.connection.commit()
        except BaseException as databaseErr:
            discobot.functions.create_database_error_record(databaseErr)
        else:
            break

    await discobot.functions.create_log_record(info_string + " inserting complete")
    del data_list
    kurologger.info(msg = f"objects deleted: {gc.collect()}")


# ============ Грапплер для всех каналов ============================================================================ #

async def all_channels_grapple():
    discobot.functions.grappling_flag         = True
    discobot.functions.channel_semaphore_list = []  # Опустошаем список-семафор, будем пополнять его в channel_grappler
    await discobot.functions.create_log_record("Channel grappling begin!")

    for channel in discobot.bot_config.client.get_all_channels():

        # if (discobot.functions.grappling_flag is False):
        #     await discobot.functions.create_log_record("Channel grappling interrupted!")
        #     return

        if ((channel.type == discobot.bot_config.discord.ChannelType.text)
                and (channel in discobot.functions.allowed_list)):

            try:
                discobot.bot_config.cursor.execute(
                    """
                    SELECT Date
                    FROM Messages
                    WHERE ChannelID = ?
                    ORDER BY Date DESC
                    LIMIT 1
                    """, [channel.id])

                result = discobot.bot_config.cursor.fetchone()  # Вытаскиваю дату последнего сообщения в канале

                if (result is None):

                    Database_Channel_Miss_Error_String = "\nExpecting last message date, received NONE; Channel: " \
                                                         + channel.name + "; Server: " + channel.guild.name

                    discobot.functions.create_database_error_record(BaseException(Database_Channel_Miss_Error_String))

                    last_date = None

                else:
                    last_date_string = result[0]
                    last_date = datetime.datetime.strptime(last_date_string, "%Y-%m-%d %H:%M:%S.%f")

                asyncio.create_task(channel_grappler(channel, last_date))

            except BaseException as databaseErr:
                discobot.functions.create_database_error_record(databaseErr)

    await discobot.functions.create_log_record("Channel grappling complete!")
    discobot.functions.grappling_flag = False

# ============ Статистика эмодзи для всех каналов =================================================================== #


async def emodzi_stat(guild):  # Рабочая функция, но работает несколько лет для каналов с множеством сообщений (>300000)

    if (guild is None):
        return

    emo_list = []
    for emo in guild.emojis:

        emo_string = "%<:" + emo.name + ":" + str(emo.id) + ">%"
        try:
            discobot.bot_config.cursor.execute(
                """
                SELECT *
                FROM Messages
                WHERE 1=1
                AND serverID = ?
                AND message LIKE ?
                """, [guild.id, emo_string])

            result = discobot.bot_config.cursor.fetchall()  # Вытаскиваю дату последнего сообщения в канале

        except BaseException as databaseErr:
            create_database_error_record(databaseErr)

        emo_list.append( (emo_string.strip("%"), len(result)) )

    emo_list.sort(key = lambda count: count[1])



async def uptime(start_time):
    end_time = datetime.datetime.now()
    delta_time = end_time - start_time
    return str(delta_time)[:-3]


def timer(func):
    def wrapper():
        start_time = datetime.datetime.now()
        func()
        end_time   = datetime.datetime.now()
        delta_time = end_time - start_time
        print("Function work time: " + str(delta_time)[:-3])
    return wrapper


async def send_mail(message_recipient: str, message_subject: str, message_text: str):
    HOST = "smtp." + discobot.bot_config.MAIL_DOMAIN

    msg = MIMEText(message_text, 'plain', 'utf-8')
    msg['Subject'] = Header(message_subject, 'utf-8')
    msg['From']    = discobot.bot_config.MAIL_LOGIN + "@" + discobot.bot_config.MAIL_DOMAIN
    msg['To']      = message_recipient

    context: SSLContext = ssl.create_default_context()

    server = smtplib.SMTP_SSL(HOST, port=465, context=context)
    server.login(user = discobot.bot_config.MAIL_LOGIN, password = discobot.bot_config.MAIL_PASSWORD)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()


async def save_user_roles(user: discord.Member):
    roles_ids = []
    for role in user.roles:
        if (role.name != "@everyone"):
            roles_ids.append(role.id)

    if (not roles_ids):
        return True

    roles_list = await get_user_roles(user.id)
    if (roles_list is None):
        sql_stmt = "INSERT INTO User_roles " \
                   "VALUES (?, ?, ?)"
        sql_args = [None, user.id, str(roles_ids).replace("[", "").replace("]", "")]
    else:
        sql_stmt = "UPDATE User_roles " \
                   "SET roles_ids = ? " \
                   "WHERE user_id = ?"
        sql_args = [str(roles_ids).replace("[", "").replace("]", ""), user.id]

    try:
        discobot.bot_config.cursor.execute(sql_stmt, sql_args)
        return True

    except BaseException as databaseErr:
        create_database_error_record(databaseErr)
        return False


async def get_user_roles(user_id):
    sql_stmt = "SELECT roles_ids " \
               "FROM User_roles " \
               "WHERE user_id = ?"
    sql_args = [user_id]

    try:
        discobot.bot_config.cursor.execute(sql_stmt, sql_args)
        result     = discobot.bot_config.cursor.fetchall()

        if (result):
            roles_list = [int(x) for x in result[0][0].split(", ")]
            return roles_list
        else:
            return None

    except BaseException as databaseErr:
        create_database_error_record(databaseErr)
        return None


async def set_user_roles(user: discord.Member, roles_ids, reason: str = "bot added"):

    if (not roles_ids):
        return False

    roles  = []
    server = user.guild
    for role_id in roles_ids:
        server_role = server.get_role(role_id)
        roles.append(server_role)

    await user.add_roles(*roles, reason = reason, atomic = True)


# ========================================== АСИНХРОННЫЕ И НЕ ОЧЕНЬ ФУНКЦИИ ========================================= #
