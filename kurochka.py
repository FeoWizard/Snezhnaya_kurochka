import discobot.bot_config
import discobot.functions
import discobot.logging_events
import discobot.common_events
import discord
import sqlite3
import re

from datetime import timedelta, datetime

from discobot.bot_config import DISCORD_BOT_TOKEN
from discobot.bot_config import IMAGES_PATH

BOT_NAME             = "Kurochka"
DATE_STRING          = discobot.functions.get_basetime_string()[:-4].replace(" ", "_").replace(":", "-")
SEND_MESSAGE_SIGN    = True
CHANNEL_GRAPPLE_SIGN = True
BOT_START_TIME       = datetime.now()
# Одной строкой я привожу запись вида: ("%Y-%m-%d %H:%M:%S.%f")[:-3]
# к записи вида:  "%Y-%m-%d_%H-%M-%S"

LOGS_PATH, DATABASE_PATH = discobot.functions.init(BOT_NAME, DATE_STRING, SEND_MESSAGE_SIGN, CHANNEL_GRAPPLE_SIGN)
# =============================================== СОБЫТИЯ MESSAGE LOOP =============================================== #


@discobot.bot_config.client.event
async def on_message(message):
    is_bot_mentioned        = False
    is_this_bot_message     = False
    is_this_private_message = False
    is_this_Snezhinka       = False

    time_string = message.created_at + timedelta(hours = 3)  # Прибавляем разницу между UTC+0 и UTC+3
    time_string = datetime.strftime(time_string, "%Y-%m-%d %H:%M:%S.%f")[:-3]  # Приводим к формату

    username       = discobot.functions.get_username(message.author)
    att_list       = message.attachments
    message_string = message.content
    user_id        = message.author.id
    message_id     = message.id
    channel_id     = message.channel.id
    is_deleted     = 0
    is_edited      = 0  # имеет смысл NULL

    if (message.author == discobot.bot_config.client.user):

        is_this_bot_message = True

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

        message_text = "Пользователь {} написал в личные сообщения!" \
                       "\n=====================================Текст сообщения:\n{}" \
                       "\n=====================================Прикрепления:\n{}" \
                       "\n=====================================Встроенный контент:\n{}".format(message.author,
                                                                                               message.content,
                                                                                               message.attachments,
                                                                                               message.embeds)
        await discobot.functions.send_mail("ilromik@rambler.ru", "СООБЩЕНИЕ ОТ КУРОЧКИ", message_text)
        del message_text

    else:

        server_id    = message.guild.id
        server_name  = message.guild.name
        channel_name = message.channel.name

    # =========================== ЛОГГЕР ЗДЕСЬ ====================================================================== #

    if (message.channel.id in discobot.functions.channel_semaphore_list):
        data_list = [None, time_string, server_name, server_id, channel_name, channel_id, username, user_id,
                     message_string, message_id, str(att_list), is_deleted, is_edited]

        await discobot.functions.database_message_log_write(data_list)

    # =========================== ЛОГГЕР ЗДЕСЬ ====================================================================== #

    if discobot.bot_config.client.user.mentioned_in(message):
        is_bot_mentioned = True

    message_string = message_string.lower()

