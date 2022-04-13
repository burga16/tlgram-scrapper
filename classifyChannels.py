import collections
from datetime import datetime

from rake_nltk import Rake
import db_sqlalchemy


def getKeywordsFromMessageList(messageList):
    split_it = ' '.join(messageList).split()
    # Pass the split_it list to instance of Counter class.
    Counter = collections.Counter(split_it)

    words = []
    # most_common() produces k frequently encountered
    # input values and their respective counts.
    most_occur = Counter.most_common(1000)
    for object in most_occur:
        words.append(object[0])
    print(words)

    return words


def getMessageListFromIdGroup(idGroup):
    return db_sqlalchemy.selectAllMessagesFromGroup(idGroup)


def getKeywordsFromIdGroup(idGroup):
    print("GroupID: " + idGroup)
    messageList = convertMessagesObjectListToStringList(getMessageListFromIdGroup(idGroup))
    keywords = getKeywordsFromMessageList(messageList)
    # print("Keywords: " + keywords)

    return keywords


def convertMessagesObjectListToStringList(messageObjList):
    messageList = []
    for message in messageObjList:
        if message.english_msg:
            messageList.append(message.english_msg.lower())
        else:
            messageList.append(message.original_msg.lower())

    return messageList


def getKeywordsFromTxt():
    keywordsList = []
    f = open("keywords.txt", "r")
    for line in f.readlines():
        line = line.strip('\n')
        keywordsList.append(line)
    f.close()
    print(keywordsList)

    return keywordsList


def findKeywordsInGroupKeywords(groupId):
    list = getKeywordsFromIdGroup(str(groupId))
    keywordsListFromTxt = getKeywordsFromTxt()
    sum = 0

    for keyword in keywordsListFromTxt:
        print(keyword)
        # check if keyword from txt is in keywords extracted from group messages
        index = list.index(keyword) if keyword in list else -1
        print(index)
        # if keyword ins found in top 100 group messages words, add 1 to count
        if index != -1:
            sum = sum + 1

    return sum


def give1to5ToGroupWords(groupId):
    sum = findKeywordsInGroupKeywords(groupId)
    print(sum)
    # counting the total keywords in txt and sum, we give a number from 0 to 5 depending on the words found
    words_count = len(getKeywordsFromTxt())
    aux1 = sum / words_count
    result = aux1 * 5

    return result


# give a note from 1 to 3 while counting the % of links posted divided by the total messages
def give1To3ToGroupForLinkCount(groupId):
    result = db_sqlalchemy.countLinksAndTotalsFromMessagesByGroup(groupId).first()
    if result:
        per100 = (result[0] / result[3]) * 100
        oneToThree = 0
        if per100 <= 2:
            oneToThree = 0
        elif 2 < per100 <= 5:
            oneToThree = 1
        elif 5 < per100 <= 15:
            oneToThree = 2
        elif per100 > 15:
            oneToThree = 3
    else:
        oneToThree = 0

    return oneToThree


# depending on the time passed between the first msg and the last one we give from 0 to 2 points to the group
def give1To2ToGroupForLength(groupId):
    result = db_sqlalchemy.countDaysFromFirstMsgToLastMsgByGroupId(groupId)[0]
    points = 0
    if result:
        if result <= 180:
            points = 2
        elif 180 < result <= 365:
            points = 1
        elif result > 365:
            points = 0
    else:
        points = 0

    return points


def give1To10ClassificationToGroup(groupId):
    result = 0
    result = result + give1to5ToGroupWords(groupId)
    result = result + give1To3ToGroupForLinkCount(groupId)
    result = result + give1To2ToGroupForLength(groupId)

    group = db_sqlalchemy.selectGroupFromGroupId(groupId)

    print(group.group_name)
    db_sqlalchemy.updateGroupClassification(group, round(result))
    return result


def main():
    now = datetime.now()
    print("Start: " + str(now.strftime("%d/%m/%Y %H:%M:%S")))
    for group in db_sqlalchemy.selectAllGroups():
        give1To10ClassificationToGroup(group.group_id)

    now = datetime.now()
    print("End: " + str(now.strftime("%d/%m/%Y %H:%M:%S")))


main()
