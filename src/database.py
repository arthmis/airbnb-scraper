import sqlite3
from sqlite3 import Error


def create_connection(database):
    try:
        connection = sqlite3.connect(database)
        print("Connection successful...\nUsing sqlite version: {}".format(sqlite3.version))
        return connection
    except Error as error:
        print(error)

    return None


def create_table(connection, sql_statement):
    try:
        cursor = connection.cursor()
        cursor.execute(sql_statement)
        print("Completed creating table")
    except Error as error:
        print("create table error: {}".format(error))


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
        cursor.execute(statement, (listing.title, listing.url, listing.superhost, listing.image_url))
        connection.commit()
        return cursor.lastrowid
    else:
        return duplicate[0]

# currently not relevant, will probably delete later
def find_listing_by_title(connection, title):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM listings WHERE title=?', (title,))
    listing = cursor.fetchone()
    if listing is None:
        return None
    else:
        return listing


def find_listing_by_url(connection, url):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM listings WHERE url=?", (url,))
    listing = cursor.fetchone()
    if listing is None:
        return None
    else:
        return listing


def find_all_listings(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM listings LIMIT 10")
    listings = cursor.fetchall()
    if len(listings) == 0:
        return None
    else:
        return listings


create_table_sql = """
CREATE TABLE IF NOT EXISTS listings (
    id integer PRIMARY KEY,
    title text NOT NULL,
    url text NOT NULL,
    superhost boolean NOT NULL DEFAULT 'f',
    image_url text NOT NULL
)
"""

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
    # create_table(connection, create_table_sql)
    # for listing in listings:
    #     add_listing(connection, listing)

    # connection.close()
