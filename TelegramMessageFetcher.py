from telethon.sync import TelegramClient
import pandas as pd
import datetime

class TelegramMessageFetcher:
    def __init__(self, api_id, api_hash):
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = TelegramClient('session_name', api_id, api_hash)

    def connect_to_telegram(self):
        self.client.connect()

        if not self.client.is_user_authorized():
            self.client.send_code_request(input('Enter your phone number (including country code): '))
            self.client.sign_in(input('Enter the code: '))

    def fetch_messages(self, username):
        messages = []

        try:
            # Fetch the chat ID of the specified contact
            chat = self.client.get_entity(username)

            # Fetch messages from the specified contact
            for message in self.client.iter_messages(chat, reverse=True):
                sender = message.sender_id
                text = message.text
                date = message.date
                messages.append({"Sender": sender, "message": text, "Date": date})

        except Exception as e:
            print(f"An error occurred: {e}")

        return messages

    def disconnect_from_telegram(self):
        self.client.disconnect()

    def save_messages_to_csv(self, messages, filename):
        df = pd.DataFrame(messages, columns=["Sender", "Text", "Date"])
        df['Date'] = pd.to_datetime(df['Date'], unit='s').dt.strftime('%Y-%m-%d %H:%M:%S')
        df.to_csv(filename, index=False)
        print(f"Messages saved to {filename}")

if __name__ == "__main__":
    API_ID = 20815381
    API_HASH = '8882005290fa97208a103d243c864f9f'

    api_id = API_ID
    api_hash = API_HASH

    # Specify the username or phone number of the contact whose messages you want to fetch
    contact_username = input('Enter the username or phone number of the contact: ')

    # Instance of the TelegramMessageFetcher class
    message_fetcher = TelegramMessageFetcher(api_id, api_hash)

    try:
        # Connect to Telegram
        message_fetcher.connect_to_telegram()

        # Fetch messages of the specified contact
        messages = message_fetcher.fetch_messages(contact_username)

        # Disconnect from Telegram
        message_fetcher.disconnect_from_telegram()

        # Save messages to CSV
        message_fetcher.save_messages_to_csv(messages, f"{contact_username}_messages.csv")

    except Exception as e:
        print(f"An error occurred: {e}")
