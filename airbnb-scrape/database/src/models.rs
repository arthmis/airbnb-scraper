use super::schema::listings;
use diesel::{Insertable, Queryable};
use std::fmt;

#[derive(Insertable, Clone, Debug)]
#[table_name = "listings"]
pub struct NewHomeListing<'a> {
    pub title: &'a str,
    pub url: &'a str,
    pub superhost: bool,
}

#[derive(Queryable, Debug, Clone)]
pub struct HomeListing {
    pub id: i32,
    pub title: String,
    pub url: String,
    pub superhost: bool,
}

impl fmt::Display for HomeListing {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "Title: {}\nUrl: {}\nSuperhost: {}",
            self.title, self.url, self.superhost
        )
    }
}
