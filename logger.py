import discobot.bot_config
import discobot.functions
import discobot.logging_events
import discobot.common_events
import discord
import sqlite3

from datetime import timedelta, datetime

from discobot.bot_config import DISCORD_BOT_TOKEN


BOT_NAME             = "logger"
DATE_STRING          = discobot.functions.get_basetime_string()[:-4].replace(" ", "_").replace(":", "-")
SEND_MESSAGE_SIGN    = False
CHANNEL_GRAPPLE_SIGN = True
# Одной строкой я привожу запись вида: ("%Y-%m-%d %H:%M:%S.%f")[:-3]
# к записи вида:  "%Y-%m-%d_%H-%M-%S"

LOGS_PATH, DATABASE_PATH = discobot.functions.init(BOT_NAME, DATE_STRING, SEND_MESSAGE_SIGN, CHANNEL_GRAPPLE_SIGN)

# =============================================== СОБЫТИЯ MESSAGE LOOP =============================================== #


@discobot.bot_config.client.event
async def on_message(message):
    is_this_private_message = False

    time_string = message.created_at + timedelta(hours=3)  # Прибавляем разницу между UTC+0 и UTC+3
    time_string = datetime.strftime(time_string, "%Y-%m-%d %H:%M:%S.%f")[:-3]  # Приводим к формату

    username       = discobot.functions.get_username(message.author)
    att_list       = message.attachments
    message_string = message.content
    user_id        = message.author.id
    message_id     = message.id
    channel_id     = message.channel.id
    is_deleted     = 0
    is_edited      = 0  # имеет смысл NULL

    if (message.author.id == 125159119622635520):
        is_this_Snezhinka = True
    else:
        is_this_Snezhinka = False

    if (message.channel.type == discord.ChannelType.private):
        is_this_private_message = True
    else:
        is_this_private_message = False

    if (is_this_private_message):

        server_id    = None  # имеет смысл NULL
        server_name  = ""
        channel_name = str(message.channel)[:14]  # 14 - Величина строки "Direct Message" #

    else:

        server_id    = message.guild.id
        server_name  = message.guild.name
        channel_name = message.channel.name


    if (message.channel.id in discobot.functions.channel_semaphore_list):
        data_list = [None, time_string, server_name, server_id, channel_name, channel_id, username, user_id,
                     message_string, message_id, str(att_list), is_deleted, is_edited]
        await discobot.functions.database_message_log_write(data_list)

# ==================================================== Общаемся ===================================================== #

# ========================================= Сервисные команды ========================================= #

# Здесь !second_exit, чтобы не цеплялся основной бот
    if ( message.content.startswith("!logexit") and (message.author.id == 125159119622635520) ):

        print(discobot.functions.get_time_string() + " //:> " + BOT_NAME + " shutdown initialized")
        discobot.bot_config.client.loop.stop()

    elif ( message.content.startswith("!shutdown") and (is_this_Snezhinka)):
        print(discobot.functions.get_time_string() + " //:> " + BOT_NAME + " shutdown initialized")
        discobot.bot_config.client.loop.stop()

    elif (message.content.startswith("!emo") and (is_this_Snezhinka)):
        await discobot.functions.emodzi_stat(message.guild)

    elif ( message.content.startswith("!update") and (message.author.id == 125159119622635520) ):
        discobot.functions.allowed_list = await discobot.functions.update_connections_list("User command!")

    elif ( message.content.startswith('!grapple') and (message.author.id == 125159119622635520) ):
        if (discobot.functions.grappling_flag is False):  # Запускать "новый" грапплер, если "старый" уже неактивен
            await discobot.functions.all_channels_grapple()
        else:
            print(discobot.functions.get_time_string() + " //:> Grappler is already active!")

    elif (message.content.startswith("!buffer") and (message.author.id == 125159119622635520)):
        if SEND_MESSAGE_SIGN:
            print(discobot.functions.get_time_string() + " //:> message buffer count:",
                  (discobot.functions.message_buffer_counter()))

    elif (message.content.startswith("!flush") and (message.author.id == 125159119622635520)):
        await discobot.functions.message_buffer_flush()

    elif (message_string.startswith("!name") and is_this_Snezhinka):
        print(discobot.functions.get_time_string() + " //:> bot name:", BOT_NAME)

# ========================================= Сервисные команды ========================================= #


# =============================================== СОБЫТИЯ MESSAGE LOOP =============================================== #

# Эта секция - и есть функция main, если скрипт запущен непосредственно (Не вызваны из других файлов)
if __name__ == "__main__":

    file_mode = "w"
    try:
        log_file                     = open(LOGS_PATH, file_mode, encoding = "utf-8")
        discobot.bot_config.log_file = log_file  # Для добавления в модуль экземпляра лог-файла для текущего бота
    except BaseException as Error:
        print("Critical log file error:", Error)
        print("Application will be closed")
        input()
        exit(-1)
    print(discobot.functions.get_time_string() + " //:> " + BOT_NAME + "'s log file is open!\n")

    try:
        log_file.write("------------------- " + BOT_NAME + " session start -------------------\n")
        log_file.write(discobot.functions.get_time_string() + " //:> Session started;\n")
        log_file.flush()
    except BaseException as Error:
        print("log file error: ", Error)
        print("Application will be closed")
        input()
        exit(-1)

    try:
        print(discobot.functions.get_time_string() + " //:> Open " + BOT_NAME + "'s database connection")
        discobot.bot_config.connection = sqlite3.connect(DATABASE_PATH)
        # Для добавления в модуль конфигурации экземпляра соединения для текущего бота
        discobot.bot_config.cursor     = discobot.bot_config.connection.cursor()
        # Для добавления в модуль конфигурации экземпляра курсора для текущего бота
    except BaseException as err:
        print("Base connection error:", err)
        print("Application will be closed")

        try:
            log_file.write(discobot.functions.get_time_string() + " //:> Base connection error: " + str(err) + "\n")
            log_file.write("------------------- " + BOT_NAME + " session end -------------------\n")
            log_file.flush()
        except BaseException as fileErr:
            print(discobot.functions.get_time_string() + " //:> log file error:", fileErr)
        finally:
            log_file.close()
        input()
        exit(-1)



    try:

        discobot.bot_config.client.loop.create_task(discobot.bot_config.client.connect())
        discobot.bot_config.client.loop.create_task(discobot.bot_config.client.login(DISCORD_BOT_TOKEN))
        discobot.bot_config.client.loop.run_forever()

    except KeyboardInterrupt:

        print("\n" + discobot.functions.get_time_string() + " //:> " + BOT_NAME + " logout manually")

    finally:

        discobot.bot_config.client.loop.run_until_complete(discobot.bot_config.client.logout())
        print(discobot.functions.get_time_string() + " //:> " + BOT_NAME + " logout")

        discobot.bot_config.client.loop.close()
        print(discobot.functions.get_time_string() + " //:> " + BOT_NAME + "'s event loop is closed!")

        discobot.bot_config.connection.close()
        print(discobot.functions.get_time_string() + " //:> " + BOT_NAME + "'s database connection is closed!")

        try:
            log_file.write(discobot.functions.get_time_string() + " //:> Session ended;\n")
            log_file.write("------------------- " + BOT_NAME + " session end -------------------\n")
            log_file.flush()
        except BaseException as Error:
            print(discobot.functions.get_time_string() + " log file error: ", Error)

        log_file.close()
        print(discobot.functions.get_time_string() + " //:> " + BOT_NAME + "'s log file is closed!")

    input()