# =============================================== Отправляем картинки =============================================== #

    try:

        if (("!migalka" in message_string) and (not is_this_bot_message)):
            image_file = discord.File(IMAGES_PATH + "migalka.gif", filename = "Migalka.gif")
            if SEND_MESSAGE_SIGN:
                await message.channel.send(file = image_file)

        if (("!momonga" in message_string) and (not is_this_bot_message)):
            image_file = discord.File(IMAGES_PATH + "momonga.png", filename = "MOMONGA.png")
            if SEND_MESSAGE_SIGN:
                await message.channel.send(file = image_file)

        if (("!heil_lina" in message_string) and (not is_this_bot_message)):
            image_file = discord.File(IMAGES_PATH + "sticker_heil_lina.png", filename = "Heil_Lina.png")
            if SEND_MESSAGE_SIGN:
                await message.channel.send(file = image_file)

        if (("!povelitel_kurochek" in message_string) and (not is_this_bot_message)):
            image_file = discord.File(IMAGES_PATH + "pov_kur_0001.png", filename = "Snezhinka_povelitel_kurochek.png")
            if SEND_MESSAGE_SIGN:
                await message.channel.send(file = image_file)

        if (("!no_bully" in message_string) and (not is_this_bot_message)):
            image_file = discord.File(IMAGES_PATH + "no_bully.png", filename = "no_bully.png")
            if SEND_MESSAGE_SIGN:
                await message.channel.send(file = image_file)

    except BaseException as imageErr:
        try:  # пишем в файл ошибку - пытаемся
            discobot.bot_config.log_file.write(discobot.functions.get_time_string() + " //:> image send error: "
                                               + str(imageErr) + "\n")
            discobot.bot_config.log_file.flush()
        except BaseException as log_file_err:  # если НЕ ВЫШЛО - то хотя бы в консоль выведем весь пиздец
            print(discobot.functions.get_time_string() + " //:> log file error:", log_file_err)
        finally:
            print(discobot.functions.get_time_string() + " //:> image send error:", imageErr)

# =============================================== Отправляем картинки =============================================== #

# ==================================================== Общаемся ===================================================== #

    good_night_regexp = re.findall(r"!spoko[i, y]no[i, y].nochi", message_string)

    if ((("привет" in message_string) or ("privet" in message_string))
            and ((is_bot_mentioned) or (is_this_private_message))
            and not is_this_bot_message):

        if SEND_MESSAGE_SIGN:
            await message.channel.send("Priveeet, ya - " + discobot.bot_config.client.user.name
                                                         + "! :wave::blush:")

        # 152107008625999873 - ID Kaoru
        # 125159119622635520 - ID Snezhinki
    elif (message.author.id == 152107008625999873):
        emoji = "<:suave:497478213002592279>"
        await message.add_reaction(emoji)

    elif (message_string.startswith("!name") and is_this_Snezhinka):
        print(discobot.functions.get_time_string() + " //:> bot name:", BOT_NAME)

    elif (message_string.startswith("!emo") and is_this_Snezhinka):



        pass

    elif(message_string.startswith("!uptime")):
        uptime = await discobot.functions.uptime(BOT_START_TIME)
        if SEND_MESSAGE_SIGN:
            await message.channel.send("Current bot uptime: " + uptime)


    elif (message_string.startswith("!rand") and (not is_this_bot_message)):
        await discobot.functions.send_rand_number(message_string, message.channel, message.author)

    elif ((len(good_night_regexp) > 0) and (not is_this_bot_message)):

        if SEND_MESSAGE_SIGN:
            await message.channel.send("Spokoynoy nochi, " + message.author.mention + " :raised_hand::blush:")

    elif ("!date" in message_string):
        # Нужно ли что - то сюда писать?
        pass

    elif (("!nitro" in message_string) and (not is_this_bot_message) and (not is_this_private_message)):
        await discobot.functions.get_nitro_status(message)

    elif (("!help" in message_string) and (not is_this_bot_message)):
        help_message = "Privet, vot spisok realizovannyh command:\n" \
               "1) !help      - vyzvat spravku\n" \
               "2) Upomyanut bota i skazat \"privet\" - bot pozdorovaetsya s vami :wave::blush:\n" \
               "2) !nitro     - proverit kto bustil server\n" \
               "3) !momonga   - vyzvat momongu\n" \
               "4) !migalka   - vklyuchit migalku!\n" \
               "5) !heil_lina - privetstvovat Linu! :relieved:\n" \
               "6) !povelitel_kurochek - pokazat Snezhinku :blush: \n" \
               "7) !spokoynoy_nochi    - pozhelat spokoynoy nochi :sleeping: \n" \
               "8) !owner  - vyvesti administratora servera \n" \
               "9) !NY     - vyvesti vremya do Novogo Goda! \n" \
               "10)!rand <number> - generator celyh randomnyh chisel\n" \
               "11)!coin - podbrosit monetu\n" \
               "12)!ava <username/nick> or !ava <@user_mention> - poluchit avatar polzovatelya\n" \
               "13)!uptime - uznat tekushiy period raboty bota"
        if SEND_MESSAGE_SIGN:
            await message.channel.send(help_message)

    # elif message.content.startswith("!reboot"):
    #     print("//:> bot reboot initialized")
    #     reboot_code = True
    #     await discobot.bot_config.client.logout()
    #     asyncio.sleep(1)
    #     discobot.bot_config.client.loop.stop()

    # elif ( message.content.startswith("!block")
    #        and (not is_this_bot_message)
    #        and (not is_this_private_message)):
    #
    #     await discobot.functions.create_filter_record(message.author, message.author.guild) TODO: Убрать функцию
    #
    #     # Чтобы не добавлялось в массив фильтра, при повторном запросе !block
    #     if (not (user_id, server_id) in Filter_list):
    #         Filter_list.append((user_id, server_id))
    #
    # elif ( message.content.startswith("!unblock")
    #        and (not is_this_bot_message)
    #        and (not is_this_private_message)):
    #
    #     await discobot.functions.delete_filter_record(user_id, server_id) TODO: Убрать функцию
    #
    #     # Чтобы удалялось только, когда в массиве фильтра уже есть такой эл-т, при повторном вызове команды !unblock
    #     if ( (user_id, server_id) in Filter_list):
    #         Filter_list.remove((user_id, server_id))
    #
    # elif (( "!filter" in message_string )
    #       and (not is_this_bot_message)
    #       and (not is_this_private_message) ):
    #
    #     await discobot.functions.get_filter_info(message.author, message.author.guild) TODO: Убрать функцию

    elif (("!ny" in message_string) and (not is_this_bot_message)):
        await discobot.functions.get_new_year_time(message)

    elif (("!coin" in message_string) and (not is_this_bot_message)):
        if SEND_MESSAGE_SIGN:
            await message.channel.send(message.author.mention + " " + discobot.functions.coin_toss())

    elif ((("!avatar" in message_string) or ("!ava" in message_string)) and (not is_this_bot_message)):
        await discobot.functions.ava_search(message)

    elif ((("!last_seen" in message_string) or ("!last_online" in message_string)) and (not is_this_bot_message)):
        await discobot.functions.find_last_online(message)


