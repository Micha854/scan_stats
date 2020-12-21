import MySQLdb
import time
import datetime
import telebot
import discord
import asyncio
import requests
import config


client = discord.Client()
bot = telebot.TeleBot(config.token)

async def my_background_task():
    old_message = ""
    overview_id = 0
    overview_discord = ""

    # load telegram overview_id
    try:
        f = open("telegram.txt", "r")
        overview_id = f.read()
        f.close()
    except:
        overview_id = 0

    # set default overview_id
    if overview_id == None:
        overview_id = 0

    await client.wait_until_ready() # ensures cache is loaded
    channel = client.get_channel(id=config.d_channel) # replace with target channel id

    # load discord overview_id
    if not overview_discord:        
        try:
            f = open("discord.txt", "r")
            overview_discord = await channel.fetch_message(f.read())
            f.close()
        except:
            overview_discord = ""
    
    while not client.is_closed():
        area_id = []
        area    = []
        proto   = []
        mode    = []

        try:
            connection = MySQLdb.connect(host=config.db_host, db=config.db_base, user=config.db_user, passwd=config.db_pass, port=config.db_port)
            cursor = connection.cursor()
        except:
            print("   ERROR: Kein Verbindungsaufbau zur Datenbank, probiere es in 15 Sekunden erneut")
            time.sleep(15)
            continue
        
        cursor.execute(f"SELECT t.area_id,a.name,t.lastProtoDateTime,a.mode,(SELECT COUNT(area_id) FROM trs_status WHERE area_id = a.area_id GROUP BY area_id) AS anzahl FROM trs_status t LEFT JOIN settings_area a ON t.area_id = a.area_id WHERE t.instance_id = {config.instance_id} AND a.instance_id = {config.instance_id} ORDER BY anzahl DESC, a.name ASC")

        all = list(cursor.fetchall())
        i = 0
        try:
            while i < len(all):
                area_id.append(all[i][0])
                area.append(all[i][1])
                proto.append(all[i][2])
                mode.append(all[i][3])
                i +=1
        except:
            print("fehler")

        cursor = cursor.close()
        connection.close()

        n = 0
        message = ""

        # total counter
        raids = 0
        mon   = 0
        quest = 0
        idle  = 0
        other = 0

        # active counter
        aktiv_mon   = 0
        aktiv_raids = 0
        aktiv_quest = 0
        aktiv_idle  = 0
        aktiv_other = 0

        # individual data
        indi_raids = ""
        indi_mon   = ""
        indi_quest = ""
        indi_idle  = ""
        indi_other = ""

        # individual data count
        indi_count_raids = 0
        indi_count_mon   = 0
        indi_count_quest = 0
        indi_count_idle  = 0
        indi_count_other = 0

        # fetch all individual areas
        e=0
        indi_area = {}
        for x in area:
            indi_area[x] = {"type": mode[e], "all": 0, "aktiv": 0, "result": 0}
            e+=1

        for x in area:
            last = datetime.datetime("1970-01-01 00:00:00").timestamp if proto[n] == None else datetime.datetime.strptime(str(proto[n]), '%Y-%m-%d %H:%M:%S').timestamp()
            now  = time.time()
            diff = now - last
            
            # individual areas
            indi_area[area[n]]["all"] +=1
            if diff < config.timeout_sek:
                indi_area[area[n]]["aktiv"] +=1

            # raids
            if mode[n] == 'raids_mitm':
                raids +=1
                if diff < config.timeout_sek: aktiv_raids +=1
            # mon
            elif mode[n] == 'mon_mitm' and 'iv_mitm':
                mon +=1
                if diff < config.timeout_sek: aktiv_mon   +=1
            # quest
            elif mode[n] == 'pokestops':
                quest +=1
                if diff < config.timeout_sek: aktiv_quest +=1
            # idle
            elif mode[n] == 'idle':
                idle +=1
                if diff < config.timeout_sek: aktiv_idle  +=1
            # other
            else:
                other +=1
                if diff < config.timeout_sek: aktiv_other +=1

            n +=1

        # create message for individual areas (option detail)
        for x in indi_area:
            if not x in config.area_exclude[:]:
                indi_area[x]["result"] = int(indi_area[x]["aktiv"]*100/indi_area[x]["all"])
                area_name = x + "          "
                #tab   = "  " if indi_area[x]["result"]   == 0 else (" " if indi_area[x]["result"]   < 100 else "")
                
                if indi_area[x]["type"] == 'raids_mitm':
                    tab   = "  " if indi_area[x]["result"]   == 0 else (" " if indi_area[x]["result"]   < 100 else "")
                    indi_raids+= "\u2796 <code> " + area_name[:12] + ": " + tab + str(indi_area[x]["result"]) + "% aktiv</code>\n"
                    indi_count_raids +=1
                elif indi_area[x]["type"] == 'mon_mitm' and 'iv_mitm':
                    tab   = "  " if indi_area[x]["result"]   == 0 else (" " if indi_area[x]["result"]   < 100 else "")
                    indi_mon+=   "\u2796 <code> " + area_name[:12] + ": " + tab + str(indi_area[x]["result"]) + "% aktiv</code>\n"
                    indi_count_mon +=1
                elif indi_area[x]["type"] == 'pokestops':
                    tab   = "  " if indi_area[x]["result"]   == 0 else (" " if indi_area[x]["result"]   < 100 else "")
                    indi_quest+= "\u2796 <code> " + area_name[:12] + ": " + tab + str(indi_area[x]["result"]) + "% aktiv</code>\n"
                    indi_count_quest +=1
                elif indi_area[x]["type"] == 'idle':
                    tab   = "  " if indi_area[x]["result"]   == 0 else (" " if indi_area[x]["result"]   < 100 else "")
                    indi_idle+=  "\u2796 <code> " + area_name[:12] + ": " + tab + str(indi_area[x]["result"]) + "% aktiv</code>\n"
                    indi_count_idle +=1
                else:
                    tab   = "  " if indi_area[x]["result"]   == 0 else (" " if indi_area[x]["result"]   < 100 else "")
                    indi_other+= "\u2796 <code> " + area_name[:12] + ": " + tab + str(indi_area[x]["result"]) + "% aktiv</code>\n"
                    indi_count_other +=1

        #print(indi_area)

        raids_stat = int(aktiv_raids*100/raids) if not raids == 0 else 0
        mon_stat   = int(aktiv_mon*100/mon)     if not mon   == 0 else 0
        quest_stat = int(aktiv_quest*100/quest) if not quest == 0 else 0
        idle_stat  = int(aktiv_idle*100/idle)   if not idle  == 0 else 0
        other_stat = int(aktiv_other*100/other) if not other == 0 else 0
        
        # stat title
        raid_scan  = "Raid "
        mon_scan   = "Mon  "
        quest_scan = "Quest"
        idle_scan  = "Sleep"
        other_scan = "Other"

        # format percent
        raid_tab  = "  " if raids_stat == 0 else (" " if raids_stat < 100 else "")
        mon_tab   = "  " if mon_stat   == 0 else (" " if mon_stat   < 100 else "")
        quest_tab = "  " if quest_stat == 0 else (" " if quest_stat < 100 else "")
        idle_tab  = "  " if idle_stat  == 0 else (" " if idle_stat  < 100 else "")
        other_tab = "  " if other_stat == 0 else (" " if other_stat < 100 else "")
        
        # message
        if config.option_raids: message+= "\u2694 <code>"     + raid_scan[:5]  + " Scanner: " + raid_tab  + str(raids_stat) + "% aktiv</code>\n"
        if config.option_raids == True and config.deteil_raids == True and indi_count_quest > 1: message += indi_raids
        if raids and config.deteil_raids == True: message += "\n"

        if config.option_mon:   message+= "\U0001F47E <code>" + mon_scan[:5]   + " Scanner: " + mon_tab   + str(mon_stat)   + "% aktiv</code>\n"
        if config.option_mon ==   True and config.deteil_mon ==   True and indi_count_mon > 1: message += indi_mon
        if mon and config.deteil_mon == True: message += "\n"

        if config.option_quest: message+= "\U0001F4DC <code>" + quest_scan[:5] + " Scanner: " + quest_tab + str(quest_stat) + "% aktiv</code>\n"
        if config.option_quest == True and config.deteil_quest == True and indi_count_quest > 1: message+= indi_quest
        if quest and config.deteil_quest == True: message += "\n"

        if config.option_idle:  message+= "\U0001F634 <code>" + idle_scan[:5]  + " Scanner: " + idle_tab  + str(idle_stat)  + "% aktiv</code>\n"
        if config.option_idle ==  True and config.detail_idle ==  True and indi_count_idle > 1: message+= indi_idle
        if idle and config.detail_idle == True: message += "\n"

        if config.option_other: message+= "\u2754 <code>"     + other_scan[:5] + " Scanner: " + other_tab + str(other_stat) + "% aktiv</code>\n"
        if config.option_other == True and config.detail_other == True and indi_count_other > 1: message+= indi_other
        if other and config.detail_other == True: message += "\n"

        if config.update_message == True:
            message+= "\n\u23F1 last update: <code>" + datetime.datetime.now().strftime('%d.%m.%y %H:%M:%S') + "</code>\n"
            stand = None
        else:
            stand = "\n\u23F1 <code>Stand: " + datetime.datetime.now().strftime('%d.%m.%y %H:%M:%S') + "</code>\n"

        if not message == old_message:
            send_message = message+stand if not stand == None else message
            
            # discord
            if config.discord == True:
                discord_message = "\n" + send_message.replace('<code>','').replace('</code>','')

                try:
                    await overview_discord.edit(content=f"**```{discord_message}```**")
                    print(" SUCCESS: Discord Nachricht wurde bearbeitet")
                except:
                    try:
                        overview_discord = await channel.send(f"**```{discord_message}```**")
                        f = open("discord.txt", "w")
                        f.writelines(str(overview_discord.id))
                        f.close()
                        print(" SUCCESS: Discord Nachricht wurde gesendet")
                    except:
                        print("   ERROR: Discord Nachricht konnte nicht gesendet werden")

            # telegram
            if config.telegram == True:
                try:
                    if config.telegram == True:
                        bot.edit_message_text(send_message,chat_id=config.chat_id, message_id=overview_id, parse_mode='HTML',disable_web_page_preview=True)
                        print(" SUCCESS: Telegram Nachricht wurde bearbeitet")
                except:
                    try:
                        if config.telegram == True:
                            #unpinned = requests.get('https://api.telegram.org/bot' + token + '/unpinChatMessage?chat_id=' + str(chat_id) + '&message_id=' + str(overview_id))
                            bot.delete_message(config.chat_id,overview_id)
                            overview_id = bot.send_message(config.chat_id,send_message,parse_mode='HTML')
                            overview_id = overview_id.message_id

                            f = open("telegram.txt", "w")
                            f.writelines(str(overview_id))
                            f.close()

                            if config.pinned_message == True:
                                requests.get('https://api.telegram.org/bot' + config.token + '/pinChatMessage?chat_id=' + str(config.chat_id) + '&message_id=' + str(overview_id))
                                bot.delete_message(config.chat_id,overview_id+1)
                            print(" SUCCESS: Telegram Nachricht wurde erneut gesendet")
                    except:
                        try:
                            if config.telegram == True:
                                overview_id = bot.send_message(config.chat_id,send_message,parse_mode='HTML')
                                overview_id = overview_id.message_id

                                f = open("telegram.txt", "w")
                                f.writelines(str(overview_id))
                                f.close()

                                if config.pinned_message == True:
                                    requests.get('https://api.telegram.org/bot' + config.token + '/pinChatMessage?chat_id=' + str(config.chat_id) + '&message_id=' + str(overview_id))
                                    bot.delete_message(config.chat_id,overview_id+1)
                                print(" SUCCESS: Telegram Nachricht wurde gesendet")
                        except:
                            print("   ERROR: Telegram Nachricht konnte nicht gesendet werden")

            old_message = message
        await asyncio.sleep(config.sleeptime)

@client.event
async def on_ready():
    print('    INFO: Logged in discord as ' + str(client.user.name))
    print('    INFO: ----------------------------')
    client.loop.create_task(my_background_task())

client.run(config.d_token)