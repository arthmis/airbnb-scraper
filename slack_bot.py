import slack
from slack import RTMClient
import os
import database
from dotenv import load_dotenv
# import toml
import tomlkit as toml
# from tomlkit import dumps
# from tomlkit import parse
# from tomlkit import loads

from datetime import date

load_dotenv(verbose=True)

BOT_TOKEN = os.environ['BOT_TOKEN']
slack_client = slack.WebClient(BOT_TOKEN)

def write_toml(toml_data: str, file_path: str):
    file = open(file_path, "w")
    file.write(toml_data)
    file.close()

def read_toml(toml_path: str):
    file = open(toml_path, "r")
    toml_data = toml.parse(file.read())

    file.close()
    return toml_data

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
        # else:
        #     options = ""
        #     options += "usage: @The Last Air Scraper [option]\n"
        #     options += "\nhelp/options: show this help message\n"
        #     response = slack_client.chat_postMessage(
        #         channel='#general',
        #         text=options
        #     )

@RTMClient.run_on(event="message")
def show_dates(**payload):
    data = payload['data']
    if '@ULQA3K1H8' in data['text']:
        if "show dates" in data['text']:
            # config_file = open("config.toml", "r")
            # config = toml.loads(config_file.read())
            # config_file.close()
            config = read_toml("config.toml")
            response = slack_client.chat_postMessage(
                channel="#general",
                text="The current start date is: {}\nThe current end date is: {}".format(config['start_date'], config['end_date'])
            )

@RTMClient.run_on(event="message")
def change_start_date(**payload):
    data = payload['data']
    if '@ULQA3K1H8' in data['text']:
        if "change start date" in data['text']:
            config = read_toml("config.toml")
            new_start_date = data['text'].split(' ')[4]
            try:
                new_date = date.fromisoformat(new_start_date)
                config['start_date'] = new_start_date
                new_config = toml.dumps(config)
                write_toml(new_config, "config.toml")
                response = slack_client.chat_postMessage(
                    channel="#general",
                    text="Date changed to {}".format(new_start_date)
                )
            except ValueError as error:
                response = slack_client.chat_postMessage(
                    channel="#general",
                    text="{}\nFormat should be yyyy-mm-dd.".format(error)
                )

@RTMClient.run_on(event="message")
def change_end_date(**payload):
    data = payload['data']
    if '@ULQA3K1H8' in data['text']:
        if "change end date" in data['text']:
            config = read_toml("config.toml")
            new_end_date = data['text'].split(' ')[4]
            try:
                new_date = date.fromisoformat(new_end_date)
                config['end_date'] = new_end_date
                new_config = toml.dumps(config)
                write_toml(new_config, "config.toml")
                response = slack_client.chat_postMessage(
                    channel="#general",
                    text="Date changed to {}".format(new_end_date)
                )
            except ValueError as error:
                response = slack_client.chat_postMessage(
                    channel="#general",
                    text="{}\nFormat should be yyyy-mm-dd.".format(error)
                )

@RTMClient.run_on(event="message")
def help_prompt(**payload):
    data = payload['data']
    if '@ULQA3K1H8' in data['text']:
        if 'help' in data['text']:
            options = ""
            options += "usage: @The Last Air Scraper [option]\n"
            options += "\nhelp/options: Show this help message.\n"
            options += "\nshow dates: Show the current start and end date.\n"
            options += "\nchange start date: Changes start date.\n"
            options += "\nchange end date: Changes end date.\n"
            response = slack_client.chat_postMessage(
                channel='#general',
                text=options
            )

rtm_client = RTMClient(token=BOT_TOKEN)
rtm_client.start()
