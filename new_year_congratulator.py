import asyncio

import discobot.bot_config
import discobot.functions
import discobot.logging_events
import discobot.common_events
import datetime

from discobot.bot_config import DISCORD_BOT_TOKEN, kurologger

BOT_NAME          = "congratulator"
DATE_STRING       = discobot.functions.get_basetime_string()[:-4].replace(" ", "_").replace(":", "-")
SEND_MESSAGE_SIGN = False
# Одной строкой я привожу запись вида: ("%Y-%m-%d %H:%M:%S.%f")[:-3]
# к записи вида:  "%Y-%m-%d_%H-%M-%S"

LOGS_PATH, __ = discobot.functions.init(BOT_NAME, DATE_STRING, SEND_MESSAGE_SIGN)

del __


async def new_year_greetings():

    await asyncio.sleep(5)

    Konosuba     = discobot.bot_config.client.get_channel(200910511536078848)
    Neosilyators = discobot.bot_config.client.get_channel(233963643153154048)
    Bratki       = discobot.bot_config.client.get_channel(361255560836022276)
    Darkest      = discobot.bot_config.client.get_channel(643341791961153536)
    Eternal_dojo = discobot.bot_config.client.get_channel(485502199498014752)

    message_string = ":chicken: Kurochka Tochnogo Vremeni nachinaet svoyu rabotu! :chicken:"
    
    await Darkest.send(message_string)
    await Konosuba.send(message_string)
    await Bratki.send(message_string)
    await Neosilyators.send(message_string)
    await Eternal_dojo.send(message_string)

    poyas_1 = True
    poyas_2 = True
    poyas_3 = True
    poyas_4 = True
    poyas_5 = True
    poyas_6 = True
    poyas_7 = True
    poyas_8 = True
    poyas_9 = True
    poyas_10 = True
    poyas_11 = True
    poyas_12 = True
    poyas_13 = True
    poyas_14 = True
    poyas_15 = True
    poyas_16 = True
    poyas_17 = True
    poyas_18 = True
    poyas_19 = True
    poyas_20 = True
    poyas_21 = True
    poyas_22 = True
    poyas_23 = True
    poyas_24 = True
    poyas_25 = True
    poyas_26 = True
    poyas_27 = True

    while (True):

        current_time = datetime.datetime.now()
        # print(current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
        # await Darkest.send("TEST " + current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])

        # TODO: High label
        if ((current_time.hour == 13) and (current_time.day == 31) and poyas_1):  # 1
            message_string = "Земля начинает встречать Новый Год! :raised_hand: :blush:\nТолько что, Новый Год наступил на островах Лайн, Кирибати - " \
                             "островах тихоокеанского государства, " \
                             "расположенного в Микронезии и Полинезии в Тихом океане"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_1 = False



        if ((current_time.hour == 14) and (current_time.day == 31) and poyas_2):  # 2
            message_string = "Новый Год наступил в Новой Зеландии и ещё части архипелагов в Тихом Океане. :no_mouth: "

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_2 = False


        if (current_time.hour == 15 and poyas_3):  # 3
            message_string = "Новый Год добрался до России!\nКамчатка и Чукотка уже празднуют :blush:\n" \
                             "(А также - обитатели островов Фиджи и некоторых других тихоокеанских островов)\n\n" \
                             "А мы ждём... :relieved: "

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_3 = False


        if (current_time.hour == 16 and poyas_4):  # 4
            message_string = "Beep, beep! Новый Год наступил в восточных районах Якутской области и на Сахалине, с праздником! :snowflake: "

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_4 = False


        if (current_time.hour == 17 and poyas_5):  # 5
            message_string = "Во Владивостоке, Уссурийске и Хабаровске (<:cyberbuller:628584590126219274>) " \
                             "только что наступил Новый Год! Курочка поздравляет жителей этих городов" \
                             " с наступившим 2020 годом <:astolfo_night:522965907723517966>"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_5 = False


        if (current_time.hour == 18 and poyas_6):  # 6
            message_string = "Новый Год наступил в Чите, Благовещенске, Забайкалье и Амурской области." \
                             "\nВ это же время, в Якутии дух холода – Чысхаан (наш Дедушка Мороз) исполняет все желания," \
                             " для этого нужно лишь прикоснуться к его волшебному посоху (:eggplant:) и произнести загаданное вслух.\n" \
                             "А я ещё Новый Год только что наступил в Японии <:ageyu:550674433392640020>"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_6 = False

        if (current_time.hour == 19 and poyas_7):  # 7
            message_string = "Иркутск, Улан-Удэ и Буряточки уже празднуют Новый Год\n А что делаете вы? <:ningyo:513676059124957186>"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_7 = False


        if (current_time.hour == 20 and poyas_8):  # 8
            message_string = "<a:Padoru:649593439612043264> Красноярск, с Новым Годом! <a:Padoru:649593439612043264>\n" \
                             "А ещё Алтайский край, Кемерово, Томск, Новосибирск и республика Тыва <:seigi:589722256121528330>"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_8 = False


        if (current_time.hour == 21 and poyas_9):  # 9 TODO: "Свердловск" - это ЕКАТЕРИНБУРГ И ВРЕМЯ В НЁМ НА ЧАС ПОЗЖЕ
            message_string = "<:seigi:589722256121528330> Омск и Свердловск <:seigi:589722256121528330>"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_9 = False

        if (current_time.hour == 22 and poyas_10):  # 10
            message_string = "Челябинск, с Новым Годом! (<:ningyo:513676059124957186>)," \
                             "а также Тюмень, Пермь, и республика Башкортостан. <:suave:497478213002592279>"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_10 = False


        if (current_time.hour == 23 and poyas_11):  # 11
            message_string = "Самара - городок... <:snuggle_2:633298863083487262> \nС Новым Годом, Самара! <:mikugasm:510524091132936194>\n" \
                             "Тольятти и Удмуртию - тоже с Новым Годом <:suave:497478213002592279>"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_11 = False


        if (current_time.hour == 0 and poyas_12):  # 12
            message_string = "<:povelitel_kurochek:628577389966000139> MOSKOW NEVER SLEEPS! <:povelitel_kurochek:628577389966000139>\n" \
                             "Новый Год уже в Москве! Uraaaa <:mikugasm:510524091132936194>\n\n" \
                             ":chicken: Povelitel Kurochek pozdravlyaet vseh s nastupivshim Novym Godom! :chicken:"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_12 = False


        # =========================================================== #
        # TODO: Middle label

        if (current_time.hour == 1 and poyas_13):  # 13
            message_string = "Последним городом России, встречающим Новый Год является Калининград! <:astolfo_night:522965907723517966>\n" \
                             "и..\n" \
                             "|| З Новим Роком, браття українці <:captain:628638561113079869> ||"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_13 = False

        if (current_time.hour == 2 and poyas_14):  # 14
            message_string = "Израиль (<:ningyo:513676059124957186>), Восточная Европа (Румыния, Греция и др.)," \
                             " Турция, Финляндия, часть Африки будут праздновать Новый Год. Когда? - да прямо СЕЙЧАС! :snowflake: <:hyperGudako:484271410529959946> :snowflake:"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_14 = False


        if (current_time.hour == 3 and poyas_15):  # 15
            message_string = "Западная и Центральная Европа (Бельгия, Италия, Франция, Венгрия, Швеция и др.)," \
                             " ещё одна часть Африки встречают Новый Год <:suave:497478213002592279>"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_15 = False


        if (current_time.hour == 4 and poyas_16):  # 16
            message_string = "Новый Год наступил на Нулевом меридиане (Гринвич), в Великобритании, Португалии, Гренландии, на Канарских островах," \
                             "и опять часть Африки."

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_16 = False


        if (current_time.hour == 5 and poyas_17):  # 17
            message_string = "Новый Год дошёл до Азорских островов. <:seigi:589722256121528330> "

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_17 = False


        if (current_time.hour == 6 and poyas_18):  # 18
            message_string = "Новый Год уже в Бразилии <:ningyo:513676059124957186>"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_18 = False


        if (current_time.hour == 7 and poyas_19):  # 19
            message_string = "Аргентина и восточная часть Южной Америки празднуют <:astolfo_night:522965907723517966>"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_19 = False


        if (current_time.hour == 8 and poyas_20):  # 20
            message_string = "Восточная Канада, много островов Карибского бассейна, часть Южной Америки встречают Новый Год :blush:"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_20 = False


        if (current_time.hour == 9 and poyas_21):  # 21
            message_string = "Канада (Оттава) и США (Вашингтон, Нью-Йорк), западная часть Южной Америки празднуют наступление Нового Года <:suave:497478213002592279>"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_21 = False


        if (current_time.hour == 10 and poyas_22):  # 22
            message_string = "Новый Год наступил в Центральных частях Канады и США (Чикаго, Хьюстон), Мексике и большинстве стран Латинской Америки."

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_22 = False


        if (current_time.hour == 11 and poyas_23):  # 23
            message_string = "Канада (Эдмонтон, Калгари) и США (Денвер, Феникс, Солт-Лейк-Сити) встречают Новый Год <:ningyo:513676059124957186>"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_23 = False


        if (current_time.hour == 12 and poyas_24):  # 24
            message_string = "Западные части Канады (Ванкувер), и западное побережье США (Лос-Анжелес, Сан-Франциско) в деле."

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_24 = False


        if ((current_time.hour == 13) and (current_time.day == 1) and poyas_25):  # 25
            message_string = "Новый Год наступил на Аляске. || <:seigi:589722256121528330> ещё немного осталось <:seigi:589722256121528330> ||"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_25 = False


        if ((current_time.hour == 14) and (current_time.day == 1) and poyas_26):  # 26
            message_string = "Гавайские острова (США), Таити и острова Кука встречают благодатную полночь, и с ней к ним приходит Новый Год <:ningyo:513676059124957186>"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_26 = False


        if ((current_time.hour == 15) and (current_time.day == 1) and poyas_27):  # 27
            message_string = "UTC−12 — часовой пояс, используемый в навигации и располагающийся между 180° и 172°30′ западной долготы.\n" \
                             "В данном часовом поясе нет каких-либо обитаемых территорий, его используют только корабли.\n" \
                             "В этом поясе находятся также принадлежащие США необитаемые острова Бейкер и Хауленд.\n" \
                             "Этот часовой пояс — последний, в котором начинаются новые сутки, и как следствие - Новый Год\n\n" \
                             "Ну, вот и всё. Теперь вся Земля вошла в 2020 год.\n\nЧто он нам принесёт - а чёрт его знает." \
                             " Желаю всем найти себя в этом году и следовать своим мечтам. Кто знает, быть может эта дорога однажды сделает вас счастливыми?.. \n" \
                             "Счастья, крепкого здоровья и, конечно же, побольше удачи всем вам, таким разным, но таким любимым <:povelitel_kurochek:628577389966000139> :heart:\n\n" \
                             "Kurochka Tochnogo Vremeni zavershaet svoyu rabotu. <:astolfo_night:522965907723517966>\n" \
                             "|| Ved dazhe kurochkam nado otdyhat <:suave:497478213002592279> ||"

            await Darkest.send(message_string)
            await Konosuba.send(message_string)
            await Bratki.send(message_string)
            # await Neosilyators.send(message_string)
            await Eternal_dojo.send(message_string)

            poyas_27 = False

        # TODO: Low label

        await asyncio.sleep(5)  # Делаем sleep, чтобы не грузить процессор запросами по чём зря


