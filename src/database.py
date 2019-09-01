import sqlite3
from sqlite3 import Error
from sqlite3 import DatabaseError
from sqlite3 import OperationalError
from sqlite3 import ProgrammingError
import traceback
import logging

# formatter = logging.Formatter("%(levelname)s - %(asctime)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# console_handler = logging.StreamHandler()
# console_handler.setFormatter(formatter)
# logger.addHandler(console_handler)

MAX_ROWS = 15

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
    sql = """
    CREATE TABLE IF NOT EXISTS listings (
        id integer PRIMARY KEY,
        title text NOT NULL,
        url text NOT NULL,
        image_url text NOT NULL,
        home_type text NOT NULL,
        price integer NOT NULL,
        review_count integer NOT NULL,
        rating real NOT NULL,
        weighted_rating real NOT NULL
    )
    """
    try:
        cursor.execute(sql)
        logger.info(f"Completed creating table: listings")
    except OperationalError:
        logger.exception("Syntax error with create table sql:", exc_info=True)


def delete_row(conn, id):
    statement = "DELETE FROM listings WHERE id=?"
    cursor = conn.cursor()
    try:
        cursor.execute(statement, (id,))
    except Error:
        logger.exception(f"Failed to delete row with id: {id}", exc_info=True)
        raise
    else:
        logger.debug(f"Deleted row with id: {id}")
        return id

# will add listing if it isn't there otherwise
# returns the rowid of the listing if its a duplicate
def add_listing(connection, listing):
    statement = """
        INSERT INTO listings (title, url, image_url, home_type, price, review_count, rating, weighted_rating)
        VALUES(?,?,?,?,?,?,?,?)
    """
    duplicate = find_listing_by_url(connection, listing.url)
    if duplicate is None:
        cursor = connection.cursor()
    num_rows = cursor.execute("SELECT Count(*) FROM listings").fetchone()[0] 
    if num_rows < MAX_ROWS:
        if duplicate is None:
        try:
            cursor.execute(
                statement,
                    (listing.title, listing.url, listing.image_url, listing.home_type, listing.price, listing.review_count, listing.rating, listing.weighted_rating),
            )
            except Error:
            logger.exception(
                    f"Failed to add listing to database with error: ", exc_info=True
            )
            raise
        else:
            logger.info(f"Added listing with rowid: {cursor.lastrowid}")
            connection.commit()
            logger.info("Committed listing to db.")
        return cursor.lastrowid
    else:
        return duplicate[0]
    elif num_rows == MAX_ROWS:
        lowest_weighted_rating_row = find_lowest_weight_rated(connection)
        lowest_weighted_rating = lowest_weighted_rating_row[8]
        id = lowest_weighted_rating_row[0]
        if lowest_weighted_rating < listing.weighted_rating:
            try:
                delete_row(connection, id)
            except Error:
                raise
            else:
                return add_listing(connection, listing)



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

def find_lowest_weight_rated(connection):
    cursor = connection.cursor()
    find_min_weight_rated = """
        SELECT 
            * 
        FROM 
            listings 
        WHERE 
            weighted_rating = (
                SELECT 
                    min(weighted_rating) 
                FROM 
                    listings
            )
    """
    try:
        cursor.execute(find_min_weight_rated)
    except Error:
        logger.exception("", exc_info=True)
        raise
    else:
        listing = cursor.fetchone()
        return listing


def find_all_listings(connection, limit=5):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM listings LIMIT ?", (limit,))
    except Error:
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
