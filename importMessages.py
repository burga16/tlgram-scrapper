import asyncio
import csv
import db_sqlalchemy
import traductor
import telegramClient

from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest

from datetime import datetime

# Header for csv file
header = ['message_id', 'from', 'date', 'content']


# But then we can use the client instance as usual
def getChannelMessages(client: TelegramClient, channelName):
    channel = findChannelEntity(client, channelName)
    messages = client.iter_messages(channel)

    for message in messages:
        print(message)

    return messages


def findChannelEntity(client: TelegramClient, channelTitle):
    channelID = findChannelID(client, channelTitle)
    channelEntity = client.get_entity(channelID)

    return channelEntity


def findChannelID(client: TelegramClient, channelTitle):
    for dialog in client.iter_dialogs():
        if not dialog.is_group and dialog.is_channel:
            if channelTitle == dialog.title:
                return dialog.id


def getChannelInfo(client: TelegramClient, channel_id):
    try:
        ch = client.get_entity(channel_id)
        ch_full = client(GetFullChannelRequest(channel=ch))
        # this is what you need
        print(ch_full.full_chat)
        return ch_full.full_chat
    except Exception:
        print("Error")
        return 0


def main():
    now = datetime.now()
    print("Start: " + str(now.strftime("%d/%m/%Y %H:%M:%S")))

    # Create the client and connect
    # We have to manually call "start" if we want an explicit bot token
    client = telegramClient.startTelegramClient()

    for group in db_sqlalchemy.selectAllGroupsToImport():
        print('Group: ' + group.group_name)

        # Save group in groups table
        channel_info = getChannelInfo(client, group.group_name)
        if channel_info == 0:
            continue

        db_sqlalchemy.addGroup(group.group_name, channel_info.about, channel_info.id, str(channel_info))
        messages = client.get_messages(group.group_name, 1000)

        with open('messages.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)

            # write the header
            writer.writerow(header)

            for message in messages:
                if message.text:
                    print(message)
                    try:
                        data = [message.id, message.get_sender().username, message.date, message.text]
                    except AttributeError:
                        data = [message.id, "", message.date, message.text]

                    now = datetime.now()

                    # write the data
                    writer.writerow(data)
                    print(message.id, message.text)

                    if message.text:
                        try:
                            db_sqlalchemy.addMessage(message.id, message.peer_id.channel_id, group.group_name,
                                                     message.text,
                                                     traductor.translateMsg(message.text), message.get_sender().id,
                                                     message.get_sender().username, message.date,
                                                     now.strftime("%d/%m/%Y %H:%M:%S"), str(message))
                        except Exception:
                            print("Error al guardar msg")
                            # db_sqlalchemy.addMessage(message.id, "", group.group_name, message.text,
                            #                          "", message.get_sender().id,
                            #                          message.get_sender().username, message.date,
                            #                          now.strftime("%d/%m/%Y %H:%M:%S"), str(message))
        # Mark group as imported with date
        db_sqlalchemy.markGroupAsImported(group)

    now = datetime.now()
    print("End: " + str(now.strftime("%d/%m/%Y %H:%M:%S")))

# Otherwise
# asyncio.run(main())
main()