# ========================================= Сервисные команды ========================================= #

# Здесь !second_exit, чтобы не цеплялся основной бот
    elif ( message.content.startswith("!exit") and (is_this_Snezhinka) ):

        print(discobot.functions.get_time_string() + " //:> " + BOT_NAME + " shutdown initialized")
        discobot.bot_config.client.loop.stop()

    elif ( message.content.startswith("!shutdown") and (is_this_Snezhinka) ):
        print(discobot.functions.get_time_string() + " //:> " + BOT_NAME + " shutdown initialized")
        discobot.bot_config.client.loop.stop()

    elif ( message.content.startswith('!grapple') and (is_this_Snezhinka) ):
        if (discobot.functions.grappling_flag is False):  # Запускать "новый" грапплер, если "старый" уже неактивен
            await discobot.functions.all_channels_grapple()
        else:
            print(discobot.functions.get_time_string() + " //:> Grappler is already active!")


    elif ( message.content.startswith("!update") and (is_this_Snezhinka) ):
        discobot.functions.allowed_list = await discobot.functions.update_connections_list("User command!")


    elif ( not is_this_private_message ):

        # ======================================== Notifications processing ========================================= #

        if (message.content.startswith("!set_join_channel") and ((is_this_Snezhinka)
                                                                 or (message.author.id == message.guild.owner.id))):
            await discobot.functions.set_notification_channel(server_id, message.channel, "join", message.content)

        if (message.content.startswith("!set_leave_channel") and ((is_this_Snezhinka)
                                                                  or (message.author.id == message.guild.owner.id))):
            await discobot.functions.set_notification_channel(server_id, message.channel, "leave", message.content)

        if (message.content.startswith("!set_welcome_channel") and ((is_this_Snezhinka)
                                                                    or (message.author.id == message.guild.owner.id))):
            await discobot.functions.set_notification_channel(server_id, message.channel, "welcome", message.content)

        if (message.content.startswith("!set_welcome_message") and ((is_this_Snezhinka)
                                                                    or (message.author.id == message.guild.owner.id))):
            await discobot.functions.set_welcome_message(server_id, message.channel, message.content)

        # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = #


        if (message.content.startswith("!del_join_channel") and ((is_this_Snezhinka)
                                                                 or (message.author.id == message.guild.owner.id))):
            await discobot.functions.del_notification_channel(server_id, message.channel, "join", message.content)

        if (message.content.startswith("!del_leave_channel") and ((is_this_Snezhinka)
                                                                  or (message.author.id == message.guild.owner.id))):
            await discobot.functions.del_notification_channel(server_id, message.channel, "leave", message.content)

        if (message.content.startswith("!del_welcome_channel") and ((is_this_Snezhinka)
                                                                    or (message.author.id == message.guild.owner.id))):
            await discobot.functions.del_notification_channel(server_id, message.channel, "welcome", message.content)

        # = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = #

        # show_notification_channels(server_id: int, channel, role: str, mode: str):

        if (message.content.startswith("!get_join_channel") and ((is_this_Snezhinka)
                                                                 or (message.author.id == message.guild.owner.id))):
            await discobot.functions.show_notification_channels(server_id, message.channel, "join", "one_role")

        if (message.content.startswith("!get_leave_channel") and ((is_this_Snezhinka)
                                                                  or (message.author.id == message.guild.owner.id))):
            await discobot.functions.show_notification_channels(server_id, message.channel, "leave", "one_role")

        if (message.content.startswith("!get_welcome_channel") and ((is_this_Snezhinka)
                                                                    or (message.author.id == message.guild.owner.id))):
            await discobot.functions.show_notification_channels(server_id, message.channel, "welcome", "one_role")

        if (message.content.startswith("!get_all_channels") and ((is_this_Snezhinka)
                                                                 or (message.author.id == message.guild.owner.id))):
            await discobot.functions.show_notification_channels(server_id, message.channel, "", "all")

        # ======================================== Notifications processing ========================================= #

        if ( message.content.startswith("!owner") ):
            owner = "Server owner: " + discobot.functions.get_username(message.guild.owner)
            if SEND_MESSAGE_SIGN:
                await message.channel.send(owner)
            # stupid_bitch_id = 475327581449879563
            # stupid_bitch = "@名無し1725#3665"
            # await message.guild.ban(stupid_bitch, reason = "Pidoras ebanyi")

        elif (message.content.startswith("!buffer") and (is_this_Snezhinka)):
            print(discobot.functions.get_time_string() + " //:> message buffer count:",
                  (discobot.functions.message_buffer_counter()))

        elif (message.content.startswith("!flush") and (is_this_Snezhinka)):
            await discobot.functions.message_buffer_flush()


