import sqlite3
from sqlite3 import Error
from sqlite3 import DatabaseError
from sqlite3 import OperationalError
from sqlite3 import ProgrammingError
import traceback

import logging

formatter = logging.Formatter("%(levelname)s - %(asctime)s - %(name)s - %(message)s")
logger = logging.getLogger("crawl_airbnb")
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def create_connection(database):
    logger.info(f"Attempting to connect to: {database}")
    try:
        connection = sqlite3.connect(database)
        logger.info(f"Connection successful!\nUsing sqlite version: {sqlite3.version}")
        return connection
    except DatabaseError:
        logger.exception("Database error", exc_info=True)
        raise
    except OperationalError:
        logger.exception("OperationalError", exc_info=True)
        raise

    return None


def create_table(connection):
    cursor = connection.cursor()
    sql = f"""
    CREATE TABLE IF NOT EXISTS listings (
        id integer PRIMARY KEY,
        title text NOT NULL,
        url text NOT NULL,
        superhost boolean NOT NULL DEFAULT 'f',
        image_url text NOT NULL
    )
    """
    try:
        cursor.execute(sql)
        logger.info(f"Completed creating table: listings")
    except OperationalError:
        logger.exception("Syntax error with create table sql:", exc_info=True)

# will add listing if it isn't there otherwise
# returns the rowid of the listing if its a duplicate
def add_listing(connection, listing):
    statement = """
        INSERT INTO listings (title, url, superhost, image_url)
        VALUES(?,?,?,?)
    """
    duplicate = find_listing_by_url(connection, listing.url)
    if duplicate is None:
        cursor = connection.cursor()
        try:
            cursor.execute(statement, (listing.title, listing.url, listing.superhost, listing.image_url))
        except Error as error:
            logger.exception(f"Failed to add listing to database with error: {error}.", exc_info=True)
            raise
        else:
            logger.info(f"Added listing with rowid: {cursor.lastrowid}")
            connection.commit()
            logger.info("Committed listing to db.")
        return cursor.lastrowid
    else:
        return duplicate[0]

# Urls are always unique so I can use this to ensure
# there aren't any duplicate listings
def find_listing_by_url(connection, url):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM listings WHERE url=?", (url,))
    except Error as error:
        logger.exception(f"Failed to find listing with error: {error}", exc_info=True)
        traceback.print_exc()
        raise
    else:
        listing = cursor.fetchone()

        if listing is None:
            logger.info("Url was not found.")
            return None
        else:
            logger.info("Successfully found url.")
            return listing

def find_all_listings(connection, limit=5):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM listings LIMIT ?", (limit,))
    except Error as error:
        traceback.print_exc()
        raise
    else:
        listings = cursor.fetchall()
        if len(listings) == 0:
            logger.info("Didn't find any listings.")
            return None
        else:
            logger.info(f"Found {limit} listings.")
            return listings


import scrape_page
if __name__ == "__main__":
    print("in database script")

    # html_source = open("second_type_results.html")
    #
    # listings = scrape_page.scrape(html_source.read())
    # html_source.close()
    #
    # connection = create_connection("listings.db")
    #
    # create_table(connection, "listings")
    # for listing in listings:
    #     add_listing(connection, listing)

    # connection.close()
    connection = create_connection("listings.db")
    create_table(connection)
    print(find_all_listings(connection))
    connection.close()
