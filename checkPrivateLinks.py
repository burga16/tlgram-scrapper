from datetime import datetime
from time import sleep

import db_sqlalchemy
import re
import telegramClient
import traductor
import asyncio

from telethon.tl.functions.messages import ImportChatInviteRequest


def connectToPrivateChannelAndReturnChannelId(client, channelLink):
    # split link
    channelHash = channelLink.replace('https://t.me/joinchat/', '')
    # join channel
    updates = client(ImportChatInviteRequest(channelHash))
    print(updates)
    # get channel id:
    if len(updates.updates) != 0:
        channelId = updates.updates[1].channel_id
    else:
        channelId = updates.chats[0].id

    print(channelId)
    return channelId


def getMessagesFromPrivateChannelFromChannelId(client, channelId):
    #channelId = connectToPrivateChannelAndReturnChannelId(channelLink)

    entity = client.get_entity(channelId)

    messages = client.get_messages(entity, 1000)
    #print(messages)

    return messages


def checkTelegramPrivateLinkInMessagesFromGroupId(client, group_id, group):
    # get messages from group id
    messages = db_sqlalchemy.selectAllMessagesFromGroup(group_id)

    for message in messages:
        url = re.findall(r'https://t.me/joinchat/+\w*', message.original_msg)

        if url:
            answer = ""
            for urlItem in url:
                if urlItem:
                    # if group already exists on groupsToImport table it does not have to be added again
                    if not db_sqlalchemy.existGroupFromPrivateUrl(urlItem) and not db_sqlalchemy.existPrivateLink(urlItem):
                        while answer not in ["y", "n"]:
                            print("Nuevo enlace privado a otro canal detectado, el canal original es: " + group.group_name + " y tiene una clasificación de " + str(group.classification1to10) + "/10. El enlace del nuevo canal privado es: " + urlItem)
                            answer = input("Desea unirse al canal privado y examinar los mensajes? Y/N").lower()
                        if answer == "y":
                            print("Examinando canal...")
                            try:
                                channelID = connectToPrivateChannelAndReturnChannelId(client, urlItem)
                                print(channelID)
                                messagesFromNewGroup = getMessagesFromPrivateChannelFromChannelId(client, channelID)
                                #print(messagesFromNewGroup[0].message)
                                db_sqlalchemy.addGroup("PrivateChannel", "", channelID, private_link=urlItem)

                                for messageFromNewGroup in messagesFromNewGroup:
                                    if messageFromNewGroup.text:

                                        now = datetime.now()

                                        if messageFromNewGroup.text:
                                            try:
                                                db_sqlalchemy.addMessage(messageFromNewGroup.id,
                                                                         messageFromNewGroup.peer_id.channel_id,
                                                                         "PrivateChannel",
                                                                         messageFromNewGroup.text,
                                                                         traductor.translateMsg(messageFromNewGroup.text),
                                                                         messageFromNewGroup.get_sender().id,
                                                                         messageFromNewGroup.get_sender().username,
                                                                         messageFromNewGroup.date,
                                                                         now.strftime("%d/%m/%Y %H:%M:%S"),
                                                                         str(messageFromNewGroup))
                                            except Exception as e1:
                                                print("Error:" + str(e1))
                                # Select group and mark as imported with date
                                selectedGroup = db_sqlalchemy.selectGroupFromGroupId(channelID)
                                db_sqlalchemy.markGroupAsImported(selectedGroup)

                            except Exception as e:
                                print("Error" + str(e))

                            sleep(20)
                        else:
                            print("No se unirá al canal ni se examinarán los mensajes.")
                    # guardamos el link para no repetirlo
                    db_sqlalchemy.addPrivateLink(urlItem)


def main():
    now = datetime.now()
    print("Start: " + str(now.strftime("%d/%m/%Y %H:%M:%S")))

    client = telegramClient.startTelegramClient()

    for group in db_sqlalchemy.selectAllGroups():
        checkTelegramPrivateLinkInMessagesFromGroupId(client, group.group_id, group)

    now = datetime.now()
    print("End: " + str(now.strftime("%d/%m/%Y %H:%M:%S")))


asyncio.run(main())