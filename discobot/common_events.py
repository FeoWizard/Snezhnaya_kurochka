import discobot.bot_config
import discobot.functions
import traceback
import sys

from discobot.bot_config import kurologger


@discobot.bot_config.client.event
async def on_error(event, *args, **kwargs):
    error_name = sys.exc_info()
    kurologger.error(msg = f"Unhandled error: {event} Start error description:", exc_info = error_name[1])


@discobot.bot_config.client.event
async def on_resumed():
    kurologger.info(msg = "Session resumed")


@discobot.bot_config.client.event
async def on_disconnect():
    kurologger.info(msg = "Client disconnected")


@discobot.bot_config.client.event
async def on_connect():
    kurologger.info(msg = "Client connected")


@discobot.bot_config.client.event
async def on_ready():
    discobot.functions.allowed_list = await discobot.functions.update_connections_list("on_ready")
    login_string = f"\n\nLogged in as\n" \
                   f"    User.name = {discobot.bot_config.client.user.name}\n" \
                   f"    User.id   = {discobot.bot_config.client.user.id}\n" \
                   f"Latency: {discobot.bot_config.client.latency}\n" \
                   f"\nClient is ready!\n"
    kurologger.info(msg = login_string)

    # Запускать "новый" грапплер, если "старый" уже неактивен
    if (discobot.functions.grappling_flag is False):
        await discobot.functions.all_channels_grapple()
    else:
        kurologger.info(msg = "Grappler is already active!")
