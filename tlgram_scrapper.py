import sys
import requests
import json
import db_sqlalchemy
from datetime import datetime


def getChannelsFromTgstat(wordToSearch):
    # url de tgstat
    url = 'https://tgstat.com/channels/list'

    post_data = {'period': 'current_year', 'country': 'global', 'language': 'global', 'verified': 0,
                 'search': str(wordToSearch)}

    resp = requests.post(url, data=post_data)
    print(resp.text)
    groups_list = []

    if resp.status_code == 200:
        obj = json.loads(resp.text)
        for group_element in obj['items']['list']:
            if group_element['channelIdCode']:
                groups_list.append(group_element['channelIdCode'].replace('@', ''))

        print(groups_list)

    else:
        print('Error en la llamada a tgstat')

    return groups_list


def storeGroupsFromTgstat(wordToSearch):
    aux = getChannelsFromTgstat(wordToSearch)
    for group_name in aux:
        db_sqlalchemy.addGroupToImport(group_name, "id_group")


def main():
    if len(sys.argv) != 2:
        print("Error. Usage: tlgram_scrapper.py wordToSearch")
    else:
        now = datetime.now()
        print("Start: " + str(now.strftime("%d/%m/%Y %H:%M:%S")))
        storeGroupsFromTgstat(sys.argv[1])

        now = datetime.now()
        print("End: " + str(now.strftime("%d/%m/%Y %H:%M:%S")))


main()
