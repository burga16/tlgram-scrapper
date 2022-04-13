from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError

phone = +34phone_number
username = "username"
api_id = api_id
api_hash = "api_hash"



def startTelegramClient():
    client = TelegramClient(username, api_id, api_hash)
    client.start()

    checkAuth(client)
    return client


def checkAuth(client: TelegramClient):
    # Ensure you're authorized
    if not client.is_user_authorized():
        client.send_code_request(phone)
        try:
            client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            client.sign_in(password=input('Password: '))
    print("Client Created")
