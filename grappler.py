from datetime import datetime

import discobot.bot_config
import discobot.functions
import discobot.common_events
import sqlite3

from discobot.bot_config import DISCORD_BOT_TOKEN

BOT_NAME             = "grappler"
DATE_STRING          = discobot.functions.get_basetime_string()[:-4].replace(" ", "_").replace(":", "-")
SEND_MESSAGE_SIGN    = False
CHANNEL_GRAPPLE_SIGN = True
# Одной строкой я привожу запись вида: ("%Y-%m-%d %H:%M:%S.%f")[:-3]
# к записи вида:  "%Y-%m-%d_%H-%M-%S"

LOGS_PATH, DATABASE_PATH = discobot.functions.init(BOT_NAME, DATE_STRING, SEND_MESSAGE_SIGN, CHANNEL_GRAPPLE_SIGN)


# =============================================== СОБЫТИЯ MESSAGE LOOP =============================================== #


@discobot.bot_config.client.event
async def on_message(message):

    if (message.author.id == 125159119622635520):
        is_this_Snezhinka = True
    else:
        is_this_Snezhinka = False

    if ( message.content.startswith("!grapexit") and (message.author.id == 125159119622635520) ):

        print(discobot.functions.get_time_string() + " //:> " + BOT_NAME + " shutdown initialized")
        discobot.bot_config.client.loop.stop()

    elif ( message.content.startswith("!shutdown") and (is_this_Snezhinka)):
        print(discobot.functions.get_time_string() + " //:> " + BOT_NAME + " shutdown initialized")
        discobot.bot_config.client.loop.stop()

    elif ( message.content.startswith("!update") and (message.author.id == 125159119622635520) ):
        discobot.functions.allowed_list = await discobot.functions.update_connections_list("User command!")

    elif ( message.content.startswith('!grapple') and (message.author.id == 125159119622635520) ):
        if (discobot.functions.grappling_flag is False):  # Запускать "новый" грапплер, если "старый" уже неактивен
            await discobot.functions.all_channels_grapple()
        else:
            print(discobot.functions.get_time_string() + " //:> Grappler is already active!")

    elif (message.content.startswith("!name") and is_this_Snezhinka):
        print(discobot.functions.get_time_string() + " //:> bot name:", BOT_NAME)

    if message.content.startswith('!grapdata'):  # Тестов ради
        # messages_list = await message.channel.history(limit=None, after=datetime(2019, 12, 6),
        #                                               oldest_first=True).flatten()
        #
        # for elem in messages_list:
        #     print(elem.content)

        discobot.bot_config.cursor.execute(
            "SELECT Date "
            "FROM Messages "
            "WHERE ChannelID = ? "
            "ORDER BY id DESC "
            "LIMIT 1", [message.channel.id])

        result = discobot.bot_config.cursor.fetchone()

        if (result is None):
            raise Exception("Expecting last message date, received NONE")

        last_date_string = result[0]
        last_date = datetime.strptime(last_date_string, "%Y-%m-%d %H:%M:%S.%f")
        print(last_date)


# =============================================== СОБЫТИЯ MESSAGE LOOP =============================================== #


# Эта секция - и есть функция main, если скрипт запущен непосредственно (Не вызваны из других файлов)
if __name__ == "__main__":
    # ==============================================================================
    # file_mode = "w"
    # temp_file = open("logs/grappler/grappler_temp.txt", file_mode, encoding = "utf-8")
    # ==============================================================================

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

# Здесь заполнение массива фильтров логгирования ======================================================================

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
