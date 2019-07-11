use fantoccini::{Client, Locator};
use futures::future::Future;
use std::process::Command;
use tokio;

enum Date {
    Begin,
    End,
}

fn main() {
    let mut geckodriver = Command::new("geckodriver")
        .spawn()
        .expect("geckodriver failed to start");
    println!("{}", geckodriver.id());
    let client = Client::new("http://localhost:4444");
    // let location = "San Francisco, CA";

    // tokio::run(
    //     client
    //         .map_err(|error| panic!("failed to connect to WebDriver: {:?}", error))
    //         .and_then(|client| {
    //             client.goto("https://www.google.com")
    //         })
    //         .and_then(|mut client| {
    //             client.form(Locator::Id("tsf"))
    //         })
    //         .and_then(|mut form| {
    //             form.set(
    //                 Locator::XPath(r#"//input[@class="gLFyf gsfi" and @name="q" and @type="text"]"#),
    //                 "rust"
    //             )
    //         })
    //         .and_then(|mut form| {
    //             // form.submit()
    //             form.submit_direct()
    //         })
    //         .and_then(|mut client| {
    //             client.persist()
    //         })
    //         .map_err(|error| {
    //             panic!("a WebDriver command failed: {:?}", error);
    //         })
    //
    // );
    let start_date_aria_label = create_aria_label(12, "July", 2019, "Friday", Date::Begin);
    println!("{}", start_date_aria_label);
    let end_date_aria_label = create_aria_label(15, "July", 2019, "Monday", Date::End);

    tokio::run(
        client
            .map_err(|error| unimplemented!("failed to connect to WebDriver: {:?}", error))
            .and_then(|client| client.goto("https://www.airbnb.com"))
            .and_then(|mut client| client.form(Locator::Id("MagicCarpetSearchBar")))
            .and_then(|mut form| {
                form.set(
                    Locator::Id("Koan-magic-carpet-koan-search-bar__input"),
                    "San Francisco, CA",
                )
            })
            // .and_then(|form| form.client().wait_for_find(Locator::Id("checkin_input")))
            // .and_then(|element| element.click())
            // .and_then(|mut client| client.form(Locator::Id("MagicCarpetSearchBar")))
            // .and_then(|form| form.submit_direct())
            .and_then(|form| form.submit_sneaky("type", "submit"))
            // .and_then(|client| {
            //     client.wait_for_navigation(None)
            // })
            .and_then(|client| {
                client.wait_for_find(Locator::XPath(
                    r#"//button[@aria-controls="menuItemComponent-date_picker"]"#,
                ))
            })
            .and_then(|element| element.click())
            .and_then(move |client| client.wait_for_find(Locator::XPath(&start_date_aria_label)))
            .and_then(|element| element.click())
            .and_then(move |client| client.wait_for_find(Locator::XPath(&end_date_aria_label)))
            .and_then(|element| element.click())
            .and_then(|mut client| {
                client.find(Locator::XPath(
                    r#"//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]"#,
                ))
            })
            .and_then(|element| element.click())
            .and_then(|client| {
                client.wait_for_find(Locator::XPath(r#"//img[@alt="Entire homes"]"#))
            })
            .and_then(|element| element.click()) 
            .and_then(|mut client| client.persist())
            .map_err(|error| {
                panic!("a WebDriver command failed: {:?}", error);
            })
            .map(|_| ()),
    );
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
