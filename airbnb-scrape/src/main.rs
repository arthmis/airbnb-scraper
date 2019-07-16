#![recursion_limit = "128"]
use fantoccini::error::CmdError;
use fantoccini::{Client, Locator, Form};
use futures::future::Future;
use scraper::{Html, Selector};
// use std::process::Command;
use std::time::{Duration, Instant};
use std::fs;
use tokio;
use tokio::timer::Delay;
use serde_json::json;
// for unescaping html
use htmlescape::decode_html;

enum Date {
    Begin,
    End,
}

fn main() {
    // let mut geckodriver = Command::new("geckodriver")
    //     .spawn()
    //     .expect("geckodriver failed to start");
    let client = Client::new("http://localhost:4444");
    let location = "San Francisco, CA";

    let start_date_aria_label = create_aria_label(22, "July", 2019, "Monday", Date::Begin);
    let end_date_aria_label = create_aria_label(26, "July", 2019, "Friday", Date::End);
    let price_button_xpath = r#"//button[@class="_1i67wnzj" and @aria-haspopup="true" and @aria-expanded="false" and @aria-controls="menuItemComponent-price_range"]"#;
    let price_apply_button = r#"//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]"#;

    let scrape_airbnb = client
        .map_err(|error| unimplemented!("failed to connect to WebDriver: {:?}", error))
        .and_then(|client| client.goto("https://www.airbnb.com"))
        .and_then(|client| delay_client(client, 5000))
        .and_then(|mut client| client.form(Locator::Id("MagicCarpetSearchBar")))
        .and_then(move |mut form| {
            form.set(
                Locator::Id("Koan-magic-carpet-koan-search-bar__input"),
                location,
            )
        })
        .and_then(|form| form.submit_sneaky("type", "submit"))
        .and_then(|client| delay_client(client, 4000))
        .and_then(|client| {
            client.wait_for_find(Locator::XPath(
                r#"//button[@aria-controls="menuItemComponent-date_picker"]"#,
            ))
        })
        .and_then(|element| element.click())
        .and_then(|client| delay_client(client, 2000))
        .and_then(move |client| client.wait_for_find(Locator::XPath(&start_date_aria_label)))
        .and_then(|element| element.click())
        .and_then(|client| delay_client(client, 2000))
        .and_then(move |client| client.wait_for_find(Locator::XPath(&end_date_aria_label)))
        .and_then(|element| element.click())
        .and_then(|mut client| {
            client.find(Locator::XPath(
                r#"//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]"#,
            ))
        })
        .and_then(|element| element.click())
        .and_then(|client| delay_client(client, 2000))
        .and_then(|client| client.wait_for_find(Locator::XPath(r#"//img[@alt="Entire homes"]"#)))
        .and_then(|element| element.click())
        .and_then(move |client| {
            delay_client(client, 4000)
                .and_then(move |client| client.wait_for_find(Locator::XPath(price_button_xpath.clone())))
                .and_then(|element| element.click())
        })
        .and_then(|client| {
            delay_client(client, 1500)
                .and_then(|mut client| {
                    client.form(Locator::Id("price_filter_min"))
                        .and_then(|mut form| form.set(Locator::Id("price_filter_min"), "100"))
                        .and_then(|mut form| form.set(Locator::Id("price_filter_max"), "160"))
                        .and_then(|form| Ok(form.client()))
                })
        })
        .and_then(move |client| {
            delay_client(client, 1500)
                .and_then(move |mut client| {
                    client.find(Locator::XPath(price_apply_button))
                })
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
                    vec![json!(null)]           
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
    let page_source: String = fs::read_to_string("temp.html").unwrap();
    // let page_source: String = fs::read_to_string("something.html").unwrap();
    let document = Html::parse_fragment(&page_source);
    let title_selector = Selector::parse(r#"div._1dss1omb"#).expect("couldn't find that selector?");
    let home_url_selector = Selector::parse(r#"a[data-check-info-section="true"]._1ol0z3h"#).expect("couldn't create <a> selector");
    // let superhost_selector = Selector::parse(r#"span._j2qalb2"#).expect("couldn't create superhost selector");
    let mut home_links: Vec<String> = Vec::new();
    let mut home_titles: Vec<String> = Vec::new();

    for element in document.select(&title_selector) {
	home_titles.push(decode_html(&element.inner_html()).unwrap());
    }

    for url in document.select(&home_url_selector) {
	println!("https://www.airbnb.com{}", url.value().attr("href").unwrap().to_string());
	home_links.push(format!("https://www.airbnb.com{}", url.value().attr("href").expect("link").to_string()));
	
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
        .and_then(|client| {
            delay_client(client, 1500)
                .and_then(|mut client| {
                    client.form(Locator::Id("price_filter_min"))
                        .and_then(|mut form| {
                            form.set(Locator::Id("price_filter_min"), "");
                            // Ok(form.client())
                            form.client().
                                // .and_then(|mut client| {
                                    find(Locator::Id("price_filter_min"))
                                        .and_then(|mut element|  {
                                            element.send_keys("");
                                            Ok(client)
                                        })
                                // })
                        })
                        // .and_then(|form| delay_form(form, 2000))
                        // .and_then(|mut form| form.set(Locator::Id("price_filter_max"), ""))
                        // .and_then(|form| Ok(form.client()))
                        .and_then(|mut client| {
                            client.find(Locator::Id("price_filter_min"))
                                .and_then(|mut element|  {
                                    element.send_keys("");
                                    Ok(client)
                                })
                        })
                })
        })
        .and_then(move |client| {
            delay_client(client, 1500)
                .and_then(move |mut client| {
                    client.find(Locator::XPath(price_apply_button))
                        .and_then(|element| element.click())
                    // client.find(Locator::XPath(price_apply_span))
                })
                // .and_then(|element| element.click())
        })
        .and_then(|client| delay_client(client, 7000))
        .map(|_| ())
        .map_err(|error| panic!("webdriver command error: {}", error));

    // tokio::run(apply_price);
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