# =============================================== СОБЫТИЯ MESSAGE LOOP =============================================== #


# Эта секция - и есть функция main, если скрипт запущен непосредственно (Не вызваны из других файлов)
if __name__ == "__main__":
    # ==============================================================================
    # file_mode = "w"
    # temp_file = open( "logs/" + BOT_NAME + "/message_edit_temp.txt", file_mode, encoding="utf-8")
    # ==============================================================================

    file_mode = "w"
    try:
        log_file = open(LOGS_PATH, file_mode, encoding = "utf-8")
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
        discobot.bot_config.cursor = discobot.bot_config.connection.cursor()
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

    # Здесь заполнение массива фильтров логгирования ================================================================ #
    # try:
    #     discobot.bot_config.cursor.execute(
    #         "SELECT Exception_Users.UserID, Exception_Users.ServerID FROM Exception_Users")
    #     Filter_list = discobot.bot_config.cursor.fetchall()
    # except BaseException as databaseErr:
    #     print("Critical database error, application will be closed")
    #
    #     try:
    #         log_file.write(
    #             discobot.functions.get_time_string() + " //:> Critical database error: " + str(databaseErr) + "\n")
    #         log_file.write("------------------- " + BOT_NAME + " session end -------------------\n")
    #         log_file.flush()
    #     except BaseException as fileErr:
    #         print(discobot.functions.get_time_string() + " //:> log file error:", fileErr)
    #     finally:
    #         log_file.close()
    #     input()
    #     exit(-1)
    # Здесь заполнение массива фильтров логгирования ================================================================ #

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
