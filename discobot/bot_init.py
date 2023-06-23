import discord
from discord.ext import commands

import discobot.db
import discobot.log_module as log_module
from   discobot.bot_config import DISCORD_BOT_TOKEN, MAIL_DOMAIN, MAIL_LOGIN, MAIL_PASSWORD

intents    = discord.Intents.default()

kurologger = log_module.Logger_Factory(bot_name = "Kurochka").get_logger(logger_name = "Kurologger", date = True)
activity   = discord.Activity(type = discord.ActivityType.watching, name = "за курочками")
client     = discord.Client(activity = activity, status = discord.Status.online, intents = discord.Intents.all())
bot        = commands.Bot(command_prefix='>', intents=intents)

DATABASE_PATH     = "databases/"
LOGS_PATH         = "logs/"
IMAGES_PATH       = "images/"
SEND_MESSAGE_SIGN = None


# db_worker  = discobot.db.SQLiteWorker(database_path = DATABASE_PATH, logger = kurologger)

cursor     = None
connection = None
