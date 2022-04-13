import db_sqlalchemy
import re
from datetime import datetime


def splitTelegramUrl(url):
    group = url.replace('https://t.me/', '')
    return group


def checkTelegramUrlInMessagesFromGroupId(group_id, group):
    # get messages from group id
    messages = db_sqlalchemy.selectAllMessagesFromGroup(group_id)

    for message in messages:
        url = re.findall(r'https://t.me/+\w*', message.original_msg)

        if url:
            answer = ""
            for urlItem in url:
                group_name = splitTelegramUrl(urlItem)

                # if group already exists on groupsToImport table it does not have to be added again
                if not db_sqlalchemy.existGroupToImportFromGroupName(group_name):
                    while answer not in ["y", "n"]:
                        print("Nuevo enlace a otro canal detectado, el canal original es: " + group.group_name + " y tiene una clasificación de " + str(group.classification1to10) + "/10. El nick del nuevo canal es: " + group_name)
                        answer = input("Desea añadir el canal para examinar? Y/N").lower()

                    if answer == "y":
                        print("Nuevo canal añadido en BBDD para examinar")
                        db_sqlalchemy.addGroupToImport(group_name, "group_id", urlItem)
                    else:
                        print("El nuevo canal encontrado no se añadirá para examinar")
            # regexp https://t.me/+\w* -->find telegram link
def main():
    now = datetime.now()
    print("Start: " + str(now.strftime("%d/%m/%Y %H:%M:%S")))

    for group in db_sqlalchemy.selectAllGroups():
        checkTelegramUrlInMessagesFromGroupId(group.group_id, group)

    now = datetime.now()
    print("End: " + str(now.strftime("%d/%m/%Y %H:%M:%S")))


main()