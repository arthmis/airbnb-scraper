import slack
from slack import RTMClient

# from slack import RTMClient, SlackClientError, SlackApiError
import os
import database
from dotenv import load_dotenv
import tomlkit as toml

# from tomlkit import ParseError
from datetime import date

from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    RetryError,
    before_log,
    after_log,
    retry_if_exception_type,
)

import logging

config_path = "config.toml"

load_dotenv(verbose=True)
BOT_TOKEN = os.environ["BOT_TOKEN"]
slack_client = slack.WebClient(BOT_TOKEN)

formatter = logging.Formatter("%(levelname)s - %(asctime)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


@RTMClient.run_on(event="message")
def respond_message(**payload):
    data = payload["data"]
    if "@ULQA3K1H8" in data["text"]:
        if "change location" in data["text"]:
            logger.info("Changing location...")
            change_location(data)
        elif "show dates" in data["text"]:
            logger.info("Showing dates...")
            show_dates(data)
        elif "change start date" in data["text"]:
            logger.info("Changing start date...")
            change_start_date(data)
        elif "change end date" in data["text"]:
            logger.info("Changing end date...")
            change_end_date(data)
        elif "help" in data["text"]:
            logger.info("Showing help prompt...")
            help_prompt()
        elif "listings" in data["text"]:
            logger.info("Showing top 5 listings...")
            show_listings(data)
        elif "change prices" in data["text"]:
            logger.info("Changing prices...")
            change_prices(data)
        elif "show prices" in data["text"]:
            logger.info("Showing price range...")
            show_price_range()


def show_listings(data):
    try:
        logger.debug("Attempting to connect to listings.db...")
        connection = database.create_connection("listings.db")
    except Exception as error:
        logger.exception(f"{error}", exc_info=True)
    else:
        logger.debug("Successfully connected to: listings.db.")
    listings = database.find_all_listings(connection)
    output = []
    if listings is None:
        logger.DEBUG("There were no listings found in listings.db.")
        output = output.append(
            {
                "type": "mrkdwn",
                "text": "No listings have been found. Check logs for potential errors.",
            }
        )
    else:
        for i in range(len(listings)):
            superhost_status = ""

            if listings[i][3] == 1:
                superhost_status = "Superhost"
            else:
                superhost_status = "Non Superhost"

            output.append(
                format_listing(
                    (listings[i][1], listings[i][2], superhost_status, listings[i][4])
                )
            )

    connection.close()
    response = slack_client.chat_postMessage(channel="#general", blocks=output)
    assert response["ok"]


# uses slack's block styling to format a listing
def format_listing(listing):
    url = listing[1]
    title = listing[0]
    superhost_status = listing[2]
    image_url = listing[3]

    # need alternative text whenever displaying an image or nothing will work
    # use whether listing is guesthouse, apartment, house, etc to be
    # the alternative text
    display_format = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "<{}|{}>\n\n{}".format(url, title, superhost_status),
        },
        "accessory": {
            "type": "image",
            "image_url": image_url,
            "alt_text": "alt text for image",
        },
    }

    return display_format


def show_dates(data):
    message = ""
    try:
        config = read_toml(config_path)
    except FileNotFoundError:
        message = (
            f"There was a problem. The configuration file could not be found or read."
        )
    except Exception as error:
        logger.exception("", exc_info=True)
    else:
        message = f'The current start date is: {config["start_date"]}\nThe current end date is: {config["end_date"]}'

    response = slack_client.chat_postMessage(channel="#general", text=message)
    log.debug(f"{response}")
    assert response["ok"]


def change_start_date(data):
    message = ""
    try:
        config = read_toml(config_path)
    except FileNotFoundError:
        message = f"There was a problem. The configuration file `{config_path}`, could not be found or read."
        logger.exception("", exc_info=True)
    except Exception as error:
        message = f"There was a problem with configuration file: `{config_path}`"
        logger.exception("", exc_info=True)
    else:
        new_start_date = data["text"].split(" ")[4]
        try:
            new_date = date.fromisoformat(new_start_date)
            config["start_date"] = new_start_date
            new_config = toml.dumps(config)
            write_toml(new_config, config_path)
            message = f"Date changed to {new_start_date}"
            logger.info(f"Start date changed to {new_start_date}")
        except ValueError as error:
            logger.info(f"User wrote this date as input: {new_start_date}")
            logger.info(f"User wrote this date with error: {error}")
            message = f"Format should be yyyy-mm-dd, i.e. 2019-01-03"
    response = slack_client.chat_postMessage(channel="#general", text=message)
    log.debug(f"{response}")
    assert response["ok"]


def change_end_date(data):
    message = ""
    try:
        config = read_toml(config_path)
    except FileNotFoundError:
        message = f"There was a problem. The configuration file `{config_path}`, could not be found or read."
        logger.exception("", exc_info=True)
    except Exception as error:
        message = f"There was a problem with configuration file: `{config_path}`"
        logger.exception("", exc_info=True)
    else:
        new_end_date = data["text"].split(" ")[4]
        try:
            new_date = date.fromisoformat(new_end_date)
            config["end_date"] = new_end_date
            new_config = toml.dumps(config)
            write_toml(new_config, config_path)
            message = f"Date changed to {new_end_date}"
        # need to write better error message for this(date is out of range or wrong formatting)
        except ValueError as error:
            logger.info("User inputted {new_end_date} for end date. ")
            logger.exception("", exc_info=True)
            message = "Format should be yyyy-mm-dd, i.e. 2019-02-03"
    response = slack_client.chat_postMessage(channel="#general", text=message)
    log.debug(f"{response}")
    assert response["ok"]


