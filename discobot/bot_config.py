import discord
import discobot.log_module as log_module

kurologger = log_module.Logger_Factory(bot_name = "Kurochka").get_logger(logger_name = "Kurologger", date = True)



def get_intents():
    intents = discord.Intents.all()
    return intents


file_mode = "r"
try:
    token_file = open("discobot/token", file_mode, encoding = "utf-8")
    DISCORD_BOT_TOKEN = token_file.readline().strip("")
    # MAIL_LOGIN        = token_file.readline().strip()
    # MAIL_PASSWORD     = token_file.readline().strip()
    # MAIL_DOMAIN       = token_file.readline().strip()
    token_file.close()
except BaseException as err:
    kurologger.error(msg = "Critical token file error:", exc_info = err)
    kurologger.error(msg = "Application will be closed", exc_info = err)
    input()
    exit(-1)

activity   = discord.Activity(type = discord.ActivityType.watching, name = "за курочками")
client     = discord.Client(activity = activity, status = discord.Status.online, intents = get_intents())

DATABASE_PATH     = "databases/"
LOGS_PATH         = "logs/"
IMAGES_PATH       = "images/"
SEND_MESSAGE_SIGN = None

cursor     = None
connection = None
