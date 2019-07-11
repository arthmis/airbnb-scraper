use fantoccini::error::CmdError;
use fantoccini::{Client, Locator};
use futures::future::Future;
use std::process::Command;
use std::time::{Duration, Instant};
use tokio;
use tokio::timer::Delay;

enum Date {
    Begin,
    End,
}

fn main() {
    let mut geckodriver = Command::new("geckodriver")
        .spawn()
        .expect("geckodriver failed to start");
    let client = Client::new("http://localhost:4444");
    let location = "San Francisco, CA";

    let start_date_aria_label = create_aria_label(12, "July", 2019, "Friday", Date::Begin);
    let end_date_aria_label = create_aria_label(15, "July", 2019, "Monday", Date::End);

    let scrape_airbnb = 
        client
            .map_err(|error| unimplemented!("failed to connect to WebDriver: {:?}", error))
            .and_then(|client| client.goto("https://www.airbnb.com"))
            .and_then(|client| delay(client, 5000))
            .and_then(|mut client| {
                client.form(Locator::Id("MagicCarpetSearchBar"))
            })
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
            .and_then(|client| {
                delay(client, 2000)
            })
            .and_then(move |client| client.wait_for_find(Locator::XPath(&start_date_aria_label)))
            .and_then(|element| element.click())
            .and_then(|client| {
                delay(client, 2000)
            })
            .and_then(move |client| client.wait_for_find(Locator::XPath(&end_date_aria_label)))
            .and_then(|element| element.click())
            .and_then(|mut client| {
                client.find(Locator::XPath(
                    r#"//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]"#,
                ))
            })
            .and_then(|element| element.click())
            .and_then(|client| {
                delay(client, 2000)
            })
            .and_then(|client| {
                client.wait_for_find(Locator::XPath(r#"//img[@alt="Entire homes"]"#))
            })
            .and_then(|element| element.click())
            .and_then(|client| {
                delay(client, 4000)
            })
            .and_then(|mut client| {
                client.source()
            })
            // .and_then(|mut client| client.persist())
            .map_err(|error| {
                panic!("a WebDriver command failed: {:?}", error);
            });

    // need to use this with `runtime.block_on() to return the result of an executed future`
    let mut runtime = tokio::runtime::Runtime::new().expect("Unable to start runtime");
    let page_source = runtime.block_on(scrape_airbnb).expect("page source not found");
    println!("source: {:?}", page_source);
    geckodriver.wait().expect("Command wasn't running");
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
