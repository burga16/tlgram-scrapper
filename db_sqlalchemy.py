import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

#engine = sqlalchemy.create_engine(
#    "mariadb+mariadbconnector://username:password@127.0.0.1:port/database_name", pool_pre_ping=True,
#    pool_recycle=1500)

engine = sqlalchemy.create_engine(
    "mariadb+mariadbconnector://tlgram-scrapper:tlgram-scrapper@127.0.0.1/tlgram-scrapper", pool_pre_ping=True,
    pool_recycle=1500)
	
Base = declarative_base()


class Group(Base):
    __tablename__ = 'groups'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    group_id = sqlalchemy.Column(sqlalchemy.String(length=255))
    group_name = sqlalchemy.Column(sqlalchemy.String(length=255))
    group_description = sqlalchemy.Column(sqlalchemy.String(length=255))
    classification1to10 = sqlalchemy.Column(sqlalchemy.Integer)
    json_info = sqlalchemy.Column(sqlalchemy.String(length=5000))
    private_link = sqlalchemy.Column(sqlalchemy.String(length=255))


class Message(Base):
    __tablename__ = 'messages'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    id_message = sqlalchemy.Column(sqlalchemy.String(length=255))
    id_group = sqlalchemy.Column(sqlalchemy.String(length=255))
    group_name = sqlalchemy.Column(sqlalchemy.String(length=255))
    original_msg = sqlalchemy.Column(sqlalchemy.String(length=5000))
    english_msg = sqlalchemy.Column(sqlalchemy.String(length=5000))
    id_sender = sqlalchemy.Column(sqlalchemy.String(length=255))
    sender_username = sqlalchemy.Column(sqlalchemy.String(length=255))
    date = sqlalchemy.Column(sqlalchemy.String(length=255))
    import_date = sqlalchemy.Column(sqlalchemy.String(length=255))
    json_info = sqlalchemy.Column(sqlalchemy.String(length=4294967295))


class GroupToImport(Base):
    __tablename__ = 'groups_to_import'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    group_name = sqlalchemy.Column(sqlalchemy.String(length=255))
    group_id = sqlalchemy.Column(sqlalchemy.String(length=255))
    date = sqlalchemy.Column(sqlalchemy.String(length=255))
    group_url = sqlalchemy.Column(sqlalchemy.String(length=255))
    imported = sqlalchemy.Column(sqlalchemy.Integer)
    date_imported = sqlalchemy.Column(sqlalchemy.String(length=255))


class PrivateLinks(Base):
    __tablename__ = 'private_links'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    link = sqlalchemy.Column(sqlalchemy.String(length=255))
    date = sqlalchemy.Column(sqlalchemy.String(length=255))


Base.metadata.create_all(engine)

# Create a session
Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)
session = Session()


def addGroup(group_name, group_description, group_id, json_info="", private_link=""):
    newGroup = Group(group_id=group_id, group_name=group_name, group_description=group_description, json_info=json_info,
                     private_link=private_link)
    session.add(newGroup)
    session.commit()


def addGroupToImport(group_name, group_id, group_url="", imported=0, date_imported=""):
    newGroupToImport = GroupToImport(group_name=group_name, group_id=group_id,
                                     date=datetime.now().strftime("%d/%m/%Y %H:%M:%S"), group_url=group_url,
                                     imported=imported, date_imported=date_imported)
    session.add(newGroupToImport)
    session.commit()


def addPrivateLink(link):
    newPrivateLink = PrivateLinks(link=link, date=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    session.add(newPrivateLink)
    session.commit()


def selectAllGroups():
    groups = session.query(Group).all()
    # for group in groups:
    # print(" - " + group.group_name + ' ' + group.group_description)
    return groups


def addMessage(id_message, id_group, group_name, original_msg, english_msg, id_sender, sender_username, date,
               import_date, json_info):
    newMessage = Message(id_message=id_message, id_group=id_group, group_name=group_name, original_msg=original_msg,
                         english_msg=english_msg, id_sender=id_sender, sender_username=sender_username, date=date,
                         import_date=import_date, json_info=json_info)
    session.add(newMessage)
    session.commit()


def selectAllGroupsToImport():
    groups_to_import = session.query(GroupToImport).filter(GroupToImport.imported == 0)
    for group in groups_to_import:
        print(" - " + group.group_id + ' ' + group.group_name)
    return groups_to_import


def markGroupAsImported(group):
    group.imported = 1
    group.date_imported = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    session.commit()


def updateGroupClassification(group, value):
    group.classification1to10 = value
    session.commit()


def selectAllMessagesFromGroup(group_id):
    messages_from_group = session.query(Message).filter(Message.id_group == group_id)
    # for message in messages_from_group:
    # print(" - " + message.id_message + ' ' + message.original_msg)
    return messages_from_group


def selectGroupFromGroupId(group_id):
    group = session.query(Group).filter_by(group_id=group_id).first()

    return group


def existGroupToImportFromGroupName(group_name):
    groupToImport = session.query(GroupToImport).filter_by(group_name=group_name).first()

    if groupToImport:
        return True
    else:
        return False


def existGroupFromGroupId(group_id):
    group = session.query(Group).filter_by(group_name=group_id).first()

    if group:
        return True
    else:
        return False


def existGroupFromPrivateUrl(group_url):
    group = session.query(Group).filter_by(private_link=group_url).first()

    if group:
        return True
    else:
        return False


def existPrivateLink(link):
    privateLink = session.query(PrivateLinks).filter_by(link=link).first()

    if privateLink:
        return True
    else:
        return False


# cuenta los links y el total de mensajes de un grupo dado el id de grupo
def countLinksAndTotalsFromMessagesByGroup(group_id):
    result = session.execute(
        "SELECT count(*) as countLinks, group_name, id_group, (SELECT count(*) FROM messages as m2 WHERE "
        "m2.group_name=m1.group_name) AS countTotal FROM messages AS m1 where original_msg like '%https://t.me/%'  "
        "and id_group = :idGroup group by group_name",
        {'idGroup': str(group_id)})

    return result


def countDaysFromFirstMsgToLastMsgByGroupId(group_id):
    result = session.execute(
        "select datediff((select date from messages where id_group = :idGroup order by `date` desc limit 1), "
        "(select date from messages where id_group = :idGroup order by `date` asc limit 1)) as days ",
        {'idGroup': str(group_id)}).first()
    print(result.days)
    return result


def main():
    countDaysFromFirstMsgToLastMsgByGroupId(1097250344)


main()
