#![recursion_limit = "128"]
use fantoccini::error::CmdError;
use fantoccini::{Client, Locator};
use futures::future::Future;
use scraper::Html;
use std::process::Command;
use std::time::{Duration, Instant};
use tokio;
use tokio::timer::Delay;

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

    let start_date_aria_label = create_aria_label(12, "July", 2019, "Friday", Date::Begin);
    let end_date_aria_label = create_aria_label(15, "July", 2019, "Monday", Date::End);
    let price_button_xpath = r#"//button[@class="_1i67wnzj" and @aria-haspopup="true" and @aria-expanded="false" and @aria-controls="menuItemComponent-price_range"]"#;
    let price_apply_button = r#"//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]"#;

    let scrape_airbnb = client
        .map_err(|error| unimplemented!("failed to connect to WebDriver: {:?}", error))
        .and_then(|client| client.goto("https://www.airbnb.com"))
        .and_then(|client| delay(client, 5000))
        .and_then(|mut client| client.form(Locator::Id("MagicCarpetSearchBar")))
        .and_then(move |mut form| {
            form.set(
                Locator::Id("Koan-magic-carpet-koan-search-bar__input"),
                location,
            )
        })
        .and_then(|form| form.submit_sneaky("type", "submit"))
        .and_then(|client| delay(client, 4000))
        .and_then(|client| {
            client.wait_for_find(Locator::XPath(
                r#"//button[@aria-controls="menuItemComponent-date_picker"]"#,
            ))
        })
        .and_then(|element| element.click())
        .and_then(|client| delay(client, 2000))
        .and_then(move |client| client.wait_for_find(Locator::XPath(&start_date_aria_label)))
        .and_then(|element| element.click())
        .and_then(|client| delay(client, 2000))
        .and_then(move |client| client.wait_for_find(Locator::XPath(&end_date_aria_label)))
        .and_then(|element| element.click())
        .and_then(|mut client| {
            client.find(Locator::XPath(
                r#"//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]"#,
            ))
        })
        .and_then(|element| element.click())
        .and_then(|client| delay(client, 2000))
        .and_then(|client| client.wait_for_find(Locator::XPath(r#"//img[@alt="Entire homes"]"#)))
        .and_then(|element| element.click())
        .and_then(move |client| {
            delay(client, 4000)
                .and_then(move |client| client.wait_for_find(Locator::XPath(price_button_xpath)))
                .and_then(|element| element.click())
        })
        .and_then(|client| {
            delay(client, 1500)
                .and_then(|mut client| {
                    client.form(Locator::Id("price_filter_min"))
                        .and_then(|mut form| form.set(Locator::Id("price_filter_min"), "100"))
                        .and_then(|mut form| form.set(Locator::Id("price_filter_max"), "160"))
                        .and_then(|form| Ok(form.client()))
                })
        })
        .and_then(move |client| {
            delay(client, 1500)
                .and_then(move |mut client| {
                    client.find(Locator::XPath(price_apply_button))
                })
                .and_then(|element| element.click())
        })
        .and_then(|mut client| client.persist().and_then(|_| Ok(client)))
        .and_then(|mut client| client.source())
        .map_err(move |error| {
            // geckodriver.kill().expect("Command wasn't running");
            panic!("a WebDriver command failed: {:?}", error);
        });

    // need to use this with `runtime.block_on() to return the result of an executed future`
    let mut runtime = tokio::runtime::Runtime::new().expect("Unable to start runtime");
    // tokio::run(scrape_airbnb);
    let page_source = runtime
        .block_on(scrape_airbnb)
        .expect("could not execute scrape airbnb");
    // geckodriver.wait().expect("Command wasn't running");
    // let document = Html::parse_document(&page_source);
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

fn delay(client: Client, time: u64) -> impl Future<Item = Client, Error = CmdError> {
    Delay::new(Instant::now() + Duration::from_millis(time))
        .and_then(|_| Ok(client))
        .map_err(|error| panic!("delay errored; err: {:?}", error))
}
