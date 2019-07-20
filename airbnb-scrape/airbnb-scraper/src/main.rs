#![recursion_limit = "128"]
use fantoccini::error::CmdError;
use fantoccini::{Client, Form, Locator};
use futures::future::Future;
use scraper::{ElementRef, Html, Selector};
// use std::process::Command;
use serde_json::json;
use std::fs;
use std::time::{Duration, Instant};
use tokio;
use tokio::timer::Delay;
// for unescaping html
use htmlescape::decode_html;
// use std::fmt;

extern crate diesel;
use diesel::prelude::*;
use diesel::sqlite::SqliteConnection;
// use diesel::Queryable;
// use dotenv::dotenv;

use database;
use database::*;

// use std::env;

enum Date {
    Begin,
    End,
}

// struct HomeListings {
//     home_urls: Vec<String>,
//     home_titles: Vec<String>,
//     is_superhost: Vec<bool>,
// }
//
// struct Listing<'a> {
//     pub home_title: &'a str,
//     pub home_url: &'a str,
//     pub superhost: bool,
// }
//
// #[derive(Debug, Queryable)]
// struct HomeListing {
//     pub id: i32,
//     pub home_title: String,
//     pub home_url: String,
//     pub superhost: bool,
// }
//
// impl fmt::Display for HomeListing {
//     fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
//         write!(
//             f,
//             "Title: {}\nUrl: {}\nSuperhost: {}",
//             self.home_title, self.home_url, self.superhost
//         )
//     }
// }

