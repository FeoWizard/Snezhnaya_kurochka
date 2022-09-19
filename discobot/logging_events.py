import discord

import discobot.bot_init
import discobot.functions
import discobot.common_events

from datetime            import datetime, timedelta
from asyncio             import sleep
from discobot.bot_init import kurologger


@discobot.bot_init.client.event
async def on_member_join(member: discord.Member):
    data_list = [ None, discobot.functions.get_basetime_string(), member.id, discobot.functions.get_username(member),
                  None, member.guild.id, member.guild.name, None, None, "ARRIVE" ]
    await discobot.functions.database_user_log_write(data_list)
    if (discobot.bot_init.SEND_MESSAGE_SIGN):
        await discobot.functions.send_notification(member, "welcome", "prishel na server! :raised_hand::blush:")
        await discobot.functions.send_welcome_message(member)

    roles_ids = await discobot.functions.get_user_roles(member.id)
    await discobot.functions.set_user_roles(member, roles_ids)


@discobot.bot_init.client.event
async def on_member_remove(member: discord.Member):
    data_list = [ None, discobot.functions.get_basetime_string(), member.id, discobot.functions.get_username(member),
                  None, member.guild.id, member.guild.name, None, None, "LEAVE" ]
    await discobot.functions.database_user_log_write(data_list)
    await discobot.functions.save_user_roles(member)
    if (discobot.bot_init.SEND_MESSAGE_SIGN):
        await discobot.functions.send_notification(member, "leave", "ushel s servera <:aqua_sad:504357956499013633>")


@discobot.bot_init.client.event
async def on_member_update(before, after):
    if (before.nick != after.nick):
        data_list = [ None, discobot.functions.get_basetime_string(), before.id, discobot.functions.get_username(before),
                      None, before.guild.id, before.guild.name, before.nick, after.nick, "NICKNAME_CHANGE" ]
        await discobot.functions.database_user_log_write(data_list)

    offline = discobot.bot_init.discord.Status.offline
    if ((before.status != offline) and (after.status == offline)) \
            or ((before.status == offline) and (after.status != offline)):

        last_seen = discobot.functions.get_basetime_string()

        try:
            discobot.bot_init.cursor.execute("UPDATE Connected_Users "
                                               "SET last_seen    = ? "
                                               "WHERE UserID     = ?", [ last_seen, before.id ])
            discobot.bot_init.connection.commit()
        except BaseException as databaseErr:
            discobot.functions.create_database_error_record(databaseErr)


@discobot.bot_init.client.event
async def on_user_update(before, after):
    if (before.avatar != after.avatar):
        return
    else:
        data_list = [ None, discobot.functions.get_basetime_string(), before.id, discobot.functions.get_username(before),
                      discobot.functions.get_username(after), None, None, None, None, "RENAME" ]
        await discobot.functions.database_user_log_write(data_list)


@discobot.bot_init.client.event
async def on_member_ban(guild, user):
    data_list = [ None, discobot.functions.get_basetime_string(), user.id, discobot.functions.get_username(user), None,
                  guild.id, guild.name, None, None, "USER_BAN" ]
    await discobot.functions.database_user_log_write(data_list)
    if (discobot.bot_init.SEND_MESSAGE_SIGN):
        await discobot.functions.send_notification(user, "leave",
                                                   "byl zabanen na servere <:yoba_pepe:628582829709852702>"
                                                   "<:gun:735749719216750594>", guild)


@discobot.bot_init.client.event
async def on_member_unban(guild, user):
    data_list = [ None, discobot.functions.get_basetime_string(), user.id, discobot.functions.get_username(user), None,
                  guild.id, guild.name, None, None, "USER_UNBAN" ]
    await discobot.functions.database_user_log_write(data_list)
    if (discobot.bot_init.SEND_MESSAGE_SIGN):
        await discobot.functions.send_notification(user, "welcome", "byl razbanen <:ningyo:513676059124957186>", guild)


# События сообщений ================================================================================================= #


@discobot.bot_init.client.event
async def on_raw_message_delete(payload):
    data_list = (payload.guild_id, payload.channel_id, payload.message_id)

    try:
        discobot.bot_init.cursor.execute("""
        UPDATE Messages SET is_deleted = 1 
        WHERE Messages.ServerID = (?) 
        AND Messages.ChannelID = (?) 
        AND Messages.MessageID = (?)""", data_list)
        discobot.bot_init.connection.commit()
    except BaseException as databaseErr:
        discobot.functions.create_database_error_record(databaseErr)


