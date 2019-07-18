#[macro_use]
// have to add this to make sure diesel works correctly in 2018 edition
extern crate diesel;

use diesel::prelude::*;
use diesel::sqlite::SqliteConnection;
use dotenv::dotenv;
use std::env;

pub mod schema;
pub mod models;

use self::models::*;

pub fn establish_connection() -> SqliteConnection {
    dotenv().ok();

    let database_url = env::var("DATABASE_URL")
        .expect("DATABASE_URL must be set");
    SqliteConnection::establish(&database_url)
        .expect(&format!("Error connecting to {}", database_url))
}

pub fn add_listing(connection: &SqliteConnection, new_listing: NewHomeListing) {
    use schema::listings;

    diesel::insert_into(listings::table) 
        .values(&(new_listing.clone()))
        .execute(connection)
        .expect("Error adding new listing");
}

// TODO add update, delete and find
