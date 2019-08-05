import slack
from slack import RTMClient
import os
import database
from dotenv import load_dotenv
import toml

config_file = open("config.toml", "r")
config = toml.loads(config_file.read())
config_file.close()

load_dotenv(verbose=True)

BOT_TOKEN = os.environ['BOT_TOKEN']
slack_client = slack.WebClient(BOT_TOKEN)

@RTMClient.run_on(event="message")
def listings(**payload):
    data = payload['data']
    if '@ULQA3K1H8' in data['text']:
        if 'listings' in data['text']:
            connection = database.create_connection("listings.db")
            listings = database.find_all_listings(connection)
            output = ""
            if listings is None:
                output = "No listings have been found. Check logs for potential errors."
            else:
                for listing in listings:
                    superhost_status = ""
                    if listing[3] == 1:
                        superhost_status = "Superhost"
                    else:
                        superhost_status= "Non Superhost"
                    output += '{}\n{}\n{}\n\n'.format(listing[1], listing[2], superhost_status)

            connection.close()
            response = slack_client.chat_postMessage(
                channel='#general',
                text=output
            )
            assert response["ok"]
        elif 'help' in data['text']:
            options = ""
            options += "usage: @The Last Air Scraper [option]\n"
            options += "\nhelp/options: show this help message\n"
            response = slack_client.chat_postMessage(
                channel='#general',
                text=options
            )
        else:
            options = ""
            options += "usage: @The Last Air Scraper [option]\n"
            options += "\nhelp/options: show this help message\n"
            response = slack_client.chat_postMessage(
                channel='#general',
                text=options
            )

rtm_client = RTMClient(token=BOT_TOKEN)
rtm_client.start()