@discobot.bot_init.client.event
async def on_raw_message_edit(payload):
    # TODO: Переделать grappler на полноценную асинхронку
    return

    data_list = (payload.channel_id, payload.message_id)

    try:  # Помечаем сообщение в основной таблице, как изменённое
        discobot.bot_init.cursor.execute("""
                                           UPDATE Messages SET is_edited = 1 
                                           WHERE Messages.ChannelID = (?) 
                                           AND Messages.MessageID = (?)""", data_list)
        discobot.bot_init.connection.commit()
    except BaseException as databaseErr:
        discobot.functions.create_database_error_record(databaseErr)


    try:
        discobot.bot_init.cursor.execute("""
        SELECT *
        FROM Edited_Messages
        WHERE Edited_Messages.MessageID = (?)
        ORDER BY Date DESC
        LIMIT 1""", [payload.message_id])

        result      = discobot.bot_init.cursor.fetchall()  # Возвращает list of tuples вида [(x,), (y,), (z,)]
        result_list = list(discobot.functions.itertools.chain.from_iterable(result))

    except BaseException as databaseErr:
        discobot.functions.create_database_error_record(databaseErr)
        result      = None
        result_list = None

    if (result):
        # Если сообщение уже менялось
        result_list[0] = None
        result_list[1] = discobot.functions.get_basetime_string()
        result_list[8] = result_list[9]  # Меняем местами старое и новые значения,т.к. это "новое" - теперь будет старым

        if (payload.data.get("content")):
            message_new = payload.data.get("content")
        else:
            message_new = payload.data.get("embeds")[0].get("url")

        result_list[9] = message_new

    else:
        # Если сведения об изменениях отсутствуют
        # Надо собрать нужную информацию перед записью изменённого сообщения
        # Достать из базы сообщение с этим ID

        while(True):
            try:
                discobot.bot_init.cursor.execute("""
                SELECT *
                FROM Messages 
                WHERE Messages.ChannelID = (?) 
                AND Messages.MessageID = (?)""", data_list)

                result      = discobot.bot_init.cursor.fetchall()  # Возвращает list of tuples вида [(x,), (y,), (z,)]
                result_list = list(discobot.functions.itertools.chain.from_iterable(result))

                if (result is None):
                    discobot.functions.create_database_error_record(databaseErr = BaseException("Original of modified message not found!"))
                    return

                break  # Выходим, только если всё завершилось успешно

            except BaseException as databaseErr:
                discobot.functions.create_database_error_record(databaseErr)
                await sleep(5)

        result_list.pop()
        result_list.pop()

        result_list[0] = None
        result_list[1] = discobot.functions.get_basetime_string()

        if (payload.data.get("content")):
            message_new = payload.data.get("content")
        else:
            message_new = payload.data.get("embeds")[0].get("url")

        result_list.insert(9, message_new)

    try:
        discobot.bot_init.cursor.execute("INSERT INTO Edited_Messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                         result_list)
        discobot.bot_init.connection.commit()
    except BaseException as databaseErr:
        discobot.functions.message_buffer.append(tuple(result_list))
        discobot.functions.create_database_error_record(databaseErr)
        await discobot.functions.create_log_record("The message was not recorded to the database, "
                                                   + str(len(discobot.functions.message_buffer))
                                                   + " messages in message buffer")


# События серверов ================================================================================================== #
"""data_list = [None, Date, ServerID, Old_server_name, New_server_name, Server_event]"""


@discobot.bot_init.client.event
async def on_guild_join(guild):
    data_list = [ None, discobot.functions.get_basetime_string(), guild.id, guild.name, None, "SERVER_INVITE" ]
    await discobot.functions.database_server_log_write(data_list)
    discobot.functions.allowed_list = await discobot.functions.update_connections_list("on_guild_join")
    if (discobot.functions.grappling_flag is False):  # Запускать "новый" грапплер, если "старый" уже неактивен
        await discobot.functions.all_channels_grapple()
    else:
        kurologger.info(msg = "Grappler is already active!")


@discobot.bot_init.client.event
async def on_guild_remove(guild):
    data_list = [ None, discobot.functions.get_basetime_string(), guild.id, guild.name, None, "SERVER_LEAVE" ]
    await discobot.functions.database_server_log_write(data_list)
    discobot.functions.allowed_list = await discobot.functions.update_connections_list("on_guild_remove")


@discobot.bot_init.client.event
async def on_guild_update(before, after):
    if (before.name != after.name):
        data_list = [None, discobot.functions.get_basetime_string(), before.id,
                     before.name, after.name, "SERVER_RENAME"]
        await discobot.functions.database_server_log_write(data_list)

    else:
        return None

# События серверных каналов ========================================================================================= #
"""data_list = [None, Date, ServerID, Server, ChannelID,
                Old_Channel_Name, New_Channel_Name, Channel_event]"""


@discobot.bot_init.client.event
async def on_guild_channel_create(channel):
    data_list = [None, discobot.functions.get_basetime_string(), channel.guild.id, channel.guild.name, channel.id,
                 channel.name, None, "GUILD_CHANNEL_CREATE"]
    await discobot.functions.database_channel_log_write(data_list)
    discobot.functions.allowed_list = await discobot.functions.update_connections_list("on_guild_channel_create")


@discobot.bot_init.client.event
async def on_guild_channel_delete(channel):
    data_list = [None, discobot.functions.get_basetime_string(), channel.guild.id, channel.guild.name, channel.id,
                 channel.name, None, "GUILD_CHANNEL_REMOVE"]
    await discobot.functions.database_channel_log_write(data_list)
    discobot.functions.allowed_list = await discobot.functions.update_connections_list("on_guild_channel_delete")


@discobot.bot_init.client.event
async def on_guild_channel_update(before, after):
    member             = before.guild.me
    permissions_before = before.permissions_for(member)
    permissions_after  = after.permissions_for(member)

    if ( ( permissions_before.read_messages              != permissions_after.read_messages)
            or ( permissions_before.read_message_history != permissions_after.read_message_history) ):
        discobot.functions.allowed_list = await discobot.functions.update_connections_list("on_guild_channel_update")

    if ( permissions_before.read_message_history is False ) and ( permissions_after.read_message_history is True):
        await discobot.functions.channel_grappler(after)

    if (before.name != after.name):
        data_list = [ None, discobot.functions.get_basetime_string(), before.guild.id, before.guild.name, before.id,
                      before.name, after.name, "GUILD_CHANNEL_RENAME" ]
        await discobot.functions.database_channel_log_write(data_list)

# События серверных каналов ========================================================================================= #


@discobot.bot_init.client.event
async def on_private_channel_create(channel):
    data_list = [ None, discobot.functions.get_basetime_string(), None, None, channel.id,
                  str(channel), None, "PRIVATE_CHANNEL_CREATE" ]
    await discobot.functions.database_channel_log_write(data_list)
    discobot.functions.allowed_list = await discobot.functions.update_connections_list("on_private_channel_create")

    try:
        discobot.bot_init.cursor.execute(
            """
            SELECT Date
            FROM Messages
            WHERE ChannelID = ?
            ORDER BY id DESC
            LIMIT 1
            """, [channel.id])

        result = discobot.bot_init.cursor.fetchone()  # Вытаскиваю дату последнего сообщения в канале

        if (result is None):
            Database_Channel_Miss_Error_String = "\nExpecting last message date, received NONE; Channel: " \
                                                 + str(channel)[:14] + "\n"

            discobot.functions.create_database_error_record(BaseException(Database_Channel_Miss_Error_String))
            last_date = None

        else:
            last_date_string = result[0]
            last_date = datetime.strptime(last_date_string, "%Y-%m-%d %H:%M:%S.%f")

        await discobot.functions.channel_grappler(channel, last_date)

    except BaseException as databaseErr:
        discobot.functions.create_database_error_record(databaseErr)


@discobot.bot_init.client.event
async def on_private_channel_delete(channel):
    data_list = [ None, discobot.functions.get_basetime_string(), None, None, channel.id,
                  str(channel), None, "PRIVATE_CHANNEL_DELETE" ]
    await discobot.functions.database_channel_log_write(data_list)
    discobot.functions.allowed_list = await discobot.functions.update_connections_list("on_private_channel_delete")


@discobot.bot_init.client.event
async def on_private_channel_update(before, after):
    if (before.name != after.name):
        data_list = [ None, discobot.functions.get_basetime_string(), None, None, before.id,
                      str(before), str(after), "PRIVATE_CHANNEL_RENAME" ]
        await discobot.functions.database_channel_log_write(data_list)
    else:
        return None