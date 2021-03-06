import discord



def get_intents():
    intents = discord.Intents.all()
    return intents


file_mode = "r"
try:
    token_file = open("discobot/token", file_mode, encoding="utf-8")
    DISCORD_BOT_TOKEN = token_file.readline().strip("")
    # MAIL_LOGIN        = token_file.readline().strip()
    # MAIL_PASSWORD     = token_file.readline().strip()
    # MAIL_DOMAIN       = token_file.readline().strip()
    token_file.close()
except BaseException as Error:
    print("Critical token file error:", Error)
    print("Application will be closed")
    input()
    exit(-1)

activity   = discord.Activity(type = discord.ActivityType.watching, name = "за курочками")
client     = discord.Client(activity = activity, status = discord.Status.online, intents = get_intents())

DATABASE_PATH     = "databases/"
LOGS_PATH         = "logs/"
IMAGES_PATH       = "images/"
SEND_MESSAGE_SIGN = None

cursor     = None
log_file   = None
connection = None
