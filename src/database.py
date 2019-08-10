import sqlite3
from sqlite3 import Error
from sqlite3 import DatabaseError
from sqlite3 import OperationalError
from sqlite3 import ProgrammingError
import traceback


def create_connection(database):
    print(f"Attempting to connect to: {database}")
    try:
        connection = sqlite3.connect(database)
        print(f"Connection successful!\nUsing sqlite version: {sqlite3.version}")
        return connection
    except DatabaseError:
        raise
    except OperationalError:
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
        print(f"Completed creating table: listings")
    except OperationalError:
        print("syntax error with create table sql")
        traceback.print_exc()

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
            traceback.print_exc()
            raise
        else:
            connection.commit()
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
        traceback.print_exc()
        raise
    else:
        listing = cursor.fetchone()

        if listing is None:
            return None
        else:
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
            return None
        else:
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
