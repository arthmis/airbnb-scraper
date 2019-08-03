import sqlite3
from sqlite3 import Error

def create_connection(database):
    try:
        connection = sqlite3.connect(database)
        print("Connection successful...\n{}".format(sqlite3.version))
        return connection
    except Error as error:
        print(error)

    return None

def create_table(connection, sql_statement):
    try:
        cursor = connection.cursor()
        cursor.execute(sql_statement)
    except Error as error:
        print(error)

# will add listing if it isn't there otherwise
# returns the rowid of the listing if its a duplicate
def add_listing(connection, listing):
    statement = """
        INSERT INTO listings (title, url, superhost)
        VALUES(?,?,?)
    """
    duplicate = find_listing_by_url(connection, listing.url)
    if duplicate is None:
        cursor = connection.cursor()
        cursor.execute(statement, (listing.title, listing.url, listing.superhost))
        connection.commit()
        return cursor.lastrowid
    else:
        return duplicate[0]

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
    cursor.execute('SELECT * FROM listings WHERE url=?', (url,))
    listing = cursor.fetchone()
    if listing is None:
        return None
    else:
        return listing


create_table_sql = """
CREATE TABLE IF NOT EXISTS listings (
    id integer PRIMARY KEY,
    title text NOT NULL,
    url text NOT NULL,
    superhost boolean NOT NULL DEFAULT 'f'
)
"""