def change_location(data):
    try:
        config = read_toml(config_path)
    except Exception as error:
        logger.exception("", exc_info=True)
        post_config_not_found_error()
    else:
        new_location = data["text"].split("location")[1].strip()
        config["location"] = new_location
        write_toml(toml.dumps(config), config_path)
        logger.info(f"Changed location to: {new_location}")
        response = slack_client.chat_postMessage(
            channel="#general", text=f"Location changed to {new_location}"
        )
        log.debug(f"{response}")
        assert response["ok"]


def post_config_not_found_error():
    message = f"There was a problem with configuration file: `{config_path}`"
    response = slack_client.chat_postMessage(channel="#general", text=message)
    log.debug(f"{response}")
    assert response["ok"]


def change_prices(data):
    message = ""
    try:
        config = read_toml(config_path)
    except Exception as error:
        logger.exception("", exc_info=True)
        post_config_not_found_error()
    # else:
    prices = data["text"].split("prices")[1]
    # checks if user entered the right number of inputs
    try:
        new_min_price = prices.split()[0]
        new_max_price = prices.split()[1]
    except IndexError as error:
        log.info(f"While handling change prices event {error}")
        log.exception("", exc_info=True)
        response = slack_client.chat_postMessage(
            channel="#general",
            text="The usage for change prices is:\nchange prices [new minimum price] [new maximum price]",
        )
        log.debug(f"{response}")
        assert response["ok"]
        return

    try:
        new_min_price = float(new_min_price)
        new_min_price = int(new_min_price)
    except ValueError:
        log.exception("", exc_info=True)
        response = slack_client.chat_postMessage(
            channel="#general",
            text="New minimum price has to be a number: {}".format(new_min_price),
        )
        print("New minimum is not a float")
        log.debug(f"{response}")
        assert response["ok"]
        return

    try:
        new_max_price = float(new_max_price)
        new_max_price = int(new_max_price)
    except ValueError:
        log.exception("", exc_info=True)
        response = slack_client.chat_postMessage(
            channel="#general",
            text="New maximum price has to be a number: {}".format(new_max_price),
        )
        log.debug(f"{response}")
        assert response["ok"]
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
            text=f"Maximum price cannot be lower than minimum price:\ninput min: {new_min_price}\ninput max: {new_max_price}",
        )
        log.debug(f"{response}")
        assert response["ok"]
        return

    config["max_price"] = new_max_price
    config["min_price"] = new_min_price
    write_toml(toml.dumps(config), config_path)
    log.info("Changed min and max price to: ${new_min_price} ${new_max_price}")


def show_price_range():
    try:
        config = read_toml(config_path)
    except Exception as error:
        logger.exception("", exc_info=True)
        post_config_not_found_error()
    else:
        min_price = config["min_price"]
        max_price = config["max_price"]
        response = slack_client.chat_postMessage(
            channel="#general",
            text="Price range is: {}-{} dollars".format(min_price, max_price),
        )
        log.debug(f"{response}")
        assert response["ok"]


def help_prompt():
    options = ""
    options += "usage: @The Last Air Scraper [option]\n"
    options += "\nhelp/options: Show this help message.\n"
    options += "\nshow dates: Show the current start and end date.\n"
    options += "\nchange start date [yyyy-mm-dd]: Changes start date.\n"
    options += "\nchange end date [yyyy-mm-dd]: Changes end date.\n"
    options += "\nchange location [new location]: Changes search location.\n"
    options += (
        "\nchange prices [new minimum price] [new maximum price]: Changes price range\n"
    )
    options += "\nshow prices: Show price range\n"

    response = slack_client.chat_postMessage(channel="#general", text=options)
    log.debug(f"{response}")
    assert response["ok"]


def write_config(toml_data, file_path):
    try:
        file = open(file_path, "w")
    except OSError as exc:
        logger.exception(f"Error with {file_path}:", exc_info=True)
        raise
    else:
        try:
            file.write(toml_data)
        except Exception as error:
            logger.exception("", exc_info=True)
            raise
        file.close()


def read_config(toml_path):
    toml_data = {}
    try:
        file = open(toml_path, "r")
    except FileNotFoundError:
        logger.exception("Error:", exc_info=True)
        raise
    else:
        try:
            toml_data = toml.parse(file.read())
        except Exception as error:
            logger.exception("", exc_info=True)
            raise
        file.close()

    return toml_data


if __name__ == "__main__":
    logger.info("Executing slack bot...")

    rtm_client = RTMClient(token=BOT_TOKEN)
    rtm_client.start()

    # try:
    #     config = read_config(config_path)
    # except FileNotFoundError as error:
    #     pass
    # else:
    #     print(config)

    # config = read_config(config_path)
