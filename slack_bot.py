import slack
from slack import RTMClient
import os
import database
from dotenv import load_dotenv
import tomlkit as toml
from datetime import date

load_dotenv(verbose=True)

BOT_TOKEN = os.environ['BOT_TOKEN']
slack_client = slack.WebClient(BOT_TOKEN)


@RTMClient.run_on(event="message")
def respond_message(**payload):
    data = payload['data']
    if '@ULQA3K1H8' in data['text']:
        if 'change location' in data['text']:
            change_location(data)
        elif 'show dates' in data['text']:
            show_dates(data)
        elif "change start date" in data['text']:
            change_start_date(data)
        elif "change end date" in data['text']:
            change_end_date(data)
        elif 'help' in data['text']:
            help_prompt()
        elif 'listings' in data['text']:
            show_listings(data)
        # elif 'change min price' in data['text']:
        #     change_min_price(data)
        # elif 'change max price' in data['text']:
        #     change_max_price(data)
        elif 'change prices' in data['text']:
            change_prices(data)
        elif 'show prices' in data['text']:
            show_price_range()

def show_listings(data):
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

def show_dates(data):
    config = read_toml("config.toml")
    response = slack_client.chat_postMessage(
        channel="#general",
        text="The current start date is: {}\nThe current end date is: {}".format(config['start_date'], config['end_date'])
    )

def change_start_date(data):
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

def change_end_date(data):
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
    # need to write better error message for this(date is out of range or wrong formatting)
    except ValueError as error:
        response = slack_client.chat_postMessage(
            channel="#general",
            text="{}\nFormat should be yyyy-mm-dd.".format(error)
        )

def change_location(data):
    config = read_toml("config.toml")
    new_location = data['text'].split('location')[1].strip()
    config['location'] = new_location
    write_toml(toml.dumps(config), "config.toml")
    response = slack_client.chat_postMessage(
        channel="#general",
        text="Location changed to {}".format(new_location)
    )

def change_prices(data):
    config = read_toml("config.toml")
    prices = data['text'].split('prices')[1]
    # checks if user entered the right number of inputs
    try:
        new_min_price = prices.split()[0]
        new_max_price = prices.split()[1]
    except IndexError as error:
        print(error + " while handling change prices event")
        response = slack_client.chat_postMessage(
            channel="#general",
            text="The usage for change prices is:\nchange prices [new minimum price] [new maximum price]"
        )
        assert response['ok']
        return

    try:
        new_min_price = float(new_min_price)
        new_min_price = int(new_min_price)
    except ValueError:
        response = slack_client.chat_postMessage(
            channel="#general",
            text="New minimum price has to be a number: {}".format(new_min_price)
        )
        print("New minimum is not a float")
        assert response['ok']
        return

    try:
        new_max_price = float(new_max_price)
        new_max_price = int(new_max_price)
    except ValueError:
        response = slack_client.chat_postMessage(
            channel="#general",
            text="New maximum price has to be a number: {}".format(new_max_price)
        )
        print("New maximum is not a float")
        assert response['ok']
        return

    # airbnb minimum
    if new_min_price < 10:
        new_min_price = 10
    # personal preferences over what max price is allowed
    if new_max_price > 500:
        new_max_price = 500

    if new_max_price < new_min_price:
        response = slack_client.chat_postMessage(
            channel="#general",
            text="Maximum price cannot be lower than minimum price:\ninput min: {}\ninput max: {}".format(new_min_price, new_max_price)
        )
        assert response['ok']
        return

    config['max_price'] = new_max_price
    config['min_price'] = new_min_price
    write_toml(toml.dumps(config), "config.toml")

# def change_min_price(data):
#     config = read_toml("config.toml")
#     new_min_price = data['text'].split('price')[1].strip()
#     config['min_price'] = new_min_price
#     write_toml(toml.dumps(config), "config.toml")
#     response = slack_client.chat_postMessage(
#         channel="#general",
#         text="Minimum price changed to {}".format(new_min_price)
#     )

# def change_max_price(data):
#     config = read_toml("config.toml")
#     new_max_price = data['text'].split('price')[1].strip()
#     config['max_price'] = new_max_price
#     write_toml(toml.dumps(config), "config.toml")
#     response = slack_client.chat_postMessage(
#         channel="#general",
#         text="Maximum price changed to {}".format(new_max_price)
#     )
#
def show_price_range():
    config = read_toml("config.toml")
    min_price = config['min_price']
    max_price = config['max_price']
    response = slack_client.chat_postMessage(
        channel="#general",
        text="Price range is: ${} <--> ${}".format(min_price, max_price)
    )

def help_prompt():
    options = ""
    options += "usage: @The Last Air Scraper [option]\n"
    options += "\nhelp/options: Show this help message.\n"
    options += "\nshow dates: Show the current start and end date.\n"
    options += "\nchange start date [yyyy-mm-dd]: Changes start date.\n"
    options += "\nchange end date [yyyy-mm-dd]: Changes end date.\n"
    options += "\nchange location [new location]: Changes search location.\n"
    options += "\nchange prices [new minimum price] [new maximum price]: Changes price range\n"
    options += "\nshow prices: Show price range\n"

    response = slack_client.chat_postMessage(
        channel='#general',
        text=options
    )

def write_toml(toml_data: str, file_path: str):
    file = open(file_path, "w")
    file.write(toml_data)
    file.close()

def read_toml(toml_path: str):
    file = open(toml_path, "r")
    toml_data = toml.parse(file.read())

    file.close()
    return toml_data

rtm_client = RTMClient(token=BOT_TOKEN)
rtm_client.start()