fn main() {
    // let mut geckodriver = Command::new("geckodriver")
    //     .spawn()
    //     .expect("geckodriver failed to start");
    let client = Client::new("http://localhost:4444");
    let location = "San Francisco, CA";

    let start_date_aria_label = create_aria_label(22, "July", 2019, "Monday", Date::Begin);
    let end_date_aria_label = create_aria_label(26, "July", 2019, "Friday", Date::End);
    let price_button_xpath = r#"//button[@class="_1i67wnzj" and @aria-haspopup="true" and @aria-expanded="false" and @aria-controls="menuItemComponent-price_range"]"#;
    let price_apply_button =
        r#"//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]"#;
    let home_search_button =
        r#"//button[@class="_1vs0x720" and @type="submit" and @aria-busy="false"]"#;
    let type_of_place_button = r#"//button[@class="_1i67wnzj" and @type="button" and @aria-controls="menuItemComponent-room_type"]"#;
    let stays_button = r#"//a[@class="_10l4eyf" and @aria-busy="false" and @data-veloute="explore-nav-card:/homes"]"#;
    let entire_home_checkbox_id =
        "DynamicFilterCheckboxItem-Type_of_place-room_types-Entire_home/apt";
    let save_type_of_place_button =
        r#"//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]"#;

    let scrape_airbnb = client
        .map_err(|error| unimplemented!("failed to connect to WebDriver: {:?}", error))
        .and_then(|client| client.goto("https://www.airbnb.com"))
        // search for location in location search bar and selects first option
        .and_then(move |client| {
            delay_client(client, 5000)
                .and_then(|mut client| {
                    client.find(Locator::Id("Koan-magic-carpet-koan-search-bar__input"))
                })
                .and_then(move |mut element| {
                    element.send_keys(location);
                    Ok(element.client())
                })
                // clicks on first result
                .and_then(|client| {
                    delay_client(client, 3000)
                        .and_then(|mut client| {
                            client.find(Locator::Id("Koan-magic-carpet-koan-search-bar__option-0"))
                        })
                        .and_then(|element| element.click())
                })
        })
        // .and_then(|form| form.submit_sneaky("type", "submit"))
        // .and_then(|client| delay_client(client, 4000))
        // .and_then(|client| {
        //     client.wait_for_find(Locator::XPath(
        //         r#"//button[@aria-controls="menuItemComponent-date_picker"]"#,
        //     ))
        // })
        // .and_then(|element| element.click())
        // .and_then(|client| delay_client(client, 2000))
        // pick beginning date
        .and_then(move |client| client.wait_for_find(Locator::XPath(&start_date_aria_label)))
        .and_then(|element| element.click())
        .and_then(|client| delay_client(client, 2000))
        // pick end date
        .and_then(move |client| client.wait_for_find(Locator::XPath(&end_date_aria_label)))
        .and_then(|element| element.click())
        // .and_then(|mut client| {
        //     client.find(Locator::XPath(
        //         r#"//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]"#,
        //     ))
        // })
        // look for the submit button which has the text value of "Search"
        .and_then(move |client| {
            delay_client(client, 3000)
                .and_then(move |mut client| client.find(Locator::XPath(home_search_button)))
        })
        .and_then(|element| element.click())
        .and_then(|client| delay_client(client, 2000))
        .and_then(move |mut client| {
            client
                .find(Locator::XPath(r#"//img[@alt="Entire homes"]"#))
                // clicks on stays when "entire home button isn't found" and selects entire homes from
                // results page and resumes normal function after that
                .or_else(move |error| {
                    dbg!(error);
                    client
                        .find(Locator::XPath(stays_button))
                        .and_then(|element| element.click())
                        .and_then(move |client| {
                            delay_client(client, 3000)
                                .and_then(move |mut client| {
                                    client.find(Locator::XPath(type_of_place_button))
                                })
                                .and_then(|element| element.click())
                                .and_then(move |client| {
                                    delay_client(client, 3000)
                                        .and_then(move |mut client| {
                                            client.find(Locator::Id(entire_home_checkbox_id))
                                        })
                                        .and_then(|element| element.click())
                                        .and_then(move |client| {
                                            delay_client(client, 3000).and_then(move |mut client| {
                                                client
                                                    .find(Locator::XPath(save_type_of_place_button))
                                            })
                                        })
                                })
                        })
                })
        })
        .and_then(|element| element.click())
        .and_then(move |client| {
            delay_client(client, 4000)
                .and_then(move |client| {
                    client.wait_for_find(Locator::XPath(price_button_xpath.clone()))
                })
                .and_then(|element| element.click())
        })
        .and_then(|client| {
            delay_client(client, 1500).and_then(|mut client| {
                client
                    .find(Locator::Id("price_filter_min"))
                    .and_then(|mut element| {
                        element.clear();
                        // element.send_keys("100");
                        element.client().find(Locator::Id("price_filter_max"))
                    })
                    .and_then(|mut element| {
                        element.clear();
                        // element.send_keys("160");
                        Ok(element.client())
                    })
                // .form(Locator::Id("price_filter_min"))
                // .and_then(|mut form| form.set(Locator::Id("price_filter_min"), "100"))
                // .and_then(|mut form| form.set(Locator::Id("price_filter_max"), "160"))
                // .and_then(|form| Ok(form.client()))
            })
        })
        .and_then(move |client| {
            delay_client(client, 1500)
                .and_then(move |mut client| client.find(Locator::XPath(price_apply_button)))
                .and_then(|element| element.click())
        })
        // .and_then(|mut client| client.persist().and_then(|_| Ok(client)))
        .and_then(|client| delay_client(client, 15_000))
        .and_then(|mut client| {
            client
                // to get the value of the html after all javascript executes
                // doesn't retrieve the doctype for some reason(need to investigate)
                .execute(
                    "return document.getElementsByTagName('html')[0].innerHTML",
                    vec![json!(null)],
                )
        })
        // .and_then(|mut client| client.source())
        .map_err(move |error| {
            // geckodriver.kill().expect("Command wasn't running");
            panic!("a WebDriver command failed: {:?}", error);
        });

    // need to use this with `runtime.block_on() to return the result of an executed future`
    // let mut runtime = tokio::runtime::Runtime::new().expect("Unable to start runtime");
    // let page_source = runtime
    //     .block_on(scrape_airbnb)
    //     .expect("could not execute scrape airbnb");

    // use serde_json::de;
    // use serde_json::Value;
    // deseralize the json into the html fragment
    // let page_source = match page_source.clone() {
    //     Value::String(value) => value,
    //     _ => "".to_string(),
    // };

    // let page_source: String = fs::read_to_string("San Francisco-Stays-Airbnb.html").unwrap();
    let page_source: String = fs::read_to_string("./airbnb-scraper/temp.html").unwrap();
    // let page_source: String = fs::read_to_string("something.html").unwrap();
    let document = Html::parse_fragment(&page_source);
    let title_selector = Selector::parse(r#"div._1dss1omb"#).expect("couldn't find that selector?");
    let home_url_selector = Selector::parse(r#"a[data-check-info-section="true"]._1ol0z3h"#)
        .expect("couldn't create <a> selector");
    // airbnb seems to use different classes for the div surrounding the Superhost span, have
    // to figure out which ones they are
    // let superhost_selector = Selector::parse(r#"span._j2qalb2 > span[aria-hidden="true"]"#).expect("not a valid selector for superhost");
    let superhost_selector =
        Selector::parse(r#"span._1plk0jz1"#).expect("not a valid selector for superhost");
    // let superhost_selector_parent = Selector::parse(r#"div._z0s1fl0 > span._1plk0jz1"#).expect("not a valid selector for superhost");
    let superhost_selector_parent =
        Selector::parse(r#"div._z0s1fl0"#).expect("not a valid selector for superhost parent");
    // let superhost_selector = Selector::parse(r#"span._j2qalb2"#).expect("couldn't create superhost selector");
    let mut home_listings: Vec<HomeListing> = Vec::new();

    for (i, element) in document.select(&title_selector).enumerate() {
        let home_listing = HomeListing {
            id: i as i32,
            title: decode_html(&element.inner_html()).unwrap(),
            url: String::new(),
            superhost: false,
        };
        home_listings.push(home_listing);
    }

    for (listing_url, home_listing) in document
        .select(&home_url_selector)
        .zip(home_listings.iter_mut())
    {
        home_listing.url = format!(
            "https://www.airbnb.com{}",
            listing_url.value().attr("href").expect("link").to_string()
        );
    }

    for (element, home_listing) in document
        .select(&superhost_selector_parent)
        .zip(home_listings.iter_mut())
    {
        // have to figure out how to get the inner html to output whether "Superhost"
        // or not; for now checking whether the second child is a div or span
        let second_child = *(&element
            .last_child()
            .expect("expected second child to be last"));
        let node = ElementRef::wrap(second_child).unwrap();
        if node.value().name() == "span" {
            home_listing.superhost = true;
        }
    }

    use database::models::*;
    use database::schema::listings::dsl::*;

    let connection = database::establish_connection();

    for listing in home_listings.iter() {
        // dbg!(listing);
        // println!("{}", listing);
        // println!();
        let new_listing = NewHomeListing {
            title: &listing.title,
            url: &listing.url,
            superhost: listing.superhost,
        };
        // database::add_listing(&connection, new_listing);
    }

    let results = listings
        .select(title)
        // figure out why <String> isn't <HomeListing>
        .load::<String>(&connection)
        .expect("Error loading listings");

    // println!("Displaying {:?} posts", results.len());
    for listing in home_listings {
        println!("{}", listing);
        println!();
    }

    let test_url = String::from("https://www.airbnb.com/rooms/14240737?location=San%20Francisco%2C%20CA&check_in=2019-07-22&check_out=2019-07-26");
    match find_listing(&connection, test_url) {
        Ok(result) => println!("title: {}\nurl : {}", result.title, result.url),
        Err(error) => match error {
            diesel::NotFound => println!("error: {}", error),
            _ => panic!("shouldn't have any other error besides NotFound"),
        },
    }

    let client = Client::new("http://localhost:4444");
    let price_apply_span = r#"//span[@data-action="save"]"#;
    let apply_price = client
        .map_err(|error| unimplemented!("failed to connect to WebDriver: {:?}", error))
        .and_then(|client| client.goto("https://www.airbnb.com/s/San-Francisco--CA--United-States/homes?refinement_paths%5B%5D=%2Fhomes&toddlers=0&search_type=filter_change&zoom=10&search_by_map=true&sw_lat=37.567223764294454&sw_lng=-122.58102479003907&ne_lat=38.10949381266281&ne_lng=-122.13470520996094&place_id=ChIJIQBpAG2ahYAR_6128GcTUEo&checkin=2019-08-15&checkout=2019-08-19&adults=2&room_types%5B%5D=Entire%20home%2Fapt&s_tag=GeEBH5Z6"))
        .and_then(move |client| {
            delay_client(client, 10_000)
                .and_then(move |client| client.wait_for_find(Locator::XPath(price_button_xpath.clone())))
                .and_then(|element| element.click())
        })
        .and_then(move |client| {
            delay_client(client, 1500).and_then(|mut client| {
                client
                    .find(Locator::Id("price_filter_min"))
                    .and_then(|mut element| {
                        element.clear()
                            .and_then(|_| {
                                element.send_keys("200");
                                Ok(element)
                            })
                            .and_then(|element| element.click())
                            .and_then(|mut client| client.find(Locator::Id("price_filter_max")))
                        // element.send_keys("100");
                        // client().find(Locator::Id("price_filter_max"))
                    })
                    .and_then(|mut element| {
                        element.clear();
                        // element.send_keys("160");
                        Ok(element.client())
                    })
            })
        })
        // .and_then(|client| {
        //     delay_client(client, 1500)
        //         .and_then(|mut client| {
        //             client.form(Locator::Id("price_filter_min"))
        //                 .and_then(|mut form| {
        //                     form.set(Locator::Id("price_filter_min"), "");
        //                     // Ok(form.client())
        //                     form.client().
        //                         // .and_then(|mut client| {
        //                             find(Locator::Id("price_filter_min"))
        //                                 .and_then(|mut element|  {
        //                                     element.send_keys("");
        //                                     Ok(client)
        //                                 })
        //                         // })
        //                 })
        //                 // .and_then(|form| delay_form(form, 2000))
        //                 // .and_then(|mut form| form.set(Locator::Id("price_filter_max"), ""))
        //                 // .and_then(|form| Ok(form.client()))
        //                 .and_then(|mut client| {
        //                     client.find(Locator::Id("price_filter_min"))
        //                         .and_then(|mut element|  {
        //                             element.send_keys("");
        //                             Ok(client)
        //                         })
        //                 })
        //         })
        // })
        // .and_then(move |client| {
        //     delay_client(client, 1500)
        //         .and_then(move |mut client| {
        //             client.find(Locator::XPath(price_apply_button))
        //                 .and_then(|element| element.click())
        //             // client.find(Locator::XPath(price_apply_span))
        //         })
        //         // .and_then(|element| element.click())
        // })
        .and_then(|client| delay_client(client, 7000))
        .map(|_| ())
        .map_err(|error| panic!("webdriver command error: {}", error));

    tokio::run(apply_price);
}

fn create_aria_label(day: u8, month: &str, year: u16, day_name: &str, date: Date) -> String {
    let date = match date {
        Date::Begin => "start",
        Date::End => "end",
    };
    format!(
        r#"//td[@aria-label="Choose {}, {} {}, {} as your {} date. It's available."]"#,
        day_name, month, day, year, date
    )
}

fn delay_client(client: Client, time: u64) -> impl Future<Item = Client, Error = CmdError> {
    Delay::new(Instant::now() + Duration::from_millis(time))
        .and_then(|_| Ok(client))
        .map_err(|error| panic!("delay errored; err: {:?}", error))
}

// fn delay_form(form: Form, time: u64) -> impl Future<Item = Form, Error = CmdError> {
//     Delay::new(Instant::now() + Duration::from_millis(time))
//         .and_then(|_| Ok(form))
//         .map_err(|error| panic!("delay errored; err: {:?}", error))
// }