async def get_channel_objects():

    # 200910511536078848    Konosuba    Official    200910511536078848    general
    # 233963643153154048    Неосиляторы             233963643153154048    autism
    # 361255560836022274    Братки                  361255560836022276    text
    # 415854406756728855    Darkest_Server          643341791961153536    system
    # 485502198944497666    eternal    dojo         485502199498014752    general

    Konosuba     = discobot.bot_config.client.get_channel(200910511536078848)
    Neosilyators = discobot.bot_config.client.get_channel(233963643153154048)
    Bratki       = discobot.bot_config.client.get_channel(361255560836022276)
    Darkest      = discobot.bot_config.client.get_channel(643341791961153536)
    eternal_dojo = discobot.bot_config.client.get_channel(485502199498014752)

    return Konosuba, Neosilyators, Bratki, Darkest, eternal_dojo


@discobot.bot_config.client.event
async def on_ready():
    login_string = f"\nLogged in as" \
                   f"    User.name = {discobot.bot_config.client.user.name}" \
                   f"    User.id   = {discobot.bot_config.client.user.id}" \
                   f"Latency: {discobot.bot_config.client.latency}" \
                   f"\nClient is ready!"
    kurologger.info(msg = login_string)


# Эта секция - и есть функция main, если скрипт запущен непосредственно (Не вызваны из других файлов)
if __name__ == "__main__":

    if ((datetime.datetime.now().day != 31) or (datetime.datetime.now().month != 12)):
        print("Invalid start date (start this module on 31.12.xx, in last day of year), application will be closed")
        input()
        exit(-1)


    kurologger.info(msg = "------------------- " + BOT_NAME + " session start -------------------\n")
    kurologger.info(msg = "Session started;\n")

    try:

        discobot.bot_config.client.loop.create_task(discobot.bot_config.client.connect())
        discobot.bot_config.client.loop.create_task(discobot.bot_config.client.login(DISCORD_BOT_TOKEN))
        discobot.bot_config.client.loop.create_task(new_year_greetings())
        discobot.bot_config.client.loop.run_forever()

    except KeyboardInterrupt:

        print("\n" + discobot.functions.get_time_string() + " //:> " + BOT_NAME + " logout manually")

    finally:

        discobot.bot_config.client.loop.run_until_complete(discobot.bot_config.client.logout())
        print(discobot.functions.get_time_string() + " //:> " + BOT_NAME + " logout")

        discobot.bot_config.client.loop.close()
        print(discobot.functions.get_time_string() + " //:> " + BOT_NAME + "'s event loop is closed!")

        try:
            log_file.write(discobot.functions.get_time_string() + " //:> Session ended;\n")
            log_file.write("------------------- " + BOT_NAME + " session end -------------------\n")
            log_file.flush()
        except BaseException as Error:
            print(discobot.functions.get_time_string() + " log file error: ", Error)

        log_file.close()
        print(discobot.functions.get_time_string() + " //:> " + BOT_NAME + "'s log file is closed!")

    input()
