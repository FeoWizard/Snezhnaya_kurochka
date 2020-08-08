import discobot.bot_config
import discobot.functions
import traceback
import sys


@discobot.bot_config.client.event
async def on_error(event, *args, **kwargs):

    error_name = sys.exc_info()

    try:
        await discobot.functions.create_log_record("\nUnhandled error! Start error description:")
        discobot.bot_config.log_file.write("\n")
        await discobot.functions.create_log_record("ErrorType", error_name[0])
        await discobot.functions.create_log_record("Error", error_name[1])

        discobot.bot_config.log_file.write("\n")
        discobot.bot_config.log_file.write("arguments: " + str(*args))
        discobot.bot_config.log_file.write("\n")
        discobot.bot_config.log_file.write("\nerror stacktrace:\n")
        discobot.bot_config.log_file.write("\n")
        traceback.print_exc(file = discobot.bot_config.log_file)
        discobot.bot_config.log_file.write("\n")
        discobot.bot_config.log_file.flush()
        await discobot.functions.create_log_record("End error description")
    except BaseException as fileErr:
        print(discobot.functions.get_time_string() + " //:> log file error:", fileErr)

    print(discobot.functions.get_time_string() + " //:> " + "Unhandled error! Description in log file\n\nErrorType:",
          error_name[0], "\nError:", error_name[1], end="\n\n")


@discobot.bot_config.client.event
async def on_resumed():
    await discobot.functions.create_log_record("Session resumed")
    print(discobot.functions.get_time_string() + " //:> Session resumed")


@discobot.bot_config.client.event
async def on_disconnect():
    await discobot.functions.create_log_record("Client disconnected")
    print(discobot.functions.get_time_string() + " //:> Disconnected")


@discobot.bot_config.client.event
async def on_connect():
    await discobot.functions.create_log_record("Client connected")
    print(discobot.functions.get_time_string() + " //:> Connected")


@discobot.bot_config.client.event
async def on_ready():
    discobot.functions.allowed_list = await discobot.functions.update_connections_list("on_ready")
    print("\nLogged in as")
    print("    User.name =", discobot.bot_config.client.user.name)
    print("    User.id   =",   discobot.bot_config.client.user.id)
    print("    Latency:   ",   discobot.bot_config.client.latency)
    print("Client is ready!\n")
    await discobot.functions.create_log_record("Client is ready!")
    if (discobot.functions.grappling_flag is False):  # Запускать "новый" грапплер, если "старый" уже неактивен
        await discobot.functions.all_channels_grapple()
    else:
        print(discobot.functions.get_time_string() + " //:> Grappler is already active!")
